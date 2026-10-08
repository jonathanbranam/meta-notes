"""
Unit tests for scripts/meta_notes/outlook.py and the `outlook` subcommand

The network is replaced by canned JSON through outlook.fetch_json; no test
makes a live call.
"""

import json
import sys
from datetime import date
from pathlib import Path

import pytest

repo_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_dir / 'scripts'))

from meta_notes import cli, outlook

SENTINEL = "# meta-notes notes root. Created by `meta-notes init`; keep and commit it.\n"
CONFIG = SENTINEL + '\n[outlook]\nlocation = "Mason, OH"\n'
DAY = date(2026, 10, 9)

PLACE = {'name': 'Mason', 'admin1': 'Ohio', 'country_code': 'US',
         'latitude': 39.36, 'longitude': -84.31,
         'timezone': 'America/New_York'}


def hours(fn):
    return [fn(h) for h in range(24)]


# 51 at 6 AM rising to 72 at 2 PM
TEMPS = hours(lambda h: 51 + min(21, abs(h - 6) * 2.6) if h <= 14
              else 72 - (h - 14) * 2)
TEMPS[6] = 51
TEMPS[14] = 72

FORECAST = {
    'timezone': 'America/New_York',
    'daily': {
        'time': ['2026-10-09'],
        'temperature_2m_max': [72.4], 'temperature_2m_min': [51.2],
        'sunrise': ['2026-10-09T07:41'], 'sunset': ['2026-10-09T19:02'],
        'sunshine_duration': [14400.0],
        'precipitation_probability_max': [60],
        'rain_sum': [0.25], 'showers_sum': [0.05], 'snowfall_sum': [0.0],
        'wind_speed_10m_max': [12.4], 'wind_gusts_10m_max': [25.1],
        'uv_index_max': [6.6],
    },
    'hourly': {
        'temperature_2m': TEMPS,
        'precipitation_probability': hours(lambda h: 60 if 15 <= h <= 19 else 10),
        'snowfall': hours(lambda h: 0),
    },
}

ALERTS = {'features': [{'properties': {
    'event': 'Severe Thunderstorm Warning',
    'onset': '2026-10-09T12:00:00-04:00',
    'ends': '2026-10-09T18:00:00-04:00'}}]}


@pytest.fixture
def root(tmp_path, monkeypatch):
    (tmp_path / '.meta-notes').write_text(CONFIG)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def net(monkeypatch):
    """Canned network; `calls` records the URLs fetched."""
    state = {'calls': [], 'forecast': FORECAST, 'alerts': ALERTS,
             'geocode': {'results': [PLACE]}}

    def fake(url, params=None, headers=None):
        state['calls'].append(url)
        if url == outlook.GEOCODE_URL:
            return state['geocode']
        if url == outlook.FORECAST_URL:
            return state['forecast']
        assert headers and 'User-Agent' in headers
        return state['alerts']

    monkeypatch.setattr(outlook, 'fetch_json', fake)
    return state


def run(*argv):
    import io, contextlib
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = cli.main(list(argv) + ['--json'])
    return code, json.loads(out.getvalue())


# Tests for formatting

def test_outlook_hour_span_same_half_day():
    assert outlook.hour_span(15, 19) == '3-8 PM'


def test_outlook_hour_span_crosses_noon():
    assert outlook.hour_span(9, 13) == '9 AM-2 PM'


def test_outlook_hour_span_ends_at_noon():
    assert outlook.hour_span(6, 11) == '6 AM-noon'


def test_outlook_weather_line_rain():
    assert (outlook.weather_line(FORECAST['daily'], FORECAST['hourly'])
            == 'Weather: 72/51, rain 60% 3-8 PM, 0.3 in, 4h sun')


def test_outlook_weather_line_dry_has_no_rain():
    daily = {**FORECAST['daily'], 'precipitation_probability_max': [10]}
    assert outlook.weather_line(daily, FORECAST['hourly']) == 'Weather: 72/51, 4h sun'


def test_outlook_weather_line_snow_replaces_rain():
    daily = {**FORECAST['daily'], 'snowfall_sum': [2.1],
             'precipitation_probability_max': [80]}
    hourly = {**FORECAST['hourly'],
              'precipitation_probability': hours(lambda h: 80 if 6 <= h <= 11 else 0)}
    assert (outlook.weather_line(daily, hourly)
            == 'Weather: 72/51, snow 80% 6 AM-noon, 2.1 in, 4h sun')


def test_outlook_temps_line_sparkline():
    line = outlook.temps_line(FORECAST['hourly'])
    assert line.startswith('Temps: 51 ')
    assert line.endswith(' 72 (low 6 AM, high 2 PM)')
    spark = line.split(' ')[2]
    assert len(spark) == 24 and spark[6] == '▁' and spark[14] == '█'


def test_outlook_sun_line():
    assert outlook.sun_line(FORECAST['daily']) == 'Sun: 7:41 AM - 7:02 PM'


def test_outlook_moon_line_full_moon():
    assert outlook.moon_line(date(2026, 10, 26)).startswith('Moon: full moon')


def test_outlook_freeze_line_only_at_or_below_32():
    assert outlook.freeze_line(FORECAST['daily']) is None
    daily = {**FORECAST['daily'], 'temperature_2m_min': [30.2]}
    assert outlook.freeze_line(daily) == 'Freeze: low 30'


# Tests for geocoding

def test_outlook_geocode_caches_place(root, net):
    outlook.geocode(str(root), 'Mason, OH')
    net['calls'].clear()
    place = outlook.geocode(str(root), 'Mason, OH')
    assert place['name'] == 'Mason, Ohio, US' and net['calls'] == []
    assert (root / '.meta-notes-cache').is_dir()


