"""
Unit tests for scripts/meta_notes/note.py

Tests periodic paths, template dates, template selection, and that notes are
written only when new. The date_for_path cases are ported from the removed
ExtractDateForTemplate vader tests.
"""

import os
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
repo_dir = Path(__file__).parent.parent.parent
scripts_dir = repo_dir / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import note, template

DAILY_TEMPLATE = repo_dir / 'templates' / 'daily.md'
TODAY = date(2026, 9, 25)


@pytest.fixture
def notes_root(tmp_path, monkeypatch):
    """An empty notes root as the current directory."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def write(path, lines):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(line + '\n' for line in lines))


def create(kind, value=None, **kwargs):
    return note.create(kind, value, today=TODAY, **kwargs)


def all_files(root):
    return sorted(str(p.relative_to(root)) for p in root.rglob('*'))


# Tests for periodic_note function

def test_periodic_note_daily():
    assert note.periodic_note('daily', date(2026, 2, 13)) == (
        'plan/daily/26-Q1/2026-02-13 Fri.md', date(2026, 2, 13),
        '# Daily Note - 2026-02-13 Fri')


def test_periodic_note_daily_q3():
    path, _, _ = note.periodic_note('daily', date(2026, 7, 15))
    assert path == 'plan/daily/26-Q3/2026-07-15 Wed.md'


def test_periodic_note_weekly_uses_monday():
    assert note.periodic_note('weekly', date(2026, 2, 13)) == (
        'plan/week/26-Q1/2026-02-09.md', date(2026, 2, 9),
        '# Week Plan - 2026-02-09')


def test_periodic_note_weekly_monday_in_previous_quarter():
    """Thursday 2026-04-02's Monday is 2026-03-30, in Q1."""
    path, template_date, _ = note.periodic_note('weekly', date(2026, 4, 2))
    assert path == 'plan/week/26-Q1/2026-03-30.md'
    assert template_date == date(2026, 3, 30)


def test_periodic_note_weekly_monday_in_previous_year():
    path, _, _ = note.periodic_note('weekly', date(2026, 1, 1))
    assert path == 'plan/week/25-Q4/2025-12-29.md'


def test_periodic_note_quarterly():
    assert note.periodic_note('quarterly', date(2026, 8, 15)) == (
        'plan/quarter/2026-Q3.md', date(2026, 7, 1), '# Quarterly Plan - 2026 Q3')
    assert note.periodic_note('quarterly', date(2026, 12, 31))[1] == date(2026, 10, 1)


def test_periodic_note_yearly():
    assert note.periodic_note('yearly', date(2026, 8, 15)) == (
        'plan/year/2026.md', date(2026, 1, 1), '# Year Plan - 2026')


def test_periodic_note_daily_template_week_link_is_weekly_path(monkeypatch):
    """
    The shipped daily template links to the path `weekly` files that week under.

    Covers every day of 2025 and 2026: the quarter and year boundaries, and
    the weeks that span them.
    """
    monkeypatch.setattr(template, '_run', lambda command: (0, ''))
    d = date(2025, 1, 1)
    while d.year < 2027:
        path, _, _ = note.periodic_note('daily', d)
        rendered = template.render(str(DAILY_TEMPLATE),
                                   template.build_context(d, path, TODAY))
        links = [line.removeprefix('Week Plan: [[').removesuffix(']]') + '.md'
                 for line in rendered.lines if line.startswith('Week Plan: ')]
        assert links == [note.periodic_note('weekly', d)[0]], d
        d += timedelta(days=1)


# Tests for parse_date function

def test_parse_date_valid():
    assert note.parse_date('2026-02-13') == date(2026, 2, 13)


@pytest.mark.parametrize('value', ['2026-13-45', '2026-02-30', '20260213',
                                   '2026-2-13', 'today', ''])
def test_parse_date_invalid(value):
    with pytest.raises(note.NoteError,
                       match=f'Invalid date: {value} \\(expected YYYY-MM-DD\\)'):
        note.parse_date(value)


# Tests for date_for_path function

def test_date_for_path_daily():
    assert note.date_for_path('plan/daily/26-Q1/2026-02-13 Thu.md', TODAY) == date(2026, 2, 13)


def test_date_for_path_daily_requires_day_suffix():
    assert note.date_for_path('plan/daily/26-Q1/2026-02-13.md', TODAY) == TODAY


