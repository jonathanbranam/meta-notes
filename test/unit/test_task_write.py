"""
Unit tests for scripts/meta_notes/task_write.py

Tests replacing notes, replacing a node or a subtree, adding a subtask, and
the status of ancestors after a subtask changes.
"""

import sys
from datetime import date
from pathlib import Path

import pytest

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import task_show, task_update, task_write
from meta_notes.task_update import TaskUpdateError, update

TREE = [
    '# foo',
    '',
    '- [o] main 📅 2026-10-08',
    '  * note on main',
    '  - [x] first',
    '    * note on first',
    '  - [ ] second',
    '  * note after',
    '- [ ] other',
]


def write_note(tmp_path, lines, ending='\n'):
    path = tmp_path / 'foo.md'
    path.write_bytes((ending.join(lines) + ending).encode('utf-8'))
    return path


def read(path):
    return path.read_text().splitlines()


# Tests for show of a node alone with notes after the subtasks

def test_task_show_node_skips_subtasks_before_late_note(tmp_path):
    path = write_note(tmp_path, TREE)
    data, lines, numbers = task_show.show(str(path), 3)
    assert numbers == [3, 4, 8]
    assert lines == ['- [o] main 📅 2026-10-08', '  * note on main',
                     '  * note after']
    assert data['notes'] == ['  * note on main', '  * note after']
    assert data['end_line'] == 8
    assert task_show.format_ranges(numbers) == '3-4,8-8'


def test_task_show_tree_is_contiguous(tmp_path):
    path = write_note(tmp_path, TREE)
    _, lines, numbers = task_show.show(str(path), 3, tree=True)
    assert numbers == [3, 4, 5, 6, 7, 8]
    assert task_show.format_ranges(numbers) == '3-8'
    assert len(lines) == 6


# Tests for replace_notes

def test_task_write_notes_replaced_before_subtasks(tmp_path):
    path = write_note(tmp_path, TREE)
    result = task_write.replace_notes(
        str(path), 3, '  * note on main\n  * note after', '  * new a\n  * new b')
    assert result.changed
    assert read(path) == [
        '# foo', '', '- [o] main 📅 2026-10-08', '  * new a', '  * new b',
        '  - [x] first', '    * note on first', '  - [ ] second',
        '- [ ] other']


def test_task_write_notes_subtask_notes_are_its_own(tmp_path):
    path = write_note(tmp_path, TREE)
    task_write.replace_notes(str(path), 5, '    * note on first', '    * x')
    assert read(path)[3] == '  * note on main'
    assert read(path)[5] == '    * x'


def test_task_write_notes_added_and_removed(tmp_path):
    path = write_note(tmp_path, TREE)
    task_write.replace_notes(str(path), 9, '', '  * hello')
    assert read(path)[-2:] == ['- [ ] other', '  * hello']
    task_write.replace_notes(str(path), 9, '  * hello', '')
    assert read(path)[-1] == '- [ ] other'


def test_task_write_notes_mismatch_writes_nothing(tmp_path):
    path = write_note(tmp_path, TREE)
    before = path.read_bytes()
    with pytest.raises(TaskUpdateError, match='has changed') as e:
        task_write.replace_notes(str(path), 3, '  * stale', '  * x')
    assert e.value.current == '  * note on main\n  * note after'
    assert path.read_bytes() == before


@pytest.mark.parametrize('text', ['no indent', '  - [ ] sub', '  * a\n\n  * b'])
def test_task_write_notes_rejects_bad_notes(tmp_path, text):
    path = write_note(tmp_path, TREE)
    before = path.read_bytes()
    with pytest.raises(TaskUpdateError):
        task_write.replace_notes(
            str(path), 3, '  * note on main\n  * note after', text)
    assert path.read_bytes() == before


def test_task_write_notes_unchanged_not_written(tmp_path):
    path = write_note(tmp_path, TREE, ending='\r\n')
    before = path.read_bytes()
    result = task_write.replace_notes(str(path), 9, '', '')
    assert not result.changed
    assert path.read_bytes() == before


def test_task_write_notes_keeps_crlf(tmp_path):
    path = write_note(tmp_path, TREE, ending='\r\n')
    task_write.replace_notes(str(path), 9, '', '  * hi')
    assert path.read_bytes().endswith(b'- [ ] other\r\n  * hi\r\n')


