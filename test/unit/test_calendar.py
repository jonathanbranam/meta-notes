"""
Unit tests for scripts/meta_notes/calendar.py and the `calendar` and
`cache clear` subcommands

Test exports are written as .ics text and zipped at test time, with file
modification times set explicitly. Today is Monday 2026-09-28 in
America/New_York unless a test says otherwise.
"""

import builtins
import json
import os
import sys
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

# Add scripts directory to path to import the modules
repo_dir = Path(__file__).parent.parent.parent
scripts_dir = repo_dir / 'scripts'
sys.path.insert(0, str(scripts_dir))

import icalendar
import recurring_ical_events

from meta_notes import calendar, cli

NY = ZoneInfo('America/New_York')
TODAY = date(2026, 9, 28)
SENTINEL = "# meta-notes notes root. Created by `meta-notes init`; keep and commit it.\n"
CONFIG = SENTINEL + '\n[calendar]\nemail = "me@example.com"\ntimezone = "America/New_York"\n'

VTIMEZONE_NY = """BEGIN:VTIMEZONE
TZID:America/New_York
X-LIC-LOCATION:America/New_York
BEGIN:DAYLIGHT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
DTSTART:19700308T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
DTSTART:19701101T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
END:STANDARD
END:VTIMEZONE"""


# Helpers for building exports

def _when(name, value, tzid='America/New_York'):
    """A DTSTART/DTEND/RECURRENCE-ID line from a date or 'YYYYMMDDTHHMMSS[Z]'."""
    if isinstance(value, date):
        return f'{name};VALUE=DATE:{value:%Y%m%d}'
    if value.endswith('Z') or tzid is None:
        return f'{name}:{value}'
    return f'{name};TZID={tzid}:{value}'


def vevent(uid, start, end=None, summary='Meeting', tzid='America/New_York',
           extra=()):
    """One VEVENT; start and end are dates (all day) or local time strings."""
    lines = ['BEGIN:VEVENT', f'UID:{uid}', _when('DTSTART', start, tzid)]
    if end is not None:
        lines.append(_when('DTEND', end, tzid))
    lines.append(f'SUMMARY:{summary}')
    lines.extend(extra)
    lines.append('END:VEVENT')
    return '\n'.join(lines)


def vcalendar(events, name=None, timezones=(VTIMEZONE_NY,)):
    """A VCALENDAR with X-WR-CALNAME (when given), timezones, and events."""
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Google Inc//Google Calendar 70.9054//EN']
    if name:
        lines.append(f'X-WR-CALNAME:{name}')
    lines.append('X-WR-TIMEZONE:America/New_York')
    lines.extend(timezones)
    lines.extend(events)
    lines.append('END:VCALENDAR')
    return '\r\n'.join('\n'.join(lines).split('\n')) + '\r\n'


def set_mtime(path, day, hour=12):
    """Set a file's modification time to noon (by default) New York time."""
    ts = datetime(day.year, day.month, day.day, hour, tzinfo=NY).timestamp()
    os.utime(path, (ts, ts))


def write_ics(path, text, modified=TODAY):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    set_mtime(path, modified)
    return path


def write_zip(path, members, modified=TODAY):
    """A Google-style export zip: {member file name: calendar text}."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, text in members.items():
            zf.writestr(name, text)
    set_mtime(path, modified)
    return path


def three_calendars():
    """Members for me@example.com, Holidays in United States, and Birthdays."""
    return {
        'me@example.com.ics': vcalendar(
            [vevent('m1', '20260928T090000', '20260928T093000', 'Standup')],
            name='me@example.com'),
        'en.usa#holiday@group.v.calendar.google.com.ics': vcalendar(
            [vevent('h1', date(2026, 9, 28), date(2026, 9, 29), 'Holiday')],
            name='Holidays in United States'),
        'addressbook#contacts@group.v.calendar.google.com.ics': vcalendar(
            [vevent('b1', date(2026, 9, 28), date(2026, 9, 29), 'Sam birthday')],
            name='Birthdays'),
    }


@pytest.fixture
def root(tmp_path, monkeypatch):
    """A notes root with config and cache folders, as the current directory."""
    (tmp_path / '.meta-notes').write_text(CONFIG)
    (tmp_path / '.meta-notes-cache' / 'ics').mkdir(parents=True)
    (tmp_path / '.meta-notes-cache' / 'calendar').mkdir()
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def ics_dir(root):
    return root / '.meta-notes-cache' / 'ics'


def cal_dir(root):
    return root / '.meta-notes-cache' / 'calendar'


def set_config(root, extra):
    (root / '.meta-notes').write_text(CONFIG + extra)


def run(root, period=None, ics=None, today=TODAY, names=(), searches=()):
    return calendar.run(str(root), period, ics, today=today, names=names,
                        searches=searches)


def titles(data, day):
    """Event titles on a day (YYYY-MM-DD) in a run's JSON data."""
    for entry in data['days']:
        if entry['date'] == day:
            return [e['title'] for e in entry['events']]
    raise AssertionError(f'{day} not in agenda')


