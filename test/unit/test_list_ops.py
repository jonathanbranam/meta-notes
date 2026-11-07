"""
Unit tests for scripts/meta_notes/list_ops.py and the list commands that use
it: items sourced from a task, and the current list in the daily note.
"""

import json
import sys
from datetime import date
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import cli

LIST = 'resource/lists/26-Q4/2026-11-07 Walmart.md'
TASKS = ['# Home', '', '- [ ] buy soup #walmart \U0001F4C5 2026-11-08',
         '- [ ] call Sam \U0001F4C5 2026-11-08']
SOUP = '- [ ] buy soup #walmart \U0001F4C5 2026-11-08'


@pytest.fixture
def notes_root(tmp_path, monkeypatch):
    (tmp_path / '.meta-notes').write_text('# meta-notes notes root\n')
    (tmp_path / 'project').mkdir()
    (tmp_path / 'project' / 'home.md').write_text('\n'.join(TASKS) + '\n')
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.chdir(tmp_path)
    return tmp_path


def run(capsys, *argv, ok=True):
    code = cli.main(list(argv) + ['--json'])
    out = json.loads(capsys.readouterr().out)
    assert (code == 0) == ok, out
    return out


def sourced_list(capsys):
    run(capsys, 'list', 'new', 'Walmart', '--date', '2026-11-07')
    return run(capsys, 'list', 'item-add', 'Walmart', '3 soups for work',
               '--source', 'project/home.md:3')


def task_lines():
    return Path('project/home.md').read_text().splitlines()


# Tests for item sources

def test_list_item_add_source_copies_task_text_exactly(notes_root, capsys):
    out = sourced_list(capsys)
    item = out['groups'][0]['items'][0]
    assert item['source'] == {'file': 'project/home', 'line': 3, 'text': SOUP}
    assert ('  * source: [[project/home]] line 3: ' + SOUP + '\n'
            in Path(LIST).read_text())
    assert task_lines() == TASKS


def test_list_item_add_source_not_open_checkbox_fails(notes_root, capsys):
    run(capsys, 'list', 'new', 'Walmart', '--date', '2026-11-07')
    for target in ('project/home.md:1', 'project/home.md:99',
                   'project/nope.md:3', 'project/home.md'):
        run(capsys, 'list', 'item-add', 'Walmart', 'x', '--source', target,
            ok=False)
    assert Path(LIST).read_text() == '# 2026-11-07 Walmart\n'


# Tests for check closing the source task

def test_list_check_sourced_item_closes_exactly_that_task(notes_root, capsys):
    sourced_list(capsys)
    out = run(capsys, 'list', 'check', 'Walmart', '1')
    lines = task_lines()
    assert lines[2].startswith('- [x] buy soup #walmart')
    assert lines[:2] == TASKS[:2] and lines[3] == TASKS[3]
    assert out['groups'][0]['items'][0]['state'] == 'done'
    assert out['groups'][0]['items'][0]['closed_task']['text'] == lines[2]


def test_list_check_finds_task_when_its_line_moved(notes_root, capsys):
    sourced_list(capsys)
    Path('project/home.md').write_text('\n'.join(['intro'] + TASKS) + '\n')
    run(capsys, 'list', 'check', 'Walmart', '1')
    assert task_lines()[3].startswith('- [x] buy soup')


def test_list_check_expect_mismatch_changes_neither_file(notes_root, capsys):
    sourced_list(capsys)
    changed = TASKS[:2] + ['- [ ] buy soup and bread #walmart'] + TASKS[3:]
    Path('project/home.md').write_text('\n'.join(changed) + '\n')
    before_list = Path(LIST).read_text()
    out = run(capsys, 'list', 'check', 'Walmart', '1', ok=False)
    assert 'Nothing was changed' in out['error']
    assert task_lines() == changed
    assert Path(LIST).read_text() == before_list


def test_list_check_item_without_source_touches_no_task(notes_root, capsys):
    run(capsys, 'list', 'new', 'Walmart', '--date', '2026-11-07')
    run(capsys, 'list', 'item-add', 'Walmart', 'milk')
    run(capsys, 'list', 'check', 'Walmart', '1')
    assert task_lines() == TASKS