def test_task_write_notes_not_a_checkbox(tmp_path):
    path = write_note(tmp_path, TREE)
    with pytest.raises(TaskUpdateError, match='not a checkbox'):
        task_write.replace_notes(str(path), 4, '', '')


# Tests for replace_node

def test_task_write_replace_node_keeps_subtasks(tmp_path):
    path = write_note(tmp_path, TREE)
    task_write.replace_node(
        str(path), 3, '- [o] main 📅 2026-10-08\n  * note on main\n  * note after',
        '- [o] main 📅 2026-10-09\n  * only note')
    assert read(path) == [
        '# foo', '', '- [o] main 📅 2026-10-09', '  * only note',
        '  - [x] first', '    * note on first', '  - [ ] second',
        '- [ ] other']


def test_task_write_replace_subtree(tmp_path):
    path = write_note(tmp_path, TREE)
    _, lines, _ = task_show.show(str(path), 3, tree=True)
    result = task_write.replace_node(
        str(path), 3, '\n'.join(lines),
        '- [ ] main\n  - [ ] solo\n    * deep', tree=True)
    assert result.line == 3 and result.end_line == 5
    assert read(path) == ['# foo', '', '- [ ] main', '  - [ ] solo',
                          '    * deep', '- [ ] other']


def test_task_write_replace_subtree_of_a_subtask(tmp_path):
    path = write_note(tmp_path, TREE)
    task_write.replace_node(
        str(path), 5, '  - [x] first\n    * note on first',
        '  - [x] first\n    * changed', tree=True)
    assert read(path)[4:6] == ['  - [x] first', '    * changed']


def test_task_write_replace_status_updates_ancestors(tmp_path):
    path = write_note(tmp_path, TREE)
    result = task_write.replace_node(str(path), 7, '  - [ ] second',
                                     '  - [x] second')
    assert read(path)[2] == '- [X] main 📅 2026-10-08'
    assert result.ancestors == [{'line': 3, 'old': '- [o] main 📅 2026-10-08',
                                 'new': '- [X] main 📅 2026-10-08'}]


def test_task_write_replace_mismatch_writes_nothing(tmp_path):
    path = write_note(tmp_path, TREE)
    before = path.read_bytes()
    with pytest.raises(TaskUpdateError) as e:
        task_write.replace_node(str(path), 5, '  - [ ] first', '  - [x] first')
    assert e.value.current == '  - [x] first\n    * note on first'
    assert path.read_bytes() == before


@pytest.mark.parametrize('text', ['', 'a note', '  - [ ] indented',
                                  '- [ ] a\n\n  * b', '- [ ] a\n* b'])
def test_task_write_replace_rejects_bad_text(tmp_path, text):
    path = write_note(tmp_path, TREE)
    before = path.read_bytes()
    with pytest.raises(TaskUpdateError):
        task_write.replace_node(str(path), 9, '- [ ] other', text)
    assert path.read_bytes() == before


# Tests for add_subtask

def test_task_write_add_subtask_after_notes_and_subtasks(tmp_path):
    path = write_note(tmp_path, TREE)
    result = task_write.add_subtask(
        str(path), 3, '- [o] main 📅 2026-10-08', 'third', due='2026-10-07')
    assert result.line == 9
    assert read(path)[7:10] == ['  * note after', '  - [ ] third 📅 2026-10-07',
                                '- [ ] other']
    assert read(path)[2] == '- [o] main 📅 2026-10-08'


def test_task_write_add_first_subtask_indents_two_deeper(tmp_path):
    path = write_note(tmp_path, TREE)
    task_write.add_subtask(str(path), 5, '  - [x] first', 'inner')
    assert read(path)[5:7] == ['    * note on first', '    - [ ] inner']


def test_task_write_add_subtask_at_end_without_final_newline(tmp_path):
    path = tmp_path / 'foo.md'
    path.write_bytes(b'- [ ] a')
    task_write.add_subtask(str(path), 1, '- [ ] a', 'b')
    assert path.read_bytes() == b'- [ ] a\n  - [ ] b\n'


