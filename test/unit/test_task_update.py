"""
Unit tests for scripts/meta_notes/task_update.py

Tests line edits (status, tags, dates, ✅ stamping) and the file update
guards.
"""

import os
import sys
from datetime import date
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import task_update
from meta_notes.task_update import TaskUpdateError, edit_line, update

TODAY = date(2026, 9, 25)


def edit(text, **kwargs):
    """edit_line with a fixed today."""
    return edit_line(text, today=TODAY, **kwargs)


def write_note(tmp_path, lines, ending='\n', final_newline=True):
    """Write a note of lines; return its path."""
    path = tmp_path / 'foo.md'
    content = ending.join(lines) + (ending if final_newline else '')
    path.write_bytes(content.encode('utf-8'))
    return path


# Tests for update function: guards and file handling

def test_update_expect_mismatch(tmp_path):
    """A line that differs from --expect is reported and not written."""
    path = write_note(tmp_path, ['# foo', '', '- [ ] call Sam 📅 2026-10-02'])
    before = path.read_bytes()

    with pytest.raises(TaskUpdateError, match='has changed') as e:
        update(str(path), 3, '- [ ] call Sam 📅 2026-10-01', status='x')

    assert e.value.current == '- [ ] call Sam 📅 2026-10-02'
    assert path.read_bytes() == before


def test_update_expect_ignores_trailing_whitespace(tmp_path):
    """Trailing whitespace on the line or on --expect doesn't matter."""
    path = write_note(tmp_path, ['# foo', '', '- [ ] call Sam 📅 2026-10-01  '])

    result = update(str(path), 3, '- [ ] call Sam 📅 2026-10-01 ', status='-')

    assert result.changed
    assert path.read_text().splitlines()[2].startswith('- [-] call Sam')


def test_update_line_out_of_range(tmp_path):
    """A line number past the end of the file is an error."""
    path = write_note(tmp_path, ['- [ ] a 📅'] * 10)
    before = path.read_bytes()

    with pytest.raises(TaskUpdateError, match='out of range'):
        update(str(path), 11, '- [ ] a 📅', status='x')
    with pytest.raises(TaskUpdateError, match='out of range'):
        update(str(path), 0, '- [ ] a 📅', status='x')

    assert path.read_bytes() == before


def test_update_not_a_checkbox(tmp_path):
    """A line without a checkbox is an error, not an edit."""
    path = write_note(tmp_path, ['# project/foo', '', '- [ ] a 📅'])
    before = path.read_bytes()

    with pytest.raises(TaskUpdateError, match='not a checkbox'):
        update(str(path), 1, '# project/foo', status='x')

    assert path.read_bytes() == before


def test_update_missing_file(tmp_path):
    """A file that doesn't exist is an error."""
    with pytest.raises(TaskUpdateError, match='No such file'):
        update(str(tmp_path / 'missing.md'), 1, '- [ ] a', status='x')


def test_update_crlf_file(tmp_path):
    """Every line of a CRLF file keeps its CRLF ending."""
    path = write_note(tmp_path, ['# foo', '', '- [ ] call Sam 📅 2026-10-01',
                                 'after'], ending='\r\n')

    update(str(path), 3, '- [ ] call Sam 📅 2026-10-01', status='-')

    assert path.read_bytes().decode('utf-8') == (
        '# foo\r\n\r\n- [-] call Sam 📅 2026-10-01\r\nafter\r\n')


def test_update_no_final_newline(tmp_path):
    """A file without a final newline still has none after the edit."""
    path = write_note(tmp_path, ['# foo', '- [ ] call Sam 📅 2026-10-01'],
                      final_newline=False)

    update(str(path), 2, '- [ ] call Sam 📅 2026-10-01', status='-')

    assert path.read_bytes().decode('utf-8') == (
        '# foo\n- [-] call Sam 📅 2026-10-01')


def test_update_only_target_line_changes(tmp_path):
    """Other lines, and the number of lines, are unchanged."""
    lines = ['# foo', '', '- [ ] a 📅 2026-10-01', 'text  ', '- [ ] b 📅']
    path = write_note(tmp_path, lines)

    update(str(path), 3, lines[2], status='-')

    new_lines = path.read_text().split('\n')
    assert new_lines == ['# foo', '', '- [-] a 📅 2026-10-01', 'text  ',
                         '- [ ] b 📅', '']