# Tests for uncheck and cancel

def test_list_uncheck_reopens_task_the_list_closed(notes_root, capsys):
    sourced_list(capsys)
    run(capsys, 'list', 'check', 'Walmart', '1')
    out = run(capsys, 'list', 'uncheck', 'Walmart', '1')
    assert task_lines() == TASKS
    assert out['groups'][0]['items'][0]['closed_task'] is None


def test_list_uncheck_mismatch_changes_neither_file(notes_root, capsys):
    sourced_list(capsys)
    run(capsys, 'list', 'check', 'Walmart', '1')
    lines = task_lines()
    lines[2] += ' edited'
    Path('project/home.md').write_text('\n'.join(lines) + '\n')
    before_list = Path(LIST).read_text()
    run(capsys, 'list', 'uncheck', 'Walmart', '1', ok=False)
    assert task_lines() == lines
    assert Path(LIST).read_text() == before_list


def test_list_cancel_sourced_item_leaves_task_open(notes_root, capsys):
    sourced_list(capsys)
    out = run(capsys, 'list', 'cancel', 'Walmart', '1')
    assert task_lines() == TASKS
    assert out['groups'][0]['items'][0]['state'] == 'canceled'


def test_list_cancel_done_item_reopens_task(notes_root, capsys):
    sourced_list(capsys)
    run(capsys, 'list', 'check', 'Walmart', '1')
    run(capsys, 'list', 'cancel', 'Walmart', '1')
    assert task_lines() == TASKS


def test_list_check_twice_changes_nothing_more(notes_root, capsys):
    sourced_list(capsys)
    run(capsys, 'list', 'check', 'Walmart', '1')
    after_first = (task_lines(), Path(LIST).read_text())
    run(capsys, 'list', 'check', 'Walmart', '1')
    assert (task_lines(), Path(LIST).read_text()) == after_first


def test_list_check_recurring_task_tracks_moved_line(notes_root, capsys):
    Path('project/home.md').write_text(
        '- [ ] change filter \U0001F501 every 3 months \U0001F4C5 2026-11-08\n')
    run(capsys, 'list', 'new', 'Walmart', '--date', '2026-11-07')
    run(capsys, 'list', 'item-add', 'Walmart', 'filter', '--source',
        'project/home.md:1')
    out = run(capsys, 'list', 'check', 'Walmart', '1')
    assert out['groups'][0]['items'][0]['closed_task']['line'] == 2
    run(capsys, 'list', 'uncheck', 'Walmart', '1')
    assert len(task_lines()) == 2
    assert all(l.startswith('- [ ]') for l in task_lines())


# Tests for the current list

def test_list_current_set_and_read_back(notes_root, capsys):
    run(capsys, 'list', 'new', 'Walmart', '--date', '2026-11-07')
    out = run(capsys, 'list', 'current', 'Walmart', '--date', '2026-11-07')
    daily = Path(out['daily'])
    assert daily.name == '2026-11-07 Sat.md'
    assert ('Current list: [[resource/lists/26-Q4/2026-11-07 Walmart]]'
            in daily.read_text().splitlines())
    got = run(capsys, 'list', 'current', '--date', '2026-11-07')
    assert got['list'] == LIST


def test_list_current_replaces_the_link_line(notes_root, capsys):
    run(capsys, 'list', 'new', 'Walmart', '--date', '2026-11-07')
    run(capsys, 'list', 'new', 'Lowes', '--date', '2026-11-07')
    run(capsys, 'list', 'current', 'Walmart', '--date', '2026-11-07')
    out = run(capsys, 'list', 'current', 'Lowes', '--date', '2026-11-07')
    text = Path(out['daily']).read_text()
    assert text.count('Current list:') == 1 and 'Lowes]]' in text


def test_list_current_none_when_unset(notes_root, capsys):
    assert run(capsys, 'list', 'current', '--date', '2026-11-07')['list'] is None


def test_list_current_unknown_list_fails_and_writes_no_note(notes_root, capsys):
    run(capsys, 'list', 'current', 'Costco', '--date', '2026-11-07', ok=False)
    assert not Path('plan').exists()
