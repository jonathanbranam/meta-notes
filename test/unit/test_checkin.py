"""
Unit tests for scripts/meta_notes/checkin.py
"""

import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

import pytest

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import checkin

DAILY = 'plan/daily/26-Q3/2026-09-25 Fri.md'
DAY = date(2026, 9, 25)

NOTE = """# Daily Note - 2026-09-25 Fri

### Time Block

| Time    | Plan                                 | Actual                      |
| ------- | ------------------------------------ | --------------------------- |
|  8:45am |                                      |                             |
|  9:00am | mtg: standup                         | standup                     |
|  9:15am |                                      |                             |
|  9:30am | write spec                           |                             |
|  9:45am | write spec                           |                             |
| 10:00am | review PRs                           |                             |
| 12:15pm | lunch                                |                             |

### Log

|  1:00pm | not a block row                      |                             |
"""


def make_note(root, text=NOTE):
    target = root / DAILY
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    return target


@pytest.fixture
def root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


# Tests for parse_time

def test_checkin_parse_time_forms():
    assert checkin.parse_time('09:10') == time(9, 10)
    assert checkin.parse_time('9:10') == time(9, 10)
    assert checkin.parse_time('3:20pm') == time(15, 20)
    assert checkin.parse_time('3:20 PM') == time(15, 20)
    assert checkin.parse_time('12:15am') == time(0, 15)
    assert checkin.parse_time('12:15pm') == time(12, 15)


@pytest.mark.parametrize('text', ['25:00', '13:00pm', 'noon', '9', ''])
def test_checkin_parse_time_invalid(text):
    with pytest.raises(ValueError):
        checkin.parse_time(text)


# Tests for time_block_rows

def test_checkin_time_block_rows_cells():
    rows = checkin.time_block_rows(NOTE.splitlines())

    assert [r.label for r in rows] == ['8:45am', '9:00am', '9:15am', '9:30am',
                                       '9:45am', '10:00am', '12:15pm']
    assert (rows[1].plan, rows[1].actual) == ('mtg: standup', 'standup')
    assert rows[2].plan == '' and rows[2].actual == ''


def test_checkin_time_block_rows_none_without_heading():
    assert checkin.time_block_rows(['| 9:00am | a | b |']) == []


# Tests for status

def test_checkin_status_unfilled_since_last_actual(root):
    make_note(root)

    data = checkin.status(DAY, time(10, 5))

    assert data['current'] == {'time': '10:00am', 'plan': 'review PRs',
                               'actual': ''}
    assert data['unfilled'] == [{'time': '9:15am', 'plan': ''},
                                {'time': '9:30am', 'plan': 'write spec'},
                                {'time': '9:45am', 'plan': 'write spec'}]
    assert data['note'] == DAILY and data['note_exists'] is True


def test_checkin_status_nothing_filled_starts_at_first_plan(root):
    text = NOTE.replace('| standup                     |',
                        '|                             |')
    make_note(root, text)

    data = checkin.status(DAY, time(9, 50))

    assert [r['time'] for r in data['unfilled']] == ['9:00am', '9:15am',
                                                     '9:30am']


def test_checkin_status_before_first_row(root):
    make_note(root)

    data = checkin.status(DAY, time(7, 0))

    assert data['current'] is None and data['unfilled'] == []


def test_checkin_status_missing_note(root):
    data = checkin.status(DAY, time(10, 0))

    assert data['note_exists'] is False
    assert data['current'] is None and data['unfilled'] == []


def test_checkin_status_no_time_block(root):
    make_note(root, '# Daily\n')

    data = checkin.status(DAY, time(10, 0))

    assert data['note_exists'] is True and data['current'] is None


def test_checkin_status_writes_nothing(root):
    target = make_note(root)

    checkin.status(DAY, time(10, 0))

    assert target.read_text() == NOTE


# Tests for wait

def fake_clock(start):
    state = {'now': start, 'sleeps': []}

    def now():
        return state['now']

    def sleep(seconds):
        state['sleeps'].append(seconds)
        state['now'] += timedelta(seconds=seconds)

    return state, now, sleep


def test_checkin_wait_interval_elapses():
    start = datetime(2026, 9, 25, 10, 0)
    state, now, sleep = fake_clock(start)

    due, reason = checkin.wait(start, 30, time(17, 30), now, sleep)

    assert reason == 'due' and due == datetime(2026, 9, 25, 10, 30)
    assert state['now'] >= due
    assert max(state['sleeps']) <= checkin.TICK_SECONDS


def test_checkin_wait_end_comes_first():
    start = datetime(2026, 9, 25, 17, 10)
    _, now, sleep = fake_clock(start)

    due, reason = checkin.wait(start, 30, time(17, 30), now, sleep)

    assert reason == 'end' and due == datetime(2026, 9, 25, 17, 30)


def test_checkin_wait_past_end_returns_without_sleeping():
    start = datetime(2026, 9, 25, 17, 45)
    state, now, sleep = fake_clock(start)

    _, reason = checkin.wait(start, 30, time(17, 30), now, sleep)

    assert reason == 'end' and state['sleeps'] == []


# Tests for fill_actual

def test_checkin_fill_actual_one_row_padded(root):
    target = make_note(root)

    result = checkin.fill_actual(DAY, time(9, 15), time(9, 15), 'reviewed PRs')

    lines = target.read_text().splitlines()
    assert lines[8] == ('|  9:15am |                                      '
                        '| reviewed PRs                |')
    assert result == {'note': DAILY, 'written': ['9:15am'], 'skipped': []}
    assert lines[:8] == NOTE.splitlines()[:8]
    assert lines[9:] == NOTE.splitlines()[9:]


def test_checkin_fill_actual_range_skips_filled(root):
    target = make_note(root)

    result = checkin.fill_actual(DAY, time(9, 0), time(9, 45), 'spec work')

    assert result['written'] == ['9:15am', '9:30am', '9:45am']
    assert result['skipped'] == ['9:00am']
    assert 'standup' in target.read_text()


def test_checkin_fill_actual_force_overwrites(root):
    target = make_note(root)

    result = checkin.fill_actual(DAY, time(9, 0), time(9, 0), 'x', force=True)

    assert result['written'] == ['9:00am']
    assert '| x                           |' in target.read_text()


def test_checkin_fill_actual_pipe_and_newline(root):
    target = make_note(root)

    checkin.fill_actual(DAY, time(9, 15), time(9, 15), 'a | b\nc')

    assert '| a / b c                     |' in target.read_text()


def test_checkin_fill_actual_long_text_not_truncated(root):
    target = make_note(root)
    text = 'x' * 40

    checkin.fill_actual(DAY, time(9, 15), time(9, 15), text)

    assert f'| {text} |' in target.read_text()


@pytest.mark.parametrize('first,text', [(time(7, 0), 'x'), (time(9, 15), ' ')])
def test_checkin_fill_actual_errors_write_nothing(root, first, text):
    target = make_note(root)

    with pytest.raises(ValueError):
        checkin.fill_actual(DAY, first, first, text)

    assert target.read_text() == NOTE


def test_checkin_fill_actual_missing_note(root):
    with pytest.raises(ValueError, match='no daily note'):
        checkin.fill_actual(DAY, time(9, 0), time(9, 0), 'x')