def test_update_several_lines_from_one_query(tmp_path):
    """Line numbers stay valid across several updates."""
    lines = ['# foo', '', '- [ ] a 📅 2026-10-01', '', '', '',
             '- [ ] b 📅 2026-10-02']
    path = write_note(tmp_path, lines)

    update(str(path), 3, lines[2], due='none')
    update(str(path), 7, lines[6], status='-')

    new_lines = path.read_text().splitlines()
    assert new_lines[2] == '- [ ] a'
    assert new_lines[6] == '- [-] b 📅 2026-10-02'


def test_update_unchanged_not_written(tmp_path):
    """When the edit produces the same line, the file isn't written."""
    path = write_note(tmp_path, ['# foo', '', '- [x] call Sam 📅 2026-09-25'])
    os.utime(path, (1_000_000, 1_000_000))

    result = update(str(path), 3, '- [x] call Sam 📅 2026-09-25', status='x',
                    today=TODAY)

    assert not result.changed
    assert result.old == result.new == '- [x] call Sam 📅 2026-09-25'
    assert path.stat().st_mtime == 1_000_000


def test_update_result_old_and_new(tmp_path):
    """The result carries the old and new line text."""
    path = write_note(tmp_path, ['# foo', '', '- [ ] call Sam 📅 2026-09-22'])

    result = update(str(path), 3, '- [ ] call Sam 📅 2026-09-22', status='x',
                    today=TODAY)

    assert result.old == '- [ ] call Sam 📅 2026-09-22'
    assert result.new == '- [x] call Sam 📅 2026-09-22 ✅ 2026-09-25'
    assert result.changed
    assert result.warnings == []


# Tests for marker token helpers

def test_remove_span_takes_preceding_space():
    """Removing a token takes the whitespace before it."""
    text = '- [ ] call  #x Sam'
    assert task_update._remove_span(text, 12, 14) == '- [ ] call Sam'


def test_remove_span_after_checkbox_takes_following_space():
    """A token right after the checkbox takes the whitespace after it."""
    text = '- [ ] #mtg prep'
    assert task_update._remove_span(text, 6, 10) == '- [ ] prep'


def test_remove_span_at_end_takes_trailing_whitespace():
    """A token at the end leaves no trailing whitespace."""
    assert task_update._remove_span('- [ ] a #x  ', 8, 10) == '- [ ] a'
    assert task_update._remove_span('- [ ] #x', 6, 8) == '- [ ]'


def test_remove_span_keeps_other_spacing():
    """Spacing elsewhere in the line is untouched."""
    text = '- [ ] a   b #x c'
    assert task_update._remove_span(text, 12, 14) == '- [ ] a   b c'


def test_insert_order_start_due_completed():
    """New date markers go in 🛫, due, ✅ order."""
    text = edit('- [x] a ✅ 2026-09-24', due='2026-09-22')
    assert text == '- [x] a 📅 2026-09-22 ✅ 2026-09-24'
    text = edit(text, start='2026-09-20')
    assert text == '- [x] a 🛫 2026-09-20 📅 2026-09-22 ✅ 2026-09-24'


def test_insert_due_after_start_before_text():
    """A new due marker goes right after the 🛫 date."""
    assert (edit('- [ ] a 🛫 2026-10-05 more', due='2026-10-10')
            == '- [ ] a 🛫 2026-10-05 📅 2026-10-10 more')


# Tests for --due

def test_edit_line_due_plain_checkbox_undated():
    """--due undated turns a checklist item into an undated task."""
    assert edit('- [ ] buy milk', due='undated') == '- [ ] buy milk 📅'


def test_edit_line_due_change_keeps_emoji():
    """Changing a date keeps the line's due emoji."""
    assert (edit('- [ ] call Sam 📆 2026-10-01', due='2026-10-08')
            == '- [ ] call Sam 📆 2026-10-08')


def test_edit_line_due_date_bare_marker():
    """A bare due emoji gets the date after it."""
    assert (edit('- [ ] someday task 🗓', due='2026-10-08')
            == '- [ ] someday task 🗓 2026-10-08')


