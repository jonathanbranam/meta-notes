"""
Unit tests for scripts/meta_notes/project.py
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import project


@pytest.fixture
def root(tmp_path, monkeypatch):
    """A notes root as the current directory."""
    for folder in ('project', 'area', 'archive/project'):
        (tmp_path / folder).mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def write(path, *lines):
    """Write lines to a file (with trailing newline), creating parents."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(''.join(line + '\n' for line in lines))


def apply(text, fields):
    return project.apply_fields(text.encode(), fields).decode()


ARCHIVE = {'status': 'archived', 'archived': '2026-09-25'}


# Tests for project_for function

def test_project_for_note_project(root):
    write('project/make-bread.md', '# Make Bread')

    assert project.project_for('project/make-bread.md') == 'project/make-bread.md'
    assert project.project_for('project/make-bread') == 'project/make-bread.md'


def test_project_for_folder_project(root):
    write('project/kitchen/Home.md', '# Kitchen')

    assert project.project_for('project/kitchen') == 'project/kitchen'
    assert project.project_for('project/kitchen/') == 'project/kitchen'


def test_project_for_archived_project(root):
    write('archive/project/old.md', '# Old')

    assert project.project_for('archive/project/old.md') == 'archive/project/old.md'


def test_project_for_nested_note_is_not_a_project(root):
    write('project/kitchen/Tasks.md', '# Tasks')

    assert project.project_for('project/kitchen/Tasks.md') is None


def test_project_for_area_is_not_a_project(root):
    write('area/health/Home.md', '# Health')

    assert project.project_for('area/health') is None


def test_project_for_missing_path(root):
    assert project.project_for('project/nope') is None


# Tests for home_note function

def test_home_note_note_project(root):
    write('project/make-bread.md', '# Make Bread')

    assert project.home_note('project/make-bread.md') == 'project/make-bread.md'


def test_home_note_folder_project(root):
    write('project/kitchen/Home.md', '# Kitchen')
    write('project/kitchen/Tasks.md', '# Tasks')

    assert project.home_note('project/kitchen') == 'project/kitchen/Home.md'


def test_home_note_folder_without_home(root):
    write('project/trip/Packing.md', '# Packing')

    assert project.home_note('project/trip') is None


# Tests for parse_fields / read_fields functions

def test_read_fields_simple(root):
    write('project/make-bread.md',
          '# Make Bread', '', '- status: paused', '- tag: make-bread')

    assert project.read_fields('project/make-bread.md') == {
        'status': 'paused', 'tag': 'make-bread'}


def test_parse_fields_case_insensitive_keys():
    assert project.parse_fields(b'# P\n\n- Status: waiting\n') == {'status': 'waiting'}


def test_parse_fields_task_list_is_not_a_field_list():
    assert project.parse_fields(b'# Make Bread\n\n- [ ] Buy a banneton #next\n') == {}


def test_parse_fields_list_under_later_heading_ignored():
    assert project.parse_fields(b'# Make Bread\n\n## Notes\n- status: paused\n') == {}


def test_parse_fields_only_first_list():
    text = b'# P\n\n- [ ] task\n\n- status: paused\n'

    assert project.parse_fields(text) == {}


def test_parse_fields_no_title():
    assert project.parse_fields(b'- status: waiting\n\nSome notes.\n') == {'status': 'waiting'}


def test_parse_fields_no_title_list_not_at_top():
    assert project.parse_fields(b'Some notes.\n\n- status: waiting\n') == {}


def test_parse_fields_mixed_list_skips_tasks():
    text = b'# P\n- status: active\n- [x] done: yes\n- tag: p\n'

    assert project.parse_fields(text) == {'status': 'active', 'tag': 'p'}


# Tests for apply_fields function

def test_apply_fields_replace_status_add_archived():
    text = '# Make Bread\n\n- status: active\n- tag: make-bread\n\n- [ ] task\n'

    assert apply(text, ARCHIVE) == (
        '# Make Bread\n\n- status: archived\n- tag: make-bread\n'
        '- archived: 2026-09-25\n\n- [ ] task\n')


def test_apply_fields_case_insensitive_key():
    assert apply('# P\n\n- Status: paused\n', {'status': 'archived'}) == (
        '# P\n\n- status: archived\n')


def test_apply_fields_replaces_existing_archived():
    text = '# P\n\n- archived: 2020-01-01\n- status: done\n'

    assert apply(text, ARCHIVE) == '# P\n\n- archived: 2026-09-25\n- status: archived\n'


def test_apply_fields_drops_duplicate_keys():
    text = '# P\n\n- status: active\n- tag: p\n- status: paused\n'

    assert apply(text, {'status': 'archived'}) == '# P\n\n- status: archived\n- tag: p\n'


def test_apply_fields_no_field_list():
    assert apply('# Make Bread\n\nSome notes.\n', ARCHIVE) == (
        '# Make Bread\n\n- status: archived\n- archived: 2026-09-25\n\nSome notes.\n')


def test_apply_fields_no_blank_after_title():
    assert apply('# Make Bread\nSome notes.\n', ARCHIVE) == (
        '# Make Bread\n\n- status: archived\n- archived: 2026-09-25\n\nSome notes.\n')


def test_apply_fields_title_only():
    assert apply('# Make Bread\n', ARCHIVE) == (
        '# Make Bread\n\n- status: archived\n- archived: 2026-09-25\n')


def test_apply_fields_title_without_newline():
    assert apply('# Make Bread', ARCHIVE) == (
        '# Make Bread\n\n- status: archived\n- archived: 2026-09-25\n')


def test_apply_fields_task_list_gets_new_list():
    assert apply('# P\n\n- [ ] task\n', {'status': 'archived'}) == (
        '# P\n\n- status: archived\n\n- [ ] task\n')


def test_apply_fields_no_title():
    assert apply('Some notes.\n', ARCHIVE) == (
        '- status: archived\n- archived: 2026-09-25\n\nSome notes.\n')


def test_apply_fields_no_title_existing_list():
    assert apply('- status: waiting\n\nSome notes.\n', {'status': 'archived'}) == (
        '- status: archived\n\nSome notes.\n')


def test_apply_fields_empty_note():
    assert apply('', {'status': 'archived'}) == '- status: archived\n'


def test_apply_fields_list_at_end_without_trailing_newline():
    assert apply('# P\n\n- status: active', ARCHIVE) == (
        '# P\n\n- status: archived\n- archived: 2026-09-25')


def test_apply_fields_crlf():
    text = '# P\r\n\r\n- status: active\r\n\r\nNotes\r\n'

    assert apply(text, ARCHIVE) == (
        '# P\r\n\r\n- status: archived\r\n- archived: 2026-09-25\r\n\r\nNotes\r\n')


def test_apply_fields_crlf_no_field_list():
    assert apply('# P\r\nNotes\r\n', {'status': 'archived'}) == (
        '# P\r\n\r\n- status: archived\r\n\r\nNotes\r\n')


# Tests for set_fields function

def test_set_fields_writes_note(root):
    write('project/p.md', '# P', '', '- status: active')

    project.set_fields('project/p.md', ARCHIVE)

    assert Path('project/p.md').read_text() == (
        '# P\n\n- status: archived\n- archived: 2026-09-25\n')