def test_task_write_add_subtask_mismatch_writes_nothing(tmp_path):
    path = write_note(tmp_path, TREE)
    before = path.read_bytes()
    with pytest.raises(TaskUpdateError) as e:
        task_write.add_subtask(str(path), 9, '- [ ] stale', 'x')
    assert e.value.current == '- [ ] other'
    assert path.read_bytes() == before


def test_task_write_add_subtask_rejects_bad_text(tmp_path):
    path = write_note(tmp_path, TREE)
    with pytest.raises(TaskUpdateError):
        task_write.add_subtask(str(path), 9, '- [ ] other', ' ')


# Tests for partial status of ancestors

def tree_of(statuses):
    """A parent with one subtask per status."""
    return ['- [ ] parent'] + [f'  - [{s}] c{i}' for i, s in enumerate(statuses)]


@pytest.mark.parametrize('done,total,expected', [
    (1, 4, '.'), (2, 4, 'o'), (3, 4, 'O'), (4, 4, 'X'),
    (1, 3, '.'), (2, 3, 'o'), (1, 2, 'o'), (1, 8, '.'), (3, 8, 'o'),
    (5, 8, 'o'), (6, 8, 'O'), (7, 8, 'O'), (8, 8, 'X'), (1, 1, 'X')])
def test_task_update_partial_status_thresholds(tmp_path, done, total, expected):
    statuses = ['x'] * (done - 1) + [' '] * (total - done + 1)
    path = write_note(tmp_path, tree_of(statuses))
    update(str(path), 2 + done - 1, f'  - [ ] c{done - 1}', status='x',
           today=date(2026, 10, 1))
    assert read(path)[0] == f'- [{expected}] parent'


def test_task_update_partial_status_none_checked(tmp_path):
    path = write_note(tmp_path, tree_of(['x', 'x']))
    update(str(path), 2, '  - [x] c0', status=' ')
    assert read(path)[0] == '- [o] parent'
    update(str(path), 3, '  - [x] c1', status=' ')
    assert read(path)[0] == '- [ ] parent'


def test_task_update_partial_status_two_levels(tmp_path):
    path = write_note(tmp_path, [
        '- [ ] top', '  - [ ] mid', '    - [ ] a', '    - [ ] b',
        '  - [ ] other'])
    result = update(str(path), 3, '    - [ ] a', status='x',
                    today=date(2026, 10, 1))
    # mid is half done (o); top has one subtask not done of two: none checked
    assert read(path)[:3] == ['- [ ] top', '  - [o] mid',
                              '    - [x] a 2026-10-01'.replace(
                                  ' 2026', ' ✅ 2026')]
    assert [a['line'] for a in result.ancestors] == [2]
    update(str(path), 4, '    - [ ] b', status='x', today=date(2026, 10, 1))
    assert read(path)[:2] == ['- [o] top', '  - [X] mid']


def test_task_update_partial_status_adds_no_date_or_occurrence(tmp_path):
    path = write_note(tmp_path, [
        '- [ ] parent 🔁 every day 📅 2026-10-01', '  - [ ] only'])
    update(str(path), 2, '  - [ ] only', status='x', today=date(2026, 10, 1))
    assert read(path)[0] == '- [X] parent 🔁 every day 📅 2026-10-01'
    assert len(read(path)) == 2


def test_task_update_partial_status_keeps_lowercase_done(tmp_path):
    path = write_note(tmp_path, ['- [x] parent', '  - [ ] only'])
    update(str(path), 2, '  - [ ] only', status='X', today=date(2026, 10, 1))
    assert read(path)[0] == '- [x] parent'


def test_task_update_partial_status_not_for_other_fields(tmp_path):
    path = write_note(tmp_path, ['- [ ] parent', '  - [x] a', '  - [ ] b'])
    update(str(path), 3, '  - [ ] b', due='2026-10-05')
    assert read(path)[0] == '- [ ] parent'


def test_task_update_partial_status_with_recurring_subtask(tmp_path):
    path = write_note(tmp_path, [
        '- [ ] parent', '  - [ ] chore 🔁 every day 📅 2026-10-01'])
    update(str(path), 2, '  - [ ] chore 🔁 every day 📅 2026-10-01',
           status='x', today=date(2026, 10, 1))
    lines = read(path)
    # The next occurrence is open above, the done one below: one of two
    assert lines[0] == '- [o] parent'
    assert lines[1].startswith('  - [ ] chore') and 'x' in lines[2][:7]
