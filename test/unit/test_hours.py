"""
Unit tests for scripts/meta_notes/hours.py and what reads it
"""

import sys
from datetime import date
from pathlib import Path

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import checkin, conventions, hours, prime, template

REPO = Path(__file__).parent.parent.parent


# Tests for hours

def test_hours_work_is_todays_behaviour():
    h = hours.for_mode('work')
    assert (h.start, h.end, h.days) == ('08:00', '17:00', 'Monday to Friday')
    assert h.checkin_end == '17:30'


def test_hours_personal_is_7_to_21_every_day():
    h = hours.for_mode('personal')
    assert (h.start, h.end, h.days) == ('07:00', '21:00',
                                        'every day of the week')
    assert h.checkin_end == '21:00'


def test_hours_prime_text_work_unchanged():
    assert hours.prime_text('work') == (
        "Work runs 08:00 to 17:00, Monday to Friday; don't plan work after "
        "17:00.\nThe time block runs to 18:00 so the last rows can hold "
        "after-work\npersonal events. Keep them, and keep meetings and "
        "personal time the\nuser placed in the time block.")


def test_hours_prime_text_personal_has_no_work_cutoff():
    text = hours.prime_text('personal')
    assert '07:00 to 21:00, every day of the week' in text
    assert "don't plan work" not in text and '17:00' not in text


def test_hours_conventions_text_by_mode():
    assert (hours.conventions_text('work')
            == 'Workdays are Monday to Friday. Weeks start on Monday.')
    assert 'Every day of the week' in hours.conventions_text('personal')


def test_hours_prime_and_conventions_read_the_source(tmp_path):
    work = prime.run(str(tmp_path), date(2026, 10, 3), 'work')
    personal = prime.run(str(tmp_path), date(2026, 10, 3), 'personal')
    assert 'Workdays are Monday to Friday.' in work
    assert 'Every day of the week is a working day' in personal
    assert 'Monday to Friday' not in personal
    assert 'Workdays are' in conventions.run('work')
    assert 'Every day of the week' in conventions.run('personal')


def test_hours_checkin_has_no_separate_default():
    assert not hasattr(checkin, 'DEFAULT_END')


# Tests for the personal daily template

def test_hours_personal_template_runs_7am_to_9pm():
    lines = (REPO / 'templates' / 'daily-personal.md').read_text().splitlines()
    rows = [l for l in lines if l.startswith('|') and 'am |' in l or 'pm |' in l]
    assert rows[0].startswith('|  7:00am |')
    assert rows[-1].startswith('|  9:00pm |')
    assert '- start day:' in lines and '- start work:' not in lines


def test_hours_work_template_unchanged():
    lines = (REPO / 'templates' / 'daily.md').read_text().splitlines()
    assert '- start work:' in lines
    assert any(l.startswith('|  8:00am |') for l in lines)
    assert any(l.startswith('|  6:00pm |') for l in lines)


def test_hours_find_template_personal_prefers_daily_personal(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    folder = tmp_path / 'resource' / 'template'
    folder.mkdir(parents=True)
    (folder / 'daily.md').write_text('# d\n')
    path = 'plan/daily/26-Q4/2026-10-03 Sat.md'
    assert template.find_template(path, 'personal') == 'resource/template/daily.md'
    (folder / 'daily-personal.md').write_text('# p\n')
    assert template.find_template(path, 'personal') == 'resource/template/daily-personal.md'
    assert template.find_template(path, 'work') == 'resource/template/daily.md'
    assert template.find_template(path) == 'resource/template/daily.md'