def test_date_for_path_weekly():
    assert note.date_for_path('plan/week/26-Q1/2026-02-09.md', TODAY) == date(2026, 2, 9)


def test_date_for_path_weekly_with_day_abbreviation():
    assert note.date_for_path('plan/week/26-Q1/2026-02-09 Mon.md', TODAY) == date(2026, 2, 9)


def test_date_for_path_quarterly():
    for q, month in (('Q1', 1), ('Q2', 4), ('Q3', 7), ('Q4', 10)):
        assert (note.date_for_path(f'plan/quarter/2026-{q}.md', TODAY)
                == date(2026, month, 1))


def test_date_for_path_yearly():
    assert note.date_for_path('plan/year/2026.md', TODAY) == date(2026, 1, 1)


def test_date_for_path_regular_note_uses_today():
    assert note.date_for_path('project/my-project/note.md', TODAY) == TODAY


def test_date_for_path_invalid_date_in_name():
    with pytest.raises(note.NoteError, match='Invalid date: 2026-02-30'):
        note.date_for_path('plan/daily/26-Q1/2026-02-30 Mon.md', TODAY)


# Tests for note_path function

def test_note_path_appends_extension():
    assert note.note_path('project/lunch/Lunch Ideas') == 'project/lunch/Lunch Ideas.md'


def test_note_path_keeps_extension():
    assert note.note_path('project/lunch/Lunch Ideas.md') == 'project/lunch/Lunch Ideas.md'


def test_note_path_normalizes():
    assert note.note_path('project/./a/../b') == 'project/b.md'


@pytest.mark.parametrize('path', ['../elsewhere/note', 'project/../../x', '..', '/tmp/x'])
def test_note_path_outside_root(path):
    with pytest.raises(note.NoteError, match='Path is outside the notes root'):
        note.note_path(path)


@pytest.mark.parametrize('path', ['', '.', 'project/..'])
def test_note_path_empty(path):
    with pytest.raises(note.NoteError, match='Invalid note path'):
        note.note_path(path)


# Tests for create function: template selection and fallback headers

@pytest.mark.parametrize('kind, value, header', [
    ('daily', '2026-02-13', '# Daily Note - 2026-02-13 Fri'),
    ('weekly', '2026-02-13', '# Week Plan - 2026-02-09'),
    ('quarterly', '2026-02-13', '# Quarterly Plan - 2026 Q1'),
    ('yearly', '2026-02-13', '# Year Plan - 2026'),
    ('new', 'area/garden/Beds', '# area/garden/Beds'),
])
def test_create_fallback_header(notes_root, kind, value, header):
    result = create(kind, value, render_only=True)
    assert result.content == header + '\n\n'
    assert result.template is None


def test_create_uses_standard_template(notes_root):
    write('resource/template/daily.md', ['# Daily {{date}}'])
    result = create('daily', '2026-02-13', render_only=True)
    assert result.template == 'resource/template/daily.md'
    assert result.content == '# Daily 2026-02-13 Fri\n'


def test_create_uses_folder_template(notes_root):
    write('project/trip/template.md', ['# {{project_name}}: {{note_name}}'])
    result = create('new', 'project/trip/Packing', render_only=True)
    assert result.template == 'project/trip/template.md'
    assert result.content == '# trip: Packing\n'


def test_create_new_date_from_plan_path(notes_root):
    write('resource/template/yearly.md', ['{{date}}'])
    result = create('new', 'plan/year/2027', render_only=True)
    assert result.content == '2027-01-01 Fri\n'


def test_create_new_date_defaults_to_today(notes_root):
    write('area/x/template.md', ['{{date}}'])
    assert create('new', 'area/x/y', render_only=True).content == '2026-09-25 Fri\n'


def test_create_template_override(notes_root):
    write('resource/template/checklist.md', ['# Checklist'])
    write('project/trip/template.md', ['# Folder'])
    result = create('new', 'project/trip/Packing', template_name='checklist',
                    render_only=True)
    assert result.template == 'resource/template/checklist.md'
    assert result.content == '# Checklist\n'


def test_create_template_override_missing(notes_root):
    with pytest.raises(note.NoteError,
                       match='^Template not found: resource/template/nope.md$'):
        create('new', 'project/trip/Packing', template_name='nope')
    assert all_files(notes_root) == []


