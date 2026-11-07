"""
Unit tests for scripts/meta_notes/list_note.py and the `list` commands.

Tests the list note format, group and item edits, file order, and that a list
item is never a task.
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import cli, list_note

LIST = 'resource/lists/26-Q4/2026-11-07 Walmart.md'


@pytest.fixture
def notes_root(tmp_path, monkeypatch):
    (tmp_path / '.meta-notes').write_text('# meta-notes notes root\n')
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.chdir(tmp_path)
    return tmp_path


def run(capsys, *argv, ok=True):
    """Run the CLI with --json; return the parsed output."""
    code = cli.main(list(argv) + ['--json'])
    out = json.loads(capsys.readouterr().out)
    assert (code == 0) == ok, out
    assert out['ok'] == ok
    return out


def new_list(capsys):
    run(capsys, 'list', 'new', 'Walmart', '--date', '2026-11-07')
    return Path(LIST)


def item_texts(out):
    return [(g['name'], i['text'], i['state'])
            for g in out['groups'] for i in g['items']]


# Tests for list new and ls

def test_list_new_creates_empty_list_in_quarter_folder(notes_root, capsys):
    out = run(capsys, 'list', 'new', 'Walmart', '--date', '2026-11-07')
    assert out['list'] == LIST
    assert Path(LIST).read_text() == '# 2026-11-07 Walmart\n'


def test_list_new_existing_list_fails(notes_root, capsys):
    new_list(capsys)
    run(capsys, 'list', 'new', 'Walmart', '--date', '2026-11-07', ok=False)


def test_list_new_name_with_slash_fails(notes_root, capsys):
    run(capsys, 'list', 'new', 'a/b', ok=False)
    assert not Path('resource').exists()


def test_list_ls_counts_open_items(notes_root, capsys):
    new_list(capsys)
    run(capsys, 'list', 'item-add', 'Walmart', 'milk')
    run(capsys, 'list', 'item-add', 'Walmart', 'eggs')
    run(capsys, 'list', 'check', 'Walmart', '1')
    out = run(capsys, 'list', 'ls')
    assert out['lists'] == [{'list': LIST, 'date': '2026-11-07',
                             'name': 'Walmart', 'items': 2, 'open': 1}]


def test_list_show_unknown_name_fails(notes_root, capsys):
    out = run(capsys, 'list', 'show', 'Costco', ok=False)
    assert 'list ls' in out['error']


def test_list_show_newest_list_with_the_name(notes_root, capsys):
    run(capsys, 'list', 'new', 'Walmart', '--date', '2026-10-01')
    new_list(capsys)
    assert run(capsys, 'list', 'show', 'Walmart')['list'] == LIST


# Tests for groups and items

def test_list_items_groups_order_round_trips(notes_root, capsys):
    new_list(capsys)
    run(capsys, 'list', 'group-add', 'Walmart', 'Produce')
    run(capsys, 'list', 'group-add', 'Walmart', 'Dairy')
    run(capsys, 'list', 'item-add', 'Walmart', 'milk?', '--group', 'Dairy')
    run(capsys, 'list', 'item-add', 'Walmart', 'bananas', '--group', 'Produce')
    run(capsys, 'list', 'item-add', 'Walmart', 'apples', '--group', 'Produce',
        '--position', '1')
    run(capsys, 'list', 'item-move', 'Walmart', '2', '--group', 'Dairy',
        '--position', '2')
    out = run(capsys, 'list', 'group-move', 'Walmart', 'Dairy', '1')
    expected = [('Dairy', 'milk?', 'open'), ('Dairy', 'bananas', 'open'),
                ('Produce', 'apples', 'open')]
    assert item_texts(out) == expected
    assert Path(LIST).read_text() == (
        '# 2026-11-07 Walmart\n\n## Dairy\n- [ ] milk?\n- [ ] bananas\n\n'
        '## Produce\n- [ ] apples\n')
    assert item_texts(run(capsys, 'list', 'show', LIST)) == expected


def test_list_group_rename_keeps_items(notes_root, capsys):
    new_list(capsys)
    run(capsys, 'list', 'group-add', 'Walmart', 'Produce')
    run(capsys, 'list', 'item-add', 'Walmart', 'apples', '--group', 'Produce')
    out = run(capsys, 'list', 'group-rename', 'Walmart', 'Produce',
              'Produce (front)')
    assert item_texts(out) == [('Produce (front)', 'apples', 'open')]


def test_list_group_missing_or_duplicate_fails(notes_root, capsys):
    new_list(capsys)
    run(capsys, 'list', 'group-add', 'Walmart', 'Produce')
    before = Path(LIST).read_text()
    run(capsys, 'list', 'group-add', 'Walmart', 'Produce', ok=False)
    run(capsys, 'list', 'item-add', 'Walmart', 'x', '--group', 'Nope', ok=False)
    run(capsys, 'list', 'group-move', 'Walmart', 'Nope', '1', ok=False)
    assert Path(LIST).read_text() == before


def test_list_flat_list_has_unnamed_group(notes_root, capsys):
    new_list(capsys)
    out = run(capsys, 'list', 'item-add', 'Walmart', 'milk')
    assert [g['name'] for g in out['groups']] == [None]


def test_list_item_text_with_task_markers_refused(notes_root, capsys):
    new_list(capsys)
    before = Path(LIST).read_text()
    for text in ('soup \U0001F4C5 2026-11-08', 'soup \U0001F6EB 2026-11-08',
                 'soup ✅ 2026-11-08', 'a\nb', ' '):
        run(capsys, 'list', 'item-add', 'Walmart', text, ok=False)
    assert Path(LIST).read_text() == before
    run(capsys, 'list', 'item-add', 'Walmart', 'soup')
    before = Path(LIST).read_text()
    run(capsys, 'list', 'item-edit', 'Walmart', '1', '--text',
        'soup \U0001F4C5', ok=False)
    assert Path(LIST).read_text() == before


def test_list_item_expect_mismatch_changes_nothing(notes_root, capsys):
    new_list(capsys)
    run(capsys, 'list', 'item-add', 'Walmart', 'milk?')
    before = Path(LIST).read_text()
    out = run(capsys, 'list', 'item-edit', 'Walmart', '1', '--expect', 'eggs',
              '--text', 'eggs x2', ok=False)
    assert 'milk?' in out['error']
    run(capsys, 'list', 'check', 'Walmart', '1', '--expect', 'eggs', ok=False)
    run(capsys, 'list', 'item-move', 'Walmart', '1', '--expect', 'eggs',
        '--position', '1', ok=False)
    assert Path(LIST).read_text() == before


def test_list_item_number_out_of_range_fails(notes_root, capsys):
    new_list(capsys)
    run(capsys, 'list', 'check', 'Walmart', '1', ok=False)


def test_list_item_edit_changes_text(notes_root, capsys):
    new_list(capsys)
    run(capsys, 'list', 'item-add', 'Walmart', 'milk?')
    out = run(capsys, 'list', 'item-edit', 'Walmart', '1', '--text', 'milk')
    assert item_texts(out) == [(None, 'milk', 'open')]


# Tests for states

def test_list_states_check_cancel_uncheck(notes_root, capsys):
    new_list(capsys)
    run(capsys, 'list', 'item-add', 'Walmart', 'milk')
    run(capsys, 'list', 'item-add', 'Walmart', 'eggs')
    run(capsys, 'list', 'check', 'Walmart', '1')
    run(capsys, 'list', 'cancel', 'Walmart', '2')
    assert Path(LIST).read_text().splitlines()[2:] == [
        '- [x] milk', '- [-] eggs']
    out = run(capsys, 'list', 'uncheck', 'Walmart', '1')
    assert [i[2] for i in item_texts(out)] == ['open', 'canceled']


# Tests for parse and render

def test_list_note_render_keeps_other_lines_and_hand_edits(notes_root):
    text = ('# 2026-11-07 Walmart\n\nNotes for the trip.\n\n'
            '- [X] flat item\n  * a note\n\n## Dairy\n\nlead line\n'
            '- [ ] milk?\n')
    note = list_note.parse('x.md', text.split('\n'))
    assert note.head == ['# 2026-11-07 Walmart', 'Notes for the trip.']
    assert note.items()[0][1].state == 'done'
    again = list_note.parse('x.md', list_note.render(note).split('\n'))
    assert list_note.render(again) == list_note.render(note)
    assert 'a note' in list_note.render(note)
    assert 'lead line' in list_note.render(note)


# Tests for items never being tasks

def test_list_items_never_listed_as_tasks(notes_root, capsys):
    new_list(capsys)
    run(capsys, 'list', 'group-add', 'Walmart', 'Produce')
    run(capsys, 'list', 'item-add', 'Walmart', 'milk?', '--group', 'Produce')
    run(capsys, 'list', 'item-add', 'Walmart', 'eggs')
    run(capsys, 'list', 'cancel', 'Walmart', '1')
    out = run(capsys, 'tasks', '--status', 'all', '--all')
    assert out['tasks'] == []
