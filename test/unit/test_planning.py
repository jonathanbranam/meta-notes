"""
Unit tests for scripts/meta_notes/planning.py
"""

import sys
from datetime import date
from pathlib import Path

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import planning

MON = 'plan/daily/26-Q3/2026-09-21 Mon.md'
TUE = 'plan/daily/26-Q3/2026-09-22 Tue.md'

BLOCK = '''### Time Block

| Time | Plan | Actual |
|------|------|--------|
{rows}
'''


def write(root, path, text):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


# Tests for day_record

def test_planning_day_record_counts_no_plan_and_crossed_out(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rows = ('| 9:00am | ~write spec~ | wrote code |\n'
            '| 10:00am | no plan | email |\n'
            '| 11:00am | ~~double~~ | x |\n'
            '| 12:00pm | lunch | |')
    write(tmp_path, MON, BLOCK.format(rows=rows))

    r = planning.day_record(date(2026, 9, 21))

    assert (r['note_exists'], r['planned'], r['no_plan'], r['crossed_out']) == (
        True, True, 1, 1)


def test_planning_day_record_only_no_plan_is_not_planned(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path, MON, BLOCK.format(rows='| 9:00am | no plan | x |'))

    assert planning.day_record(date(2026, 9, 21))['planned'] is False


def test_planning_day_record_plan_complete_marker_is_planned(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path, MON, '- [x] plan complete\n')

    assert planning.day_record(date(2026, 9, 21))['planned'] is True


def test_planning_day_record_missing_note(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    r = planning.day_record(date(2026, 9, 21))

    assert r['note_exists'] is False
    assert (r['planned'], r['no_plan'], r['crossed_out']) == (False, 0, 0)


# Tests for report and format_report

def test_planning_report_totals_and_lines(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path, MON, BLOCK.format(rows='| 9:00am | ~a~ | x |\n| 10:00am | no plan | y |'))
    write(tmp_path, TUE, '- [ ] plan complete\n')

    data = planning.report('2026-09-21..2026-09-23')

    assert data['totals'] == {'days': 3, 'notes': 2, 'planned': 1,
                              'no_plan': 1, 'crossed_out': 1}
    assert planning.format_report(data) == [
        '2026-09-21: planned, 1 no plan, 1 crossed out',
        '2026-09-22: not planned, 0 no plan, 0 crossed out',
        '2026-09-23: no note',
        'Total: 2 of 3 days with a note, 1 planned, 1 no plan, 1 crossed out']