def test_create_new_outside_root_writes_nothing(notes_root):
    with pytest.raises(note.NoteError, match='outside the notes root'):
        create('new', '../elsewhere/note')
    assert all_files(notes_root) == []


def test_create_invalid_date_writes_nothing(notes_root):
    with pytest.raises(note.NoteError, match='Invalid date: 2026-13-45'):
        create('daily', '2026-13-45')
    assert all_files(notes_root) == []


def test_create_date_defaults_to_today(notes_root):
    assert create('daily', render_only=True).path == 'plan/daily/26-Q3/2026-09-25 Fri.md'


def test_create_date_defaults_to_real_today(notes_root):
    result = note.create('yearly', render_only=True)
    assert result.path == f'plan/year/{date.today().year}.md'


# Tests for create function: writing

def test_create_writes_new_note_with_folders(notes_root):
    result = create('daily', '2026-02-13')
    path = notes_root / 'plan/daily/26-Q1/2026-02-13 Fri.md'
    assert path.read_text() == '# Daily Note - 2026-02-13 Fri\n\n'
    assert (result.path, result.exists, result.created) == (
        'plan/daily/26-Q1/2026-02-13 Fri.md', False, True)
    assert result.warnings == []


def test_create_existing_note_unchanged(notes_root):
    write('resource/template/daily.md', ['{{% shell touch ran %}}'])
    path = notes_root / 'plan/daily/26-Q1/2026-02-13 Fri.md'
    path.parent.mkdir(parents=True)
    path.write_bytes(b'# Mine\r\nkeep')
    os.utime(path, (1_000_000_000, 1_000_000_000))

    for render_only in (False, True):
        result = create('daily', '2026-02-13', render_only=render_only)
        assert (result.exists, result.created, result.content) == (True, False, None)
        assert result.template is None

    assert path.read_bytes() == b'# Mine\r\nkeep'
    assert path.stat().st_mtime == 1_000_000_000
    # The template's commands didn't run
    assert not (notes_root / 'ran').exists()


def test_create_render_only_writes_nothing(notes_root):
    write('resource/template/daily.md', ['# {{date}}', '{{% shell echo hi %}}'])
    before = all_files(notes_root)
    result = create('daily', '2026-02-13', render_only=True)
    assert all_files(notes_root) == before
    assert (result.exists, result.created) == (False, False)
    assert result.content == '# 2026-02-13 Fri\nhi\n\n'


def test_create_written_content_matches_render(notes_root):
    write('resource/template/weekly.md', ['# {{week_start}}', '', 'x'])
    rendered = create('weekly', '2026-02-13', render_only=True)
    written = create('weekly', '2026-02-13')
    assert (notes_root / written.path).read_text() == rendered.content


def test_create_race_does_not_overwrite(notes_root, monkeypatch):
    """A note created between the check and the write is left alone."""
    from meta_notes import template

    def render_and_race(path, context):
        write('plan/year/2026.md', ['# theirs'])
        return template.Rendered(lines=['# ours'])

    write('resource/template/yearly.md', ['# ours'])
    monkeypatch.setattr(template, 'render', render_and_race)
    result = create('yearly', '2026-02-13')
    assert (result.exists, result.created) == (True, False)
    assert (notes_root / 'plan/year/2026.md').read_text() == '# theirs\n'


def test_create_failed_command_still_writes(notes_root):
    write('resource/template/yearly.md', ['# Y', '{{% shell exit 3 %}}'])
    result = create('yearly', '2026-02-13')
    assert result.created
    assert result.warnings == ['Command failed: {{% shell exit 3 %}}']
    assert '<!-- Command failed: {{% shell exit 3 %}}' in (
        notes_root / 'plan/year/2026.md').read_text()


def test_create_vim_block_warning_only_when_writing(notes_root):
    write('resource/template/yearly.md', ['{{% vim echo "{{date}}" %}}'])
    rendered = create('yearly', '2026-02-13', render_only=True)
    assert rendered.warnings == []
    assert rendered.content == '{{% vim echo "2026-01-01 Thu" %}}\n'

    written = create('yearly', '2026-02-13')
    assert written.warnings == [
        'plan/year/2026.md: {{% vim %}} blocks are left as text outside Vim']
    assert (notes_root / 'plan/year/2026.md').read_text() == rendered.content