def test_edit_line_due_variation_selector():
    """An emoji variation selector after the due emoji is kept."""
    assert (edit('- [ ] task 🗓️ 2026-10-01 x', due='2026-10-08')
            == '- [ ] task 🗓️ 2026-10-08 x')
    assert (edit('- [ ] task 🗓️', due='2026-10-08')
            == '- [ ] task 🗓️ 2026-10-08')


def test_edit_line_due_new_uses_calendar_emoji():
    """A new due date uses 📅 and goes after the start date."""
    assert (edit('- [ ] draft outline 🛫 2026-10-05', due='2026-10-10')
            == '- [ ] draft outline 🛫 2026-10-05 📅 2026-10-10')


def test_edit_line_due_undated():
    """--due undated removes the date and keeps the emoji."""
    assert edit('- [ ] call Sam 📅 2026-10-01', due='undated') == '- [ ] call Sam 📅'
    assert (edit('- [ ] call Sam 📆 2026-10-01 more', due='undated')
            == '- [ ] call Sam 📆 more')


def test_edit_line_due_before_completed():
    """A new due date goes before the ✅ date."""
    assert (edit('- [x] call Sam ✅ 2026-09-24', due='2026-09-22')
            == '- [x] call Sam 📅 2026-09-22 ✅ 2026-09-24')


def test_edit_line_due_none_removes_every_due_marker():
    """--due none removes every due emoji and its date."""
    assert (edit('- [ ] a 📅 2026-10-01 b 🗓 2026-10-02 📆', due='none')
            == '- [ ] a b')


def test_edit_line_due_invalid_date_after_emoji():
    """An invalid date after the emoji is replaced or removed with it."""
    assert (edit('- [ ] a 📅 2026-02-30', due='2026-03-01')
            == '- [ ] a 📅 2026-03-01')
    assert edit('- [ ] a 📅 2026-02-30', due='none') == '- [ ] a'
    assert edit('- [ ] a 📅 2026-02-30', due='undated') == '- [ ] a 📅'


# Tests for --start

def test_edit_line_start_add():
    """A new start date goes before the due date."""
    assert (edit('- [ ] draft outline 📅 2026-10-10', start='2026-10-05')
            == '- [ ] draft outline 🛫 2026-10-05 📅 2026-10-10')


def test_edit_line_start_add_no_dates():
    """Without a due or ✅ date, a new start date goes at the end."""
    assert edit('- [ ] draft', start='2026-10-05') == '- [ ] draft 🛫 2026-10-05'


def test_edit_line_start_replace():
    """An existing start date is replaced."""
    assert (edit('- [ ] a 🛫 2026-10-05 📅 2026-10-10', start='2026-10-06')
            == '- [ ] a 🛫 2026-10-06 📅 2026-10-10')


def test_edit_line_start_remove():
    """--start none removes the start date."""
    assert (edit('- [ ] draft outline 🛫 2026-10-05 📅 2026-10-10', start='none')
            == '- [ ] draft outline 📅 2026-10-10')


# Tests for --status and the completion date

def test_edit_line_status_cancel():
    assert (edit('- [ ] call Sam 📅 2026-10-01', status='-')
            == '- [-] call Sam 📅 2026-10-01')


def test_edit_line_status_reschedule_only_sets_char():
    assert (edit('- [ ] draft outline 📅 2026-09-25', status='>')
            == '- [>] draft outline 📅 2026-09-25')


def test_edit_line_status_done_late():
    assert (edit('- [ ] call Sam 📅 2026-09-22', status='x')
            == '- [x] call Sam 📅 2026-09-22 ✅ 2026-09-25')


def test_edit_line_status_done_on_due_date():
    assert (edit('- [ ] call Sam 📅 2026-09-25', status='x')
            == '- [x] call Sam 📅 2026-09-25')


def test_edit_line_status_done_due_date_set_today_in_same_call():
    """The ✅ rule uses the due date after this call's --due edit."""
    assert (edit('- [ ] call Sam 📅 2026-09-22', status='x', due='2026-09-25')
            == '- [x] call Sam 📅 2026-09-25')
    assert (edit('- [ ] call Sam 📅 2026-09-25', status='x', due='undated')
            == '- [x] call Sam 📅 ✅ 2026-09-25')


def test_edit_line_status_done_undated():
    assert (edit('- [ ] someday task 📅', status='x')
            == '- [x] someday task 📅 ✅ 2026-09-25')