def test_outlook_geocode_state_filters_matches(root, net):
    other = {**PLACE, 'admin1': 'Michigan', 'latitude': 1.0}
    net['geocode'] = {'results': [other, PLACE]}
    assert outlook.geocode(str(root), 'Mason, OH')['latitude'] == 39.36


def test_outlook_geocode_ambiguous_city_lists_places(root, net):
    other = {**PLACE, 'admin1': 'Michigan'}
    net['geocode'] = {'results': [PLACE, other]}
    with pytest.raises(outlook.OutlookError, match='several places.*Michigan'):
        outlook.geocode(str(root), 'Mason')


def test_outlook_geocode_zip_takes_first(root, net):
    net['geocode'] = {'results': [PLACE, {**PLACE, 'admin1': 'Michigan'}]}
    assert outlook.geocode(str(root), '45040')['name'] == 'Mason, Ohio, US'


def test_outlook_geocode_no_match(root, net):
    net['geocode'] = {}
    with pytest.raises(outlook.OutlookError, match='no place found'):
        outlook.geocode(str(root), 'Nowhere, ZZ')


# Tests for the command

def test_outlook_run_default_lines(root, net):
    lines, data = outlook.run(str(root), DAY, None)
    assert lines[0].startswith('### Outlook (as of ')
    assert lines[1:] == [
        '- Weather: 72/51, rain 60% 3-8 PM, 0.3 in, 4h sun',
        '- ' + outlook.temps_line(FORECAST['hourly']),
        '- Sun: 7:41 AM - 7:02 PM',
        '- Alert: Severe Thunderstorm Warning until 6:00 PM']
    assert data['place'] == 'Mason, Ohio, US'


def test_outlook_run_switches_turn_lines_off_and_on(root, net):
    (root / '.meta-notes').write_text(
        CONFIG + 'weather = false\ntemps = false\nalert = false\n'
        'moon = true\nwind = true\nuv = true\nfreeze = true\n')
    lines, _ = outlook.run(str(root), DAY, None)
    assert [l.split(':')[0] for l in lines[1:]] == [
        '- Sun', '- Moon', '- Wind', '- UV']
    assert '- Wind: 12 mph, gusts 25' in lines


def test_outlook_run_alert_skipped_outside_us(root, net):
    net['geocode'] = {'results': [{**PLACE, 'country_code': 'CA'}]}
    lines, _ = outlook.run(str(root), DAY, 'Toronto, CA')
    assert not any('Alert' in l for l in lines)
    assert outlook.ALERTS_URL not in net['calls']


def test_outlook_run_alert_for_other_day_left_out(root, net):
    lines, _ = outlook.run(str(root), date(2026, 10, 12), None)
    assert not any('Alert' in l for l in lines)


def test_outlook_run_only_weather(root, net):
    lines, _ = outlook.run(str(root), DAY, None, only='weather')
    assert lines == ['- Weather: 72/51, rain 60% 3-8 PM, 0.3 in, 4h sun']


def test_outlook_run_location_flag_overrides_config(root, net):
    outlook.run(str(root), DAY, '45040', only='sun')
    assert (root / '.meta-notes-cache').is_dir()
    assert '45040' in (root / outlook.CACHE_FILE).read_text()


def test_outlook_run_no_config_is_unavailable_when_lenient(root, net):
    (root / '.meta-notes').write_text(SENTINEL)
    lines, data = outlook.run(str(root), DAY, None, lenient=True)
    assert lines[0] == '### Outlook'
    assert lines[1].startswith('- Weather: unavailable (no location')
    assert net['calls'] == []


def test_outlook_run_no_network_is_unavailable_when_lenient(root, monkeypatch):
    def down(*a, **k):
        raise outlook.OutlookError('no network (offline)')
    monkeypatch.setattr(outlook, 'fetch_json', down)
    lines, _ = outlook.run(str(root), DAY, None, lenient=True)
    assert lines[1] == '- Weather: unavailable (no network (offline))'


def test_outlook_run_bad_switch_value(root, net):
    (root / '.meta-notes').write_text(CONFIG + 'moon = "yes"\n')
    with pytest.raises(outlook.OutlookError, match='moon must be true or false'):
        outlook.run(str(root), DAY, None)


# Tests for the CLI

def test_outlook_cli_prints_section(root, net, capsys):
    code = cli.main(['outlook', '--date', '2026-10-09'])
    out = capsys.readouterr().out
    assert code == 0
    assert out.startswith('### Outlook (as of ') and '- Sun: 7:41 AM' in out


def test_outlook_cli_unavailable_exits_zero(root, net):
    (root / '.meta-notes').write_text(SENTINEL)
    code, data = run('outlook')
    assert code == 0 and data['unavailable'].startswith('no location')


def test_outlook_cli_subcommand_fails_when_unavailable(root, net):
    (root / '.meta-notes').write_text(SENTINEL)
    code, data = run('outlook', 'sun')
    assert code == 1 and 'no location' in data['error']


def test_outlook_cli_sun_prints_one_line(root, net, capsys):
    cli.main(['outlook', 'sun', '--date', '2026-10-09', '--location', '45040'])
    assert capsys.readouterr().out == '- Sun: 7:41 AM - 7:02 PM\n'


def test_outlook_cli_json_has_lines(root, net):
    code, data = run('outlook', '--date', '2026-10-09')
    assert code == 0 and data['date'] == '2026-10-09'
    assert 'Sun: 7:41 AM - 7:02 PM' in data['lines']