def block_imports(monkeypatch):
    """Make importing the calendar libraries fail, as without the virtualenv."""
    real = builtins.__import__

    def fake(name, *args, **kwargs):
        if name in ('icalendar', 'recurring_ical_events'):
            raise ImportError(f'No module named {name!r}')
        return real(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', fake)


def run_json(capsys, argv):
    code = cli.main(argv + ['--json'])
    captured = capsys.readouterr()
    return code, json.loads(captured.out), captured.err


# Tests for the export helpers

def test_calendar_helper_zip_lists_members(tmp_path):
    """A built zip holds one .ics per calendar."""
    path = write_zip(tmp_path / 'export.zip', three_calendars())

    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()

    assert len(names) == 3
    assert 'me@example.com.ics' in names
    assert datetime.fromtimestamp(path.stat().st_mtime, NY).date() == TODAY


# Tests for load_settings function

def test_calendar_load_settings_defaults(root):
    """An empty config gives defaults: no email, 3 stale days, all calendars."""
    (root / '.meta-notes').write_text(SENTINEL)

    settings = calendar.load_settings(str(root))

    assert settings.email is None
    assert settings.stale_days == 3
    assert settings.calendars is None


def test_calendar_load_settings_unknown_timezone(root):
    """An unknown timezone is an error naming it."""
    (root / '.meta-notes').write_text(
        SENTINEL + '[calendar]\ntimezone = "Mars/Olympus"\n')

    with pytest.raises(ValueError, match='Mars/Olympus'):
        calendar.load_settings(str(root))


def test_calendar_load_settings_invalid_toml(root):
    """Invalid TOML fails the calendar command, naming .meta-notes and the line."""
    (root / '.meta-notes').write_text('[calendar\n')

    with pytest.raises(ValueError, match=r'\.meta-notes.*line 1'):
        run(root)


@pytest.mark.parametrize('setting', ['stale_days = "3"', 'stale_days = -1',
                                     'calendars = "me"', 'email = 3'])
def test_calendar_load_settings_invalid_values(root, setting):
    """Settings of the wrong type are errors."""
    (root / '.meta-notes').write_text(f'[calendar]\n{setting}\n')

    with pytest.raises(ValueError, match=r'\[calendar\] in \.meta-notes'):
        calendar.load_settings(str(root))


# Tests for export discovery

def test_calendar_newest_export_wins(root):
    """The newest export by modification time is read, .ics or .zip."""
    write_zip(ics_dir(root) / 'a.zip', {'me.ics': vcalendar(
        [vevent('a', '20260928T090000', '20260928T100000', 'From zip')])},
        modified=date(2026, 9, 24))
    write_ics(ics_dir(root) / 'b.ics', vcalendar(
        [vevent('b', '20260928T090000', '20260928T100000', 'From ics')]),
        modified=date(2026, 9, 25))

    _, data, _ = run(root)

    assert data['source']['path'] == str(ics_dir(root) / 'b.ics')
    assert titles(data, '2026-09-28') == ['From ics']


def test_calendar_explicit_path(root, tmp_path):
    """--ics reads the given file, whatever ics/ holds."""
    write_ics(ics_dir(root) / 'b.ics', vcalendar(
        [vevent('b', '20260928T090000', '20260928T100000', 'From ics')]))
    other = write_zip(tmp_path / 'Downloads' / 'export.zip', {'me.ics': vcalendar(
        [vevent('a', '20260928T090000', '20260928T100000', 'Downloaded')])})

    _, data, _ = run(root, ics=str(other))

    assert titles(data, '2026-09-28') == ['Downloaded']


def test_calendar_explicit_path_missing(root):
    """A --ics file that doesn't exist is an error."""
    with pytest.raises(ValueError, match='not found: nope.zip'):
        run(root, ics='nope.zip')


def test_calendar_other_files_ignored(root):
    """Files that aren't .ics or .zip, and folders, aren't exports."""
    (ics_dir(root) / 'notes.txt').write_text('hi\n')
    write_ics(ics_dir(root) / 'old' / 'c.ics', vcalendar([]))

    with pytest.raises(ValueError, match='No calendar export found'):
        run(root)


def test_calendar_no_virtualenv(root, monkeypatch, capsys):
    """Without the libraries, calendar fails with init advice; tasks works."""
    write_ics(ics_dir(root) / 'b.ics', vcalendar([]))
    block_imports(monkeypatch)

    code, out, _ = run_json(capsys, ['calendar'])
    assert code == 1
    assert 'not installed in this notes root' in out['error']
    assert '`meta-notes init`' in out['error']

    code, out, _ = run_json(capsys, ['tasks'])
    assert code == 0


def test_calendar_no_virtualenv_with_venv_says_force(root, monkeypatch):
    """With a .venv lacking the libraries, the error says init --force."""
    (root / '.venv').mkdir()
    block_imports(monkeypatch)

    with pytest.raises(calendar.NotInstalled, match='init --force'):
        run(root)


# Tests for zip calendars

def test_calendar_selected_calendar(root):
    """calendars selects which zip members are loaded."""
    set_config(root, 'calendars = ["me@example.com"]\n')
    write_zip(ics_dir(root) / 'export.zip', three_calendars())

    _, data, _ = run(root)

    assert titles(data, '2026-09-28') == ['Standup']
    assert data['source']['loaded'] == ['me@example.com']
    assert len(data['source']['available']) == 3


def test_calendar_selected_by_file_stem_ignoring_case(root):
    """A calendars entry may match the member file name, in any case."""
    set_config(root, 'calendars = ["ME@EXAMPLE.COM", "addressbook#contacts@group.v.calendar.google.com"]\n')
    write_zip(ics_dir(root) / 'export.zip', three_calendars())

    _, data, _ = run(root)

    assert sorted(data['source']['loaded']) == ['Birthdays', 'me@example.com']


def test_calendar_unknown_calendar_name(root):
    """An unmatched name is an error listing the available calendars."""
    set_config(root, 'calendars = ["work"]\n')
    write_zip(ics_dir(root) / 'export.zip', three_calendars())

    with pytest.raises(ValueError) as exc:
        run(root)

    message = str(exc.value)
    assert 'work' in message
    for name in ('me@example.com', 'Holidays in United States', 'Birthdays'):
        assert name in message


def test_calendar_all_calendars(root):
    """With calendars unset, every calendar is loaded and labeled."""
    write_zip(ics_dir(root) / 'export.zip', three_calendars())

    lines, data, _ = run(root)

    assert sorted(titles(data, '2026-09-28')) == ['Holiday', 'Sam birthday', 'Standup']
    assert len(data['source']['available']) == 3
    assert len(data['source']['loaded']) == 3
    assert '09:00-09:30  Standup (me@example.com)' in lines


def test_calendar_name_from_file_stem(root):
    """A member without X-WR-CALNAME is named by its file name."""
    write_zip(ics_dir(root) / 'export.zip', {'work.ics': vcalendar(
        [vevent('w', '20260928T090000', '20260928T100000', 'Work')])})

    _, data, _ = run(root)

    assert data['source']['loaded'] == ['work']


def test_calendar_calendars_ignored_for_plain_ics(root):
    """calendars doesn't apply to a plain .ics export."""
    set_config(root, 'calendars = ["work"]\n')
    write_ics(ics_dir(root) / 'me.ics', vcalendar(
        [vevent('a', '20260928T090000', '20260928T100000', 'Mine')],
        name='me@example.com'))

    lines, data, _ = run(root)

    assert titles(data, '2026-09-28') == ['Mine']
    assert '09:00-10:00  Mine' in lines


# Tests for events in the agenda

def one_calendar(root, events, **kwargs):
    write_ics(ics_dir(root) / 'me.ics', vcalendar(events, name='me@example.com'),
              **kwargs)


def test_calendar_timezone_conversion(root):
    """An event at 10:00 Chicago shows at 11:00 New York."""
    one_calendar(root, [vevent('c', '20260928T100000', '20260928T110000',
                               'Remote', tzid='America/Chicago')])

    lines, _, _ = run(root)

    assert '11:00-12:00  Remote' in lines


def test_calendar_utc_times_converted(root):
    """UTC times are shown in the display timezone."""
    one_calendar(root, [vevent('u', '20260928T130000Z', '20260928T140000Z', 'UTC')])

    lines, _, _ = run(root)

    assert '09:00-10:00  UTC' in lines


def test_calendar_declined_meeting_hidden(root):
    """An event the user declined, as a single ATTENDEE value, is left out."""
    one_calendar(root, [
        vevent('d', '20260928T090000', '20260928T100000', 'Declined',
               extra=['ATTENDEE;PARTSTAT=DECLINED:mailto:Me@Example.com']),
        vevent('k', '20260928T110000', '20260928T120000', 'Kept'),
    ])

    _, data, warnings = run(root)

    assert titles(data, '2026-09-28') == ['Kept']
    assert not [w for w in warnings if 'email' in w]


def test_calendar_declined_among_attendees(root):
    """The user's decline is found among several attendees."""
    one_calendar(root, [vevent(
        'd', '20260928T090000', '20260928T100000', 'Declined',
        extra=['ATTENDEE;PARTSTAT=ACCEPTED:mailto:sam@example.com',
               'ATTENDEE;PARTSTAT=DECLINED:mailto:me@example.com'])])

    _, data, _ = run(root)

    assert titles(data, '2026-09-28') == []


def test_calendar_other_attendee_declined_kept(root):
    """Someone else's decline doesn't hide the event."""
    one_calendar(root, [vevent(
        'd', '20260928T090000', '20260928T100000', 'Sync',
        extra=['ATTENDEE;PARTSTAT=DECLINED:mailto:sam@example.com',
               'ATTENDEE;PARTSTAT=ACCEPTED:mailto:me@example.com'])])

    _, data, _ = run(root)

    assert titles(data, '2026-09-28') == ['Sync']


def test_calendar_email_unset(root):
    """Without email, declined events are listed with a warning."""
    (root / '.meta-notes').write_text(
        SENTINEL + '[calendar]\ntimezone = "America/New_York"\n')
    one_calendar(root, [vevent(
        'd', '20260928T090000', '20260928T100000', 'Declined',
        extra=['ATTENDEE;PARTSTAT=DECLINED:mailto:me@example.com'])])

    _, data, warnings = run(root)

    assert titles(data, '2026-09-28') == ['Declined']
    assert any('email is not set' in w for w in warnings)


def test_calendar_cancelled_event_hidden(root):
    """STATUS:CANCELLED events are left out."""
    one_calendar(root, [vevent('x', '20260928T090000', '20260928T100000',
                               'Cancelled', extra=['STATUS:CANCELLED'])])

    _, data, _ = run(root)

    assert titles(data, '2026-09-28') == []


WEEKLY_TUESDAY = vevent('weekly', '20260908T100000', '20260908T110000',
                        'Weekly', extra=['RRULE:FREQ=WEEKLY;BYDAY=TU'])


def test_calendar_cancelled_override(root):
    """A cancelled occurrence of a series is left out; others remain."""
    one_calendar(root, [WEEKLY_TUESDAY, vevent(
        'weekly', '20260929T100000', '20260929T110000', 'Weekly',
        extra=['RECURRENCE-ID;TZID=America/New_York:20260929T100000',
               'STATUS:CANCELLED'])])

    _, data, _ = run(root, '2026-09-28..2026-10-06')

    assert titles(data, '2026-09-29') == []
    assert titles(data, '2026-10-06') == ['Weekly']


def test_calendar_moved_occurrence(root):
    """An occurrence moved from Tuesday to Wednesday shows on Wednesday only."""
    one_calendar(root, [WEEKLY_TUESDAY, vevent(
        'weekly', '20260930T140000', '20260930T150000', 'Weekly',
        extra=['RECURRENCE-ID;TZID=America/New_York:20260929T100000',
               'SEQUENCE:1'])])

    lines, data, _ = run(root, '2026-09-28..2026-10-02')

    assert titles(data, '2026-09-29') == []
    assert titles(data, '2026-09-30') == ['Weekly']
    assert '14:00-15:00  Weekly' in lines


def test_calendar_series_split_at_edit(root):
    """A series split at an edit shows its meeting once on the handoff day."""
    one_calendar(root, [
        vevent('split', '20260903T100000', '20260903T110000', 'Forum',
               extra=['RRULE:FREQ=WEEKLY;UNTIL=20260924T035959Z']),
        vevent('split_R20260924T140000', '20260924T100000', '20260924T110000',
               'Forum', extra=['RRULE:FREQ=WEEKLY']),
    ])

    _, data, _ = run(root, '2026-09-17..2026-10-01')

    assert titles(data, '2026-09-17') == ['Forum']
    assert titles(data, '2026-09-24') == ['Forum']
    assert titles(data, '2026-10-01') == ['Forum']


def test_calendar_occurrence_recorded_twice(root):
    """The latest SEQUENCE of a repeated occurrence is shown once."""
    one_calendar(root, [
        WEEKLY_TUESDAY,
        vevent('weekly', '20260929T100000', '20260929T110000', 'Sync',
               extra=['RECURRENCE-ID;TZID=America/New_York:20260929T100000',
                      'SEQUENCE:1', 'LAST-MODIFIED:20260920T120000Z']),
        vevent('weekly', '20260929T100000', '20260929T110000', 'Sync (moved)',
               extra=['RECURRENCE-ID;TZID=America/New_York:20260929T100000',
                      'SEQUENCE:2', 'LAST-MODIFIED:20260921T120000Z']),
    ])

    _, data, _ = run(root, '2026-09-29')

    assert titles(data, '2026-09-29') == ['Sync (moved)']


def test_calendar_same_sequence_latest_modified_wins(root):
    """With equal SEQUENCE, the later LAST-MODIFIED wins, in any order."""
    one_calendar(root, [
        vevent('one', '20260929T100000', '20260929T110000', 'Newer',
               extra=['LAST-MODIFIED:20260921T120000Z']),
        vevent('one', '20260929T100000', '20260929T110000', 'Older',
               extra=['LAST-MODIFIED:20260920T120000Z']),
    ])

    _, data, _ = run(root, '2026-09-29')

    assert titles(data, '2026-09-29') == ['Newer']


def test_calendar_multi_day_all_day_event(root):
    """An all-day event covering 09-28..09-30 shows on 09-29 and 09-30."""
    one_calendar(root, [vevent('trip', date(2026, 9, 28), date(2026, 10, 1), 'Trip')])

    _, data, _ = run(root, '2026-09-29..2026-10-02')

    assert titles(data, '2026-09-29') == ['Trip']
    assert titles(data, '2026-09-30') == ['Trip']
    assert titles(data, '2026-10-01') == []
    event = data['days'][0]['events'][0]
    assert (event['start'], event['end'], event['all_day']) == \
        ('2026-09-28', '2026-09-30', True)


def test_calendar_all_day_first_then_by_start(root):
    """All-day events come first, then timed events by start."""
    one_calendar(root, [
        vevent('late', '20260928T150000', '20260928T160000', 'Late'),
        vevent('early', '20260928T080000', '20260928T083000', 'Early'),
        vevent('hol', date(2026, 9, 28), date(2026, 9, 29), 'Holiday'),
    ])

    _, data, _ = run(root)

    assert titles(data, '2026-09-28') == ['Holiday', 'Early', 'Late']


def test_calendar_stray_dates_filtered(root):
    """Only events overlapping the period are listed."""
    one_calendar(root, [
        vevent('before', '20260927T220000', '20260927T230000', 'Sunday night'),
        vevent('after', '20260929T003000', '20260929T010000', 'Tuesday early'),
        vevent('in', '20260928T090000', '20260928T100000', 'Monday'),
    ])

    _, data, _ = run(root)

    assert [d['date'] for d in data['days']] == ['2026-09-28']
    assert titles(data, '2026-09-28') == ['Monday']


# Tests for attendance

ORGANIZER_SAM = 'ORGANIZER;CN=Sam Lee:mailto:sam@example.com'


def attendee(address, partstat=None, cn=None, cutype=None):
    params = ''.join(f';{k}={v}' for k, v in (('CN', cn), ('CUTYPE', cutype),
                                              ('PARTSTAT', partstat)) if v)
    return f'ATTENDEE{params}:mailto:{address}'


def only_event(root, extra, name='me@example.com'):
    """Run with one event carrying extra lines; return (text line, JSON event)."""
    write_ics(ics_dir(root) / 'me.ics', vcalendar(
        [vevent('e', '20260928T090000', '20260928T100000', 'Meeting', extra=extra)],
        name=name))
    lines, data, _ = run(root)
    return lines[1], data['days'][0]['events'][0]


@pytest.mark.parametrize('partstat, response', [
    ('ACCEPTED', 'yes'), ('TENTATIVE', 'maybe'), ('NEEDS-ACTION', 'no-reply')])
def test_calendar_attendance_my_response(root, partstat, response):
    """The user's PARTSTAT is their response, in JSON and text."""
    line, event = only_event(root, [ORGANIZER_SAM,
                                    attendee('sam@example.com', 'ACCEPTED'),
                                    attendee('me@example.com', partstat)])

    assert event['response'] == response
    assert event['mine'] is False
    marker = '' if response == 'yes' else f' [{response}]'
    assert line == f'09:00-10:00  Meeting{marker}'


def test_calendar_attendance_single_attendee(root):
    """A single ATTENDEE value (not a list) is read."""
    line, event = only_event(root, [ORGANIZER_SAM,
                                    attendee('Me@Example.com', 'TENTATIVE')])

    assert event['response'] == 'maybe'
    assert event['attendee_count'] == 1


def test_calendar_attendance_created_by_user(root):
    """An event the user organized is theirs, with no text marker."""
    line, event = only_event(root, [
        'ORGANIZER;CN=Me:mailto:me@example.com',
        attendee('me@example.com', 'ACCEPTED', cn='Me'),
        attendee('sam@example.com', 'NEEDS-ACTION', cn='Sam Lee')])

    assert event['mine'] is True
    assert event['organizer'] == {'name': 'Me', 'email': 'me@example.com'}
    assert event['response'] == 'yes'
    assert event['attendees'] == [
        {'name': 'Me', 'email': 'me@example.com', 'response': 'yes'},
        {'name': 'Sam Lee', 'email': 'sam@example.com', 'response': 'no-reply'}]
    assert line == '09:00-10:00  Meeting'


def test_calendar_attendance_own_event_maybe_not_marked(root):
    """A maybe on an event the user organized isn't marked in the text."""
    line, event = only_event(root, ['ORGANIZER:mailto:me@example.com',
                                    attendee('me@example.com', 'TENTATIVE')])

    assert event['response'] == 'maybe'
    assert line == '09:00-10:00  Meeting'


def test_calendar_attendance_personal_event(root):
    """No organizer or attendees in the user's calendar: mine, no response."""
    line, event = only_event(root, [])

    assert event['mine'] is True
    assert event['organizer'] is None
    assert event['response'] is None
    assert event['attendee_count'] == 0
    assert line == '09:00-10:00  Meeting'


def test_calendar_attendance_other_calendar_event(root):
    """No organizer or attendees in another calendar: not mine, no marker."""
    line, event = only_event(root, [], name='Team')

    assert event['mine'] is False
    assert line == '09:00-10:00  Meeting'


def test_calendar_attendance_not_invited(root):
    """Someone else's meeting without the user: no response, no marker."""
    line, event = only_event(root, [ORGANIZER_SAM,
                                    attendee('sam@example.com', 'ACCEPTED')])

    assert event['mine'] is False
    assert event['response'] is None
    assert event['organizer'] == {'name': 'Sam Lee', 'email': 'sam@example.com'}
    assert line == '09:00-10:00  Meeting'


def test_calendar_attendance_large_meeting(root):
    """30 people and a room: count 30, the first 20 listed, room left out."""
    people = [attendee(f'p{n}@example.com', 'DECLINED' if n == 1 else None)
              for n in range(30)]
    room = attendee('room4@resource.example.com', 'ACCEPTED', cn='Room 4',
                    cutype='ROOM')
    _, event = only_event(root, [ORGANIZER_SAM, room, *people])

    assert event['attendee_count'] == 30
    assert [a['email'] for a in event['attendees']] == \
        [f'p{n}@example.com' for n in range(20)]
    assert event['attendees'][1]['response'] == 'no'
    assert event['attendees'][0]['response'] is None


def test_calendar_attendance_email_unset(root):
    """Without email, nothing is mine and there's no response."""
    (root / '.meta-notes').write_text(
        SENTINEL + '[calendar]\ntimezone = "America/New_York"\n')
    line, event = only_event(root, [
        'ORGANIZER:mailto:me@example.com', attendee('me@example.com', 'TENTATIVE')])

    assert event['mine'] is False
    assert event['response'] is None
    assert line == '09:00-10:00  Meeting'


# Tests for agenda output

def test_calendar_text_output(root):
    """Headings, all-day lines, and timed lines with attendance, no location."""
    write_ics(ics_dir(root) / 'team.ics', vcalendar([
        vevent('s', '20260928T090000', '20260928T093000', 'Standup',
               extra=['LOCATION:Room 4', ORGANIZER_SAM,
                      'ATTENDEE;PARTSTAT=ACCEPTED:mailto:me@example.com']),
        vevent('h', date(2026, 9, 28), date(2026, 9, 29), 'Holiday'),
    ], name='Team'))

    lines, _, _ = run(root)

    assert lines == ['## 2026-09-28 Mon', 'all day  Holiday',
                     '09:00-09:30  Standup']


def test_calendar_empty_day(root):
    """A day with no events still has its heading."""
    one_calendar(root, [])

    lines, _, _ = run(root, '2026-09-29')

    assert lines == ['## 2026-09-29 Tue']


def test_calendar_default_period(root):
    """Without --date, the agenda covers today only."""
    one_calendar(root, [])

    _, data, _ = run(root)

    assert [d['date'] for d in data['days']] == ['2026-09-28']


def test_calendar_week_range(root):
    """A range has one day per date, including empty days."""
    one_calendar(root, [])

    lines, data, _ = run(root, '2026-09-28..2026-10-02')

    assert [d['date'] for d in data['days']] == [
        '2026-09-28', '2026-09-29', '2026-09-30', '2026-10-01', '2026-10-02']
    assert [line for line in lines if line.startswith('## ')] == [
        '## 2026-09-28 Mon', '## 2026-09-29 Tue', '## 2026-09-30 Wed',
        '## 2026-10-01 Thu', '## 2026-10-02 Fri']


def test_calendar_json_shape(root):
    """Events, source, and pruned have the documented fields."""
    one_calendar(root, [vevent('s', '20260928T090000', '20260928T093000',
                               'Standup', extra=['LOCATION:Room 4'])],
                 modified=date(2026, 9, 27))

    _, data, warnings = run(root)

    assert data['days'] == [{'date': '2026-09-28', 'events': [{
        'start': '2026-09-28T09:00:00-04:00', 'end': '2026-09-28T09:30:00-04:00',
        'all_day': False, 'title': 'Standup', 'location': 'Room 4',
        'calendar': 'me@example.com', 'mine': True, 'organizer': None,
        'response': None, 'attendee_count': 0, 'attendees': []}]}]
    source = data['source']
    assert source['path'] == str(ics_dir(root) / 'me.ics')
    assert source['exported'] == '2026-09-27T12:00:00-04:00'
    assert source['age_days'] == 1
    assert source['cached'] is False
    assert source['available'] == source['loaded'] == ['me@example.com']
    assert data['pruned'] == []
    assert warnings == []


# Tests for the stale export warning

def test_calendar_stale_default_threshold(root):
    """A 4-day-old export warns with its age by default."""
    (root / '.meta-notes').write_text(
        SENTINEL + '[calendar]\nemail = "me@example.com"\ntimezone = "America/New_York"\n')
    one_calendar(root, [], modified=TODAY - timedelta(days=4))

    _, _, warnings = run(root)

    assert any('4 days old' in w for w in warnings)


def test_calendar_stale_three_days_not_stale(root):
    """A 3-day-old export isn't stale by default."""
    one_calendar(root, [], modified=TODAY - timedelta(days=3))

    _, _, warnings = run(root)

    assert warnings == []


def test_calendar_stale_configured_threshold(root):
    """stale_days = 7 accepts a 4-day-old export."""
    set_config(root, 'stale_days = 7\n')
    one_calendar(root, [], modified=TODAY - timedelta(days=4))

    _, _, warnings = run(root)

    assert warnings == []


# Tests for the export cache

def cache_files(root):
    return sorted(p.name for p in cal_dir(root).iterdir())


def test_calendar_cache_reuse(root):
    """A second run uses the cache and gives the same agenda."""
    one_calendar(root, [WEEKLY_TUESDAY])

    _, first, _ = run(root, '2026-09-28..2026-10-02')
    _, second, _ = run(root, '2026-09-28..2026-10-02')

    assert first['source']['cached'] is False
    assert second['source']['cached'] is True
    assert first['days'] == second['days']
    assert len(cache_files(root)) == 2


def test_calendar_cache_new_export(root):
    """A new export is read and cached on the next run."""
    one_calendar(root, [vevent('a', '20260928T090000', '20260928T100000', 'Old')],
                 modified=date(2026, 9, 27))
    run(root)
    write_ics(ics_dir(root) / 'new.ics', vcalendar(
        [vevent('a', '20260928T090000', '20260928T100000', 'New')]))

    _, data, _ = run(root)

    assert data['source']['cached'] is False
    assert titles(data, '2026-09-28') == ['New']


def test_calendar_cache_selection_changed(root):
    """Changing calendars reads the export again under a new entry."""
    write_zip(ics_dir(root) / 'export.zip', three_calendars())
    run(root)
    set_config(root, 'calendars = ["me@example.com"]\n')

    _, data, _ = run(root)

    assert data['source']['cached'] is False
    assert data['source']['loaded'] == ['me@example.com']
    # The entry for the old setting is pruned
    assert len(cache_files(root)) == 2


def test_calendar_cache_contents(root):
    """The cache keeps VTIMEZONEs and calendar properties, drops old history."""
    history = [vevent(f'old{n}', f'2025{n % 12 + 1:02d}{n % 27 + 1:02d}T090000',
                      f'2025{n % 12 + 1:02d}{n % 27 + 1:02d}T100000', f'Old {n}')
               for n in range(200)]
    ended = vevent('ended', '20250106T090000', '20250106T100000', 'Ended',
                   extra=['RRULE:FREQ=WEEKLY;UNTIL=20250601T000000Z'])
    counted = vevent('counted', '20250106T090000', '20250106T100000', 'Counted',
                     extra=['RRULE:FREQ=WEEKLY;COUNT=3'])
    old_override = vevent('series', '20250812T110000', '20250812T120000', 'Moved',
                          extra=['RECURRENCE-ID;TZID=America/New_York:20250811T100000'])
    kept_override = vevent('weekly', '20260915T110000', '20260915T120000', 'Moved',
                           extra=['RECURRENCE-ID;TZID=America/New_York:20260908T100000'])
    recent = vevent('recent', '20260925T090000', '20260925T100000', 'Recent')
    old_start = vevent('long', date(2026, 8, 1), date(2026, 10, 1), 'Long')
    one_calendar(root, [*history, ended, counted, WEEKLY_TUESDAY, old_override,
                        kept_override, recent, old_start])

    run(root)

    (cached,) = cal_dir(root).glob('*.ics')
    assert cached.stat().st_size < (ics_dir(root) / 'me.ics').stat().st_size / 5
    parsed = icalendar.Calendar.from_ical(cached.read_bytes())
    assert str(parsed['X-WR-CALNAME']) == 'me@example.com'
    assert [c['TZID'] for c in parsed.walk('VTIMEZONE')] == ['America/New_York']
    uids = sorted(str(e['UID']) for e in parsed.walk('VEVENT'))
    assert uids == ['counted', 'long', 'recent', 'weekly', 'weekly']
    meta = json.loads(cached.with_suffix('.json').read_text())
    assert meta['horizon'] == '2026-08-29'
    assert meta['name'] == 'me.ics'


def test_calendar_cache_agenda_equals_export(root):
    """Within the horizon, the cached agenda equals the export's."""
    events = [
        WEEKLY_TUESDAY,
        vevent('weekly', '20260930T140000', '20260930T150000', 'Weekly',
               extra=['RECURRENCE-ID;TZID=America/New_York:20260929T100000']),
        vevent('m', '20260831T090000', '20260831T100000', 'Horizon day'),
        vevent('trip', date(2026, 8, 20), date(2026, 9, 2), 'Trip'),
        vevent('old', '20260801T090000', '20260801T100000', 'Before'),
    ]
    one_calendar(root, events)
    period = '2026-08-29..2026-10-10'
    run(root, period)

    _, cached, _ = run(root, period)

    data = (ics_dir(root) / 'me.ics').read_bytes()
    export = calendar.prepare(icalendar.Calendar.from_ical(data), None)
    direct = calendar.agenda(recurring_ical_events, [('me@example.com', export)],
                             date(2026, 8, 29), date(2026, 10, 10), NY,
                             'me@example.com')
    assert cached['source']['cached'] is True
    assert cached['days'] == [{'date': d.isoformat(), 'events': e}
                              for d, e in direct.items()]
    assert titles(cached, '2026-08-31') == ['Trip', 'Horizon day']


def test_calendar_cache_folder_created(root):
    """calendar/ is created when missing."""
    cal_dir(root).rmdir()
    one_calendar(root, [])

    run(root)

    assert len(cache_files(root)) == 2


def test_calendar_export_deleted_after_caching(root):
    """With the export gone, the cached calendar is used with a warning."""
    one_calendar(root, [vevent('a', '20260928T090000', '20260928T100000', 'Cached')])
    run(root)
    (ics_dir(root) / 'me.ics').unlink()

    _, data, warnings = run(root)

    assert titles(data, '2026-09-28') == ['Cached']
    assert data['source']['cached'] is True
    assert any('me.ics is missing' in w for w in warnings)


def test_calendar_export_deleted_stale_from_recorded_time(root):
    """A cached calendar's staleness uses its export's recorded time."""
    one_calendar(root, [], modified=TODAY - timedelta(days=5))
    run(root)
    (ics_dir(root) / 'me.ics').unlink()

    _, data, warnings = run(root)

    assert data['source']['age_days'] == 5
    assert any('5 days old' in w for w in warnings)


def test_calendar_nothing_at_all(root):
    """No export and no cache is an error naming the absolute ics/ path."""
    with pytest.raises(ValueError) as exc:
        run(root)

    assert str(ics_dir(root)) in str(exc.value)
    assert 'Google Calendar' in str(exc.value)


OLD_EVENT = vevent('old', '20260730T090000', '20260730T100000', 'Long ago')


def test_calendar_range_before_horizon_reads_export(root):
    """A period 60 days back is read from the export when it exists."""
    one_calendar(root, [OLD_EVENT])
    run(root)

    _, data, warnings = run(root, '2026-07-30')

    assert titles(data, '2026-07-30') == ['Long ago']
    assert data['source']['cached'] is False
    assert warnings == []


def test_calendar_range_before_horizon_without_export(root):
    """Without the export, a period 60 days back warns that events may be missing."""
    one_calendar(root, [OLD_EVENT])
    run(root)
    (ics_dir(root) / 'me.ics').unlink()

    _, data, warnings = run(root, '2026-07-30')

    assert titles(data, '2026-07-30') == []
    assert any('before 2026-08-29 may be missing' in w for w in warnings)


# Tests for pruning

def seven_exports(root, numbers=range(1, 8)):
    """Exports e1 (oldest) to e7 (newest), a day apart."""
    for n in numbers:
        write_ics(ics_dir(root) / f'e{n}.ics', vcalendar([]),
                  modified=TODAY - timedelta(days=7 - n))


def test_calendar_prune_old_exports(root):
    """Seven exports become the newest five, and caches of the others go."""
    seven_exports(root, (1, 2))
    for n in (1, 2):
        run(root, ics=str(ics_dir(root) / f'e{n}.ics'))
    assert len(cache_files(root)) == 4
    seven_exports(root, range(3, 8))

    _, data, _ = run(root)

    assert sorted(p.name for p in ics_dir(root).iterdir()) == \
        ['e3.ics', 'e4.ics', 'e5.ics', 'e6.ics', 'e7.ics']
    assert len(cache_files(root)) == 2  # only e7's
    assert '.meta-notes-cache/ics/e1.ics' in data['pruned']
    assert '.meta-notes-cache/ics/e2.ics' in data['pruned']
    assert sum(p.startswith('.meta-notes-cache/calendar/') for p in data['pruned']) == 4


def test_calendar_prune_other_files_kept(root):
    """Pruning leaves files that aren't exports."""
    seven_exports(root)
    (ics_dir(root) / 'notes.txt').write_text('keep\n')

    run(root)

    assert (ics_dir(root) / 'notes.txt').exists()
    assert len(list(ics_dir(root).glob('*.ics'))) == 5


def test_calendar_prune_old_calendars_setting(root):
    """An entry built for an older calendars setting is removed."""
    write_zip(ics_dir(root) / 'export.zip', three_calendars())
    set_config(root, 'calendars = ["Birthdays"]\n')
    run(root)
    old = cache_files(root)
    set_config(root, 'calendars = ["me@example.com"]\n')

    _, data, _ = run(root)

    assert not set(old) & set(cache_files(root))
    assert sorted(data['pruned']) == sorted(
        f'.meta-notes-cache/calendar/{name}' for name in old)


def test_calendar_prune_keeps_ics_entry_for_its_run(root, tmp_path):
    """A --ics file's entry is kept for its run and pruned by the next."""
    one_calendar(root, [])
    other = write_ics(tmp_path / 'Downloads' / 'other.ics', vcalendar([]))
    run(root)

    _, data, _ = run(root, ics=str(other))
    assert len(cache_files(root)) == 4
    assert data['pruned'] == []

    _, data, _ = run(root)
    assert len(cache_files(root)) == 2
    assert len(data['pruned']) == 2


def test_calendar_prune_no_exports_keeps_newest_entry(root):
    """With no exports, only the newest cache entry is kept."""
    one_calendar(root, [], modified=date(2026, 9, 26))
    run(root)
    write_ics(ics_dir(root) / 'newer.ics', vcalendar([]), modified=date(2026, 9, 27))
    # Build newer.ics's entry without pruning me.ics's
    run(root, ics=str(ics_dir(root) / 'newer.ics'))
    assert len(cache_files(root)) == 4
    (ics_dir(root) / 'me.ics').unlink()
    (ics_dir(root) / 'newer.ics').unlink()
    (cal_dir(root) / 'stray.txt').write_text('x\n')

    _, data, warnings = run(root)

    assert any('newer.ics is missing' in w for w in warnings)
    remaining = cache_files(root)
    assert len(remaining) == 2
    meta = json.loads((cal_dir(root) / [n for n in remaining if n.endswith('.json')][0]).read_text())
    assert meta['name'] == 'newer.ics'
    assert '.meta-notes-cache/calendar/stray.txt' in data['pruned']


# Tests for clear function and the cache clear command

def test_calendar_cache_clear(root, capsys):
    """cache clear empties calendar/ and leaves exports and the README."""
    for n in range(3):
        write_ics(ics_dir(root) / f'e{n}.ics', vcalendar([]))
    run(root, ics=str(ics_dir(root) / 'e0.ics'))
    (root / '.meta-notes-cache' / 'README.md').write_text('readme\n')
    assert len(cache_files(root)) == 2

    code, out, _ = run_json(capsys, ['cache', 'clear'])

    assert code == 0
    assert out['count'] == 2
    assert cache_files(root) == []
    assert len(list(ics_dir(root).iterdir())) == 3
    assert (root / '.meta-notes-cache' / 'README.md').exists()


def test_calendar_cache_clear_nothing(root, capsys):
    """A missing calendar/ is not an error."""
    cal_dir(root).rmdir()

    code, out, _ = run_json(capsys, ['cache', 'clear'])

    assert code == 0
    assert out['count'] == 0


def test_calendar_cache_clear_without_libraries(root, monkeypatch, capsys):
    """cache clear doesn't need the calendar libraries."""
    (cal_dir(root) / 'abc.ics').write_text('x\n')
    block_imports(monkeypatch)

    code = cli.main(['cache', 'clear'])

    assert code == 0
    assert capsys.readouterr().out == \
        'Deleted 1 cached calendar file(s) from .meta-notes-cache/calendar/\n'


# Tests for the --with and --search filters

ZACH = attendee('zkim@example.com', 'ACCEPTED', cn='Zachary Kim')
SAPNA = attendee('sapna@example.com', 'ACCEPTED', cn='Sapna Rao')
ME = attendee('me@example.com', 'ACCEPTED')


def filtered(root, events, period=None, names=(), searches=()):
    """Run with events in one calendar and filters; return JSON data."""
    one_calendar(root, events)
    _, data, _ = run(root, period, names=names, searches=searches)
    return data


def all_titles(data):
    return [e['title'] for d in data['days'] for e in d['events']]


def test_calendar_with_first_name_prefix(root):
    """--with zach finds Zachary Kim."""
    data = filtered(root, [
        vevent('a', '20260928T090000', '20260928T093000', 'Sync',
               extra=[ORGANIZER_SAM, ZACH, ME]),
        vevent('b', '20260928T100000', '20260928T103000', 'Other',
               extra=[ORGANIZER_SAM, ME])], names=['zach'])

    assert all_titles(data) == ['Sync']


def test_calendar_with_name_in_email(root):
    """--with "Loan Bui" finds bui.loan@ with no name, words in any order."""
    data = filtered(root, [
        vevent('a', '20260928T090000', '20260928T093000', 'Sync',
               extra=[ORGANIZER_SAM, attendee('bui.loan@example.com')])],
        names=['Loan Bui'])

    assert all_titles(data) == ['Sync']
    assert data['days'][0]['events'][0]['matches']['with'][0]['people'] == [
        {'name': None, 'email': 'bui.loan@example.com', 'response': None}]


def test_calendar_with_attendee_past_cap(root):
    """Sapna as the 25th of 30 attendees matches and is in matches."""
    people = [attendee(f'p{n}@example.com') for n in range(24)]
    people.append(SAPNA)
    people += [attendee(f'q{n}@example.com') for n in range(5)]
    data = filtered(root, [vevent('a', '20260928T090000', '20260928T100000',
                                  'All hands', extra=[ORGANIZER_SAM, *people])],
                    names=['sapna'])

    event = data['days'][0]['events'][0]
    assert event['attendee_count'] == 30
    assert 'sapna@example.com' not in [a['email'] for a in event['attendees']]
    assert event['matches']['with'][0]['people'] == [
        {'name': 'Sapna Rao', 'email': 'sapna@example.com', 'response': 'yes'}]


def test_calendar_with_two_names(root):
    """Every --with NAME must match."""
    data = filtered(root, [
        vevent('a', '20260928T090000', '20260928T093000', 'Zach only',
               extra=[ORGANIZER_SAM, ZACH]),
        vevent('b', '20260928T100000', '20260928T103000', 'Both',
               extra=[ORGANIZER_SAM, ZACH, SAPNA])],
        names=['zach', 'sapna'])

    assert all_titles(data) == ['Both']
    assert [m['name'] for m in data['days'][0]['events'][0]['matches']['with']] \
        == ['zach', 'sapna']


def test_calendar_with_word_start_only(root):
    """--with ann doesn't find Joanna Smith <jsmith@>."""
    data = filtered(root, [
        vevent('a', '20260928T090000', '20260928T093000', 'Sync',
               extra=[ORGANIZER_SAM,
                      attendee('jsmith@example.com', cn='Joanna Smith')])],
        names=['ann'])

    assert data['days'] == []


def test_calendar_with_organizer_only(root):
    """An organizer who isn't an attendee matches, with a null response."""
    data = filtered(root, [
        vevent('a', '20260928T090000', '20260928T093000', 'Sync',
               extra=[ORGANIZER_SAM, ME])], names=['sam'])

    assert data['days'][0]['events'][0]['matches']['with'][0]['people'] == [
        {'name': 'Sam Lee', 'email': 'sam@example.com', 'response': None}]


def test_calendar_with_organizer_also_attendee_listed_once(root):
    """An organizer listed as an attendee matches once, with their response."""
    data = filtered(root, [
        vevent('a', '20260928T090000', '20260928T093000', 'Sync',
               extra=[ORGANIZER_SAM, attendee('sam@example.com', 'ACCEPTED',
                                              cn='Sam Lee')])],
        names=['sam'])

    assert data['days'][0]['events'][0]['matches']['with'][0]['people'] == [
        {'name': 'Sam Lee', 'email': 'sam@example.com', 'response': 'yes'}]


def test_calendar_with_rooms_ignored(root):
    """A room's name doesn't match --with."""
    data = filtered(root, [
        vevent('a', '20260928T090000', '20260928T093000', 'Sync',
               extra=[ORGANIZER_SAM, attendee('r@resource.example.com',
                                              cn='Zach Room', cutype='ROOM')])],
        names=['zach'])

    assert data['days'] == []


def test_calendar_search_topic_in_description(root):
    """--search efp finds EFP in a description, case ignored."""
    data = filtered(root, [
        vevent('a', '20260928T090000', '20260928T093000', 'Quarterly sync',
               extra=['DESCRIPTION:Agenda: EFP rollout']),
        vevent('b', '20260928T100000', '20260928T103000', 'Other')],
        searches=['efp'])

    assert all_titles(data) == ['Quarterly sync']
    assert data['days'][0]['events'][0]['matches'] == {
        'with': [], 'search': [{'text': 'efp', 'fields': ['description']}]}


def test_calendar_search_title_and_location(root):
    """--search lists every field it matched, as typed (no word splitting)."""
    data = filtered(root, [
        vevent('a', '20260928T090000', '20260928T093000', 'Zach 1:1',
               extra=['LOCATION:1:1 room'])], searches=['1:1'])

    assert data['days'][0]['events'][0]['matches']['search'] == [
        {'text': '1:1', 'fields': ['title', 'location']}]


def test_calendar_filters_combined(root):
    """--with and --search together keep only events matching both."""
    data = filtered(root, [
        vevent('a', '20260928T090000', '20260928T093000', 'Zach 1:1',
               extra=[ORGANIZER_SAM, ZACH]),
        vevent('b', '20260928T100000', '20260928T103000', 'Platform sync',
               extra=[ORGANIZER_SAM, ZACH]),
        vevent('c', '20260928T110000', '20260928T113000', 'Sapna 1:1',
               extra=[ORGANIZER_SAM, SAPNA])],
        names=['zach'], searches=['1:1'])

    assert all_titles(data) == ['Zach 1:1']


def test_calendar_filter_only_matching_days(root):
    """A filtered week lists only days with a matching event."""
    one_calendar(root, [
        vevent('a', '20260928T090000', '20260928T093000', 'Standup'),
        vevent('b', '20260930T090000', '20260930T093000', 'Zach sync',
               extra=[ORGANIZER_SAM, ZACH]),
        vevent('c', '20260930T100000', '20260930T103000', 'Other')])

    lines, data, _ = run(root, '2026-09-28..2026-10-02', names=['zach'])

    assert [d['date'] for d in data['days']] == ['2026-09-30']
    assert all_titles(data) == ['Zach sync']
    assert lines == ['## 2026-09-30 Wed', '09:00-09:30  Zach sync']


def test_calendar_filter_recurring_occurrences(root):
    """Each occurrence of a series is filtered, over every day it falls on."""
    one_calendar(root, [
        vevent('a', '20260928T090000', '20260928T093000', 'Zach weekly',
               extra=['RRULE:FREQ=WEEKLY', ORGANIZER_SAM, ZACH])])

    _, data, _ = run(root, '2026-09-28..2026-10-12', names=['zach'])

    assert [d['date'] for d in data['days']] == [
        '2026-09-28', '2026-10-05', '2026-10-12']


def test_calendar_filter_no_matches(root):
    """No matches: text says so and days is empty."""
    one_calendar(root, [vevent('a', '20260928T090000', '20260928T093000',
                               'Standup', extra=[ORGANIZER_SAM, ZACH])])

    lines, data, _ = run(root, '2026-09-28..2026-10-02', names=['nobody'])

    assert lines == ['No matching events.']
    assert data['days'] == []


def test_calendar_filter_matches_json(root):
    """The matches object for an accepted Zachary Kim is exact."""
    data = filtered(root, [
        vevent('a', '20260928T090000', '20260928T093000', 'Sync',
               extra=[ORGANIZER_SAM, ZACH])], names=['zach'])

    assert data['days'][0]['events'][0]['matches']['with'] == [
        {'name': 'zach', 'people': [{'name': 'Zachary Kim',
                                     'email': 'zkim@example.com',
                                     'response': 'yes'}]}]


def test_calendar_unfiltered_has_no_matches(root):
    """Without a filter, every day is listed and events have no matches."""
    data = filtered(root, [vevent('a', '20260928T090000', '20260928T093000',
                                  'Sync', extra=[ORGANIZER_SAM, ZACH])],
                    '2026-09-28..2026-09-29')

    assert [d['date'] for d in data['days']] == ['2026-09-28', '2026-09-29']
    assert 'matches' not in data['days'][0]['events'][0]


@pytest.mark.parametrize('name', ['', '  ', '--', '.'])
def test_calendar_with_name_without_letters(root, name):
    """A NAME with no letters or digits is an error."""
    one_calendar(root, [])

    with pytest.raises(ValueError, match='--with'):
        run(root, names=[name])


# Tests for the calendar command

def fresh_export(root):
    """An export modified now, so it isn't stale whatever today is."""
    path = ics_dir(root) / 'me.ics'
    path.write_text(vcalendar([vevent('s', '20260928T090000', '20260928T093000',
                                      'Standup', extra=['LOCATION:Room 4'])],
                              name='me@example.com'))
    return path


def test_cli_calendar_text(root, capsys):
    """Text output is the agenda, with nothing on stderr."""
    fresh_export(root)

    code = cli.main(['calendar', '--date', '2026-09-28'])
    captured = capsys.readouterr()

    assert code == 0
    assert captured.out == '## 2026-09-28 Mon\n09:00-09:30  Standup\n'
    assert captured.err == ''


def test_cli_calendar_text_warnings_and_pruned_on_stderr(root, capsys):
    """Warnings and deleted paths go to stderr without --json."""
    fresh_export(root)
    (cal_dir(root) / 'stray.txt').write_text('x\n')
    (root / '.meta-notes').write_text(SENTINEL)

    code = cli.main(['calendar', '--date', '2026-09-28'])
    err = capsys.readouterr().err

    assert code == 0
    assert 'Deleted: .meta-notes-cache/calendar/stray.txt' in err
    assert 'Warning: email is not set' in err


def test_cli_calendar_json(root, capsys):
    """--json returns the agenda and source."""
    fresh_export(root)

    code, out, err = run_json(capsys, ['calendar', '--date', '2026-09-28..2026-09-29'])

    assert code == 0
    assert out['ok'] is True
    assert [d['date'] for d in out['days']] == ['2026-09-28', '2026-09-29']
    assert out['source']['loaded'] == ['me@example.com']
    assert out['pruned'] == []
    assert out['warnings'] == []
    assert err == ''


def test_cli_calendar_no_export_json(root, capsys):
    """With no export, --json gives one error object and no stderr."""
    code, out, err = run_json(capsys, ['calendar'])

    assert code == 1
    assert out['ok'] is False
    assert str(ics_dir(root)) in out['error']
    assert err == ''


def test_cli_calendar_invalid_date(root, capsys):
    """An invalid --date is an error."""
    code, out, _ = run_json(capsys, ['calendar', '--date', '2026-13'])

    assert code == 1
    assert 'Invalid date' in out['error']


def test_cli_calendar_with_and_search(root, capsys):
    """--with and --search are repeatable and reach the filter."""
    path = ics_dir(root) / 'me.ics'
    path.write_text(vcalendar([
        vevent('a', '20260928T090000', '20260928T093000', 'Zach 1:1',
               extra=[ORGANIZER_SAM, ZACH, SAPNA, 'DESCRIPTION:EFP']),
        vevent('b', '20260928T100000', '20260928T103000', 'Zach sync',
               extra=[ORGANIZER_SAM, ZACH])], name='me@example.com'))

    code, out, _ = run_json(capsys, [
        'calendar', '--date', '2026-09-28', '--with', 'zach', '--with', 'sapna',
        '--search', '1:1', '--search', 'efp'])

    assert code == 0
    assert [e['title'] for e in out['days'][0]['events']] == ['Zach 1:1']
    matches = out['days'][0]['events'][0]['matches']
    assert [m['name'] for m in matches['with']] == ['zach', 'sapna']
    assert matches['search'] == [{'text': '1:1', 'fields': ['title']},
                                 {'text': 'efp', 'fields': ['description']}]


def test_cli_calendar_no_matches_text(root, capsys):
    """No matches prints the line and exits 0."""
    fresh_export(root)

    code = cli.main(['calendar', '--date', '2026-09-28', '--search', 'nothing'])

    assert code == 0
    assert capsys.readouterr().out == 'No matching events.\n'


def test_cli_calendar_with_invalid_name(root, capsys):
    """A NAME without letters or digits is an error."""
    fresh_export(root)

    code, out, _ = run_json(capsys, ['calendar', '--with', '...'])

    assert code == 1
    assert '--with' in out['error']
