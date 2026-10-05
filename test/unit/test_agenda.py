"""
Unit tests for the `meta-notes tasks --agenda` preset
(query.agenda, period.agenda_horizon)
"""

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import cli, query
from period import agenda_horizon

THU = date(2026, 10, 8)


# Tests for agenda_horizon

@pytest.mark.parametrize('today,end', [
    (date(2026, 10, 5), date(2026, 10, 12)),   # Mon -> next Monday
    (date(2026, 10, 7), date(2026, 10, 12)),   # Wed -> Monday
    (date(2026, 10, 8), date(2026, 10, 14)),   # Thu -> following Wed
    (date(2026, 10, 9), date(2026, 10, 14)),   # Fri -> following Wed
    (date(2026, 10, 11), date(2026, 10, 19)),  # Sun -> Monday after next
])
def test_period_agenda_horizon_anchors(today, end):
    assert agenda_horizon(today) == end


# Tests for query.agenda

def write_root(tmp_path, monkeypatch, lines):
    (tmp_path / '.meta-notes').write_text('')
    (tmp_path / 'a.md').write_text('\n'.join(lines) + '\n')
    monkeypatch.chdir(tmp_path)
    return str(tmp_path)


def by_section(sections):
    return {s['section']: [t['text'] for t in s['tasks']] for s in sections}


def test_query_agenda_places_tasks(tmp_path, monkeypatch):
    root = write_root(tmp_path, monkeypatch, [
        '- [ ] old 📅 2026-10-01',
        '- [ ] timed 📅 2026-10-08 ⏰ 00:01',
        '- [ ] next 📅 2026-10-09',
        '- [ ] begun 🛫 2026-10-01',
        '- [ ] far 📅 2027-01-01',
        '- [ ] bare 📅',
    ])
    _, sections, _ = query.agenda(root, today=THU)
    got = by_section(sections)
    assert [s['section'] for s in sections][:3] == ['overdue', 'today', '2026-10-09']
    assert sections[-1]['section'] == '2026-10-14'
    assert sections[2]['heading'] == '2026-10-09 Fri'
    assert got['overdue'] == ['- [ ] old 📅 2026-10-01']
    assert len(got['today']) == 2 and any('begun' in t for t in got['today'])
    assert got['2026-10-09'] == ['- [ ] next 📅 2026-10-09']
    assert got['2026-10-10'] == []
    assert not any('far' in t or 'bare' in t for ts in got.values() for t in ts)


def test_query_agenda_undated_off_by_default(tmp_path, monkeypatch):
    root = write_root(tmp_path, monkeypatch, ['- [ ] bare 📅'])
    lines, sections, _ = query.agenda(root, today=THU)
    assert 'undated' not in by_section(sections)
    assert lines == ['No tasks found matching the criteria.']
    lines, sections, _ = query.agenda(root, undated=True, today=THU)
    assert by_section(sections)['undated'] == ['- [ ] bare 📅']
    assert '# Undated' in lines


def test_query_agenda_through_overrides_and_text_omits_empty(tmp_path, monkeypatch):
    root = write_root(tmp_path, monkeypatch, ['- [ ] x 📅 2026-10-10'])
    lines, sections, _ = query.agenda(root, through='2026-10-10', today=THU)
    assert sections[-1]['section'] == '2026-10-10'
    assert '# 2026-10-10 Sat' in lines
    assert '# Today' not in lines


def test_query_agenda_through_before_today(tmp_path, monkeypatch):
    root = write_root(tmp_path, monkeypatch, [])
    with pytest.raises(ValueError):
        query.agenda(root, through='2026-10-01', today=THU)


# Tests for cli tasks --agenda

def test_cli_tasks_agenda_json(tmp_path, monkeypatch, capsys):
    write_root(tmp_path, monkeypatch, [f'- [ ] t 📅 {date.today().isoformat()}'])
    assert cli.main(['tasks', '--agenda', '--undated', '--json']) == 0
    out = capsys.readouterr().out
    assert '"agenda"' in out and '"section": "today"' in out


def test_cli_tasks_agenda_rejects_date(tmp_path, monkeypatch, capsys):
    write_root(tmp_path, monkeypatch, [])
    assert cli.main(['tasks', '--agenda', '--due']) != 0
    assert cli.main(['tasks', '--through', '2026-10-10']) != 0
