"""
Unit tests for scripts/meta_notes/ceremony.py
"""

import sys
from datetime import date
from pathlib import Path

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import ceremony

DAILY = 'plan/daily/26-Q3/2026-09-25 Fri.md'
WEEKLY = 'plan/week/26-Q3/2026-09-21.md'


def write(root, path, text):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def by_name(data):
    return {c['name']: c for c in data['ceremonies']}


# Tests for find_marker function

def test_find_marker_checked_with_completion_date():
    marker = ceremony.find_marker(
        ['- [x] shutdown complete ✅ 2026-09-26'], 'shutdown complete')

    assert marker == ceremony.Marker(True, True, date(2026, 9, 26))


def test_find_marker_checked_without_completion_date():
    marker = ceremony.find_marker(['- [x] plan complete'], 'plan complete')

    assert marker == ceremony.Marker(True, True, None)


def test_find_marker_uppercase_x_is_done():
    assert ceremony.find_marker(['- [X] plan complete'], 'plan complete').done


def test_find_marker_unchecked_not_done():
    marker = ceremony.find_marker(['- [ ] shutdown complete'], 'shutdown complete')

    assert marker == ceremony.Marker(True, False, None)


def test_find_marker_canceled_not_done():
    marker = ceremony.find_marker(['- [-] shutdown complete'], 'shutdown complete')

    assert marker.present
    assert not marker.done


def test_find_marker_ignores_case_and_whitespace():
    marker = ceremony.find_marker(['  * [x]   Shutdown Complete  '],
                                  'shutdown complete')

    assert marker.done


def test_find_marker_missing():
    marker = ceremony.find_marker(['# Daily Note', '- [x] other thing'],
                                  'shutdown complete')

    assert marker == ceremony.Marker(False, False, None)


def test_find_marker_other_text_is_not_marker():
    marker = ceremony.find_marker(['- [x] Shutdown complete.'], 'shutdown complete')

    assert not marker.present


def test_find_marker_any_done_line_wins():
    marker = ceremony.find_marker(
        ['- [ ] plan complete', '- [x] plan complete ✅ 2026-09-25'],
        'plan complete')

    assert marker == ceremony.Marker(True, True, date(2026, 9, 25))


def test_find_marker_found_anywhere():
    lines = ['# Daily', '', '## Notes', 'text', '- [x] shutdown complete']

    assert ceremony.find_marker(lines, 'shutdown complete').done


# Tests for status function

def test_status_all_four_ceremonies(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path, DAILY, '- [x] plan complete\n- [ ] shutdown complete\n')
    write(tmp_path, WEEKLY,
          '- [x] review complete ✅ 2026-09-25\n- [ ] plan complete\n')

    data = ceremony.status(date(2026, 9, 25))

    c = by_name(data)
    assert [n for n in c] == ['daily-plan', 'daily-shutdown', 'weekly-review',
                              'weekly-plan']
    assert c['daily-plan']['done'] is True
    assert c['daily-shutdown']['done'] is False
    assert c['weekly-review'] == {
        'name': 'weekly-review', 'note': WEEKLY, 'note_exists': True,
        'marker_present': True, 'done': True, 'completed': '2026-09-25'}
    assert c['weekly-plan']['done'] is False


def test_status_missing_weekly_note(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path, DAILY, '- [ ] plan complete\n')

    c = by_name(ceremony.status(date(2026, 9, 25)))

    for name in ('weekly-review', 'weekly-plan'):
        assert c[name]['note'] == WEEKLY
        assert c[name]['note_exists'] is False
        assert c[name]['done'] is False
    assert c['daily-shutdown']['note_exists'] is True
    assert c['daily-shutdown']['marker_present'] is False


def test_status_week_start_and_date(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    data = ceremony.status(date(2026, 9, 27))

    assert data['date'] == '2026-09-27'
    assert data['week_start'] == '2026-09-21'


# Tests for format_status function

def test_format_status_lines(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path, DAILY, '- [x] plan complete\n'
                           '- [x] shutdown complete ✅ 2026-09-26\n')

    lines, _ = ceremony.run(date(2026, 9, 25))

    assert lines == [
        'daily-plan:     done',
        'daily-shutdown: done 2026-09-26',
        'weekly-review:  not done (no note)',
        'weekly-plan:    not done (no note)',
    ]


def test_format_status_no_marker(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path, DAILY, '# Daily Note\n')

    lines, _ = ceremony.run(date(2026, 9, 25))

    assert lines[0] == 'daily-plan:     not done (no marker)'