def test_edit_line_status_done_no_completed():
    assert (edit('- [ ] call Sam 📅 2026-09-22', status='x', no_completed=True)
            == '- [x] call Sam 📅 2026-09-22')


def test_edit_line_status_done_keeps_existing_completed():
    """A line with a ✅ date doesn't get a second one."""
    assert (edit('- [ ] call Sam 📅 2026-09-22 ✅ 2026-09-23', status='x')
            == '- [x] call Sam 📅 2026-09-22 ✅ 2026-09-23')


def test_edit_line_status_done_to_done_unchanged():
    """Done set to done again keeps its completion date or lack of one."""
    assert (edit('- [x] call Sam 📅 2026-09-22', status='x')
            == '- [x] call Sam 📅 2026-09-22')
    assert (edit('- [X] call Sam 📅 2026-09-22', status='x')
            == '- [x] call Sam 📅 2026-09-22')


def test_edit_line_status_cancel_removes_completed():
    assert (edit('- [x] call Sam 📅 2026-09-22 ✅ 2026-09-24', status='-')
            == '- [-] call Sam 📅 2026-09-22')


def test_edit_line_status_reopen_removes_completed():
    assert (edit('- [x] call Sam 📅 2026-09-22 ✅ 2026-09-24', status=' ')
            == '- [ ] call Sam 📅 2026-09-22')


def test_edit_line_status_indented_star_bullet():
    assert edit('    * [ ] sub 📅', status='-') == '    * [-] sub 📅'


# Tests for tags

def test_edit_line_add_tag_before_dates():
    assert (edit('- [ ] call Sam 📅 2026-10-01', add_tags=['later'])
            == '- [ ] call Sam #later 📅 2026-10-01')


def test_edit_line_add_tag_before_start_date():
    assert (edit('- [ ] a 🛫 2026-10-01 📅 2026-10-05', add_tags=['next'])
            == '- [ ] a #next 🛫 2026-10-01 📅 2026-10-05')


def test_edit_line_add_tag_without_dates():
    assert edit('- [ ] buy milk', add_tags=['#errand']) == '- [ ] buy milk #errand'


def test_edit_line_add_tag_present_other_case():
    assert (edit('- [ ] #Later read book 📅', add_tags=['later'])
            == '- [ ] #Later read book 📅')


def test_edit_line_add_tag_present_by_alias():
    assert edit('- [ ] #mtg prep 📅', add_tags=['meeting']) == '- [ ] #mtg prep 📅'


def test_edit_line_add_tags_keep_order():
    assert (edit('- [ ] a 📅', add_tags=['x', 'y'])
            == '- [ ] a #x #y 📅')


def test_edit_line_remove_tag_by_alias():
    assert (edit('- [ ] #mtg prep agenda 📅 2026-10-01', remove_tags=['meeting'])
            == '- [ ] prep agenda 📅 2026-10-01')


def test_edit_line_remove_tag_every_occurrence():
    assert (edit('- [ ] a #later b #LATER 📅', remove_tags=['#later'])
            == '- [ ] a b 📅')


def test_edit_line_remove_tag_absent():
    assert edit('- [ ] a #laterish 📅', remove_tags=['later']) == '- [ ] a #laterish 📅'


def test_edit_line_add_and_remove_tags():
    assert (edit('- [ ] #later read book 📅', remove_tags=['later'],
                 add_tags=['next'])
            == '- [ ] read book #next 📅')


# Tests for the no-longer-a-task warning

def test_update_warns_when_line_stops_being_task(tmp_path):
    path = write_note(tmp_path, ['# foo', '', '- [ ] call Sam 📅 2026-10-01'])

    result = update(str(path), 3, '- [ ] call Sam 📅 2026-10-01', due='none')

    assert result.new == '- [ ] call Sam'
    assert len(result.warnings) == 1
    assert 'no longer a task' in result.warnings[0]


def test_update_no_warning_for_plain_checkbox(tmp_path):
    """Editing a checkbox that wasn't a task adds no warning."""
    path = write_note(tmp_path, ['- [ ] buy milk'])

    result = update(str(path), 1, '- [ ] buy milk', status='x', today=TODAY)

    assert result.new == '- [x] buy milk ✅ 2026-09-25'
    assert result.warnings == []
