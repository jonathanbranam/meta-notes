"""
Unit tests for scripts/meta_notes/query.py and `meta-notes tasks`

Text output is compared to running scripts/find_tasks.py directly.
"""

import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import cli, query

FIND_TASKS = scripts_dir / 'find_tasks.py'

TODAY = date.today()
PAST = (TODAY - timedelta(days=3)).isoformat()
FUTURE = (TODAY + timedelta(days=30)).isoformat()


@pytest.fixture
def root(tmp_path, monkeypatch):
    """A notes root with tasks of every status, date, tag, and folder."""
    files = {
        'plan/daily/today.md': [
            '# today',
            f'- [ ] Overdue 📅 {PAST}',
            f'- [x] Done 📅 {PAST} ✅ {PAST}',
            f'- [>] Moved 📅 {PAST}',
            '- [ ] Plain checkbox',
        ],
        'project/foo.md': [
            '# project/foo',
            '',
            '- [ ] #mtg Call Sam 📅 2026-10-01',
            f'- [ ] Later 🛫 {FUTURE}',
            '  - [/] #admin Nested in progress 📅',
            '- [-] Dropped 📅',
            f'- [ ] #later Someday #admin 📅 {PAST}',
            f'- [ ] Due today 📅 {TODAY.isoformat()}',
        ],
        'project/sub/bar.md': [
            '* [ ] #admin No date 🗓',
            f'+ [X] Finished 📅 {PAST} ✅ {PAST}',
        ],
        'area/home.md': [
            f'- [ ] #cd Fix sink 🗓 {FUTURE}',
            'Not a task',
        ],
        'resource/empty.md': ['# nothing here'],
    }
    for path, lines in files.items():
        p = tmp_path / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('\n'.join(lines) + '\n')
    (tmp_path / '.meta-notes').write_text('# meta-notes notes root\n')
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.chdir(tmp_path)
    return tmp_path


def find_tasks_output(root, args):
    proc = subprocess.run([sys.executable, str(FIND_TASKS), *args], cwd=root,
                          capture_output=True, text=True, check=True)
    return proc.stdout


def cli_output(capsys, args):
    code = cli.main(['tasks', *args])
    captured = capsys.readouterr()
    assert code == 0, captured.err
    return captured.out


def cli_json(capsys, args):
    code = cli.main(['tasks', '--json', *args])
    captured = capsys.readouterr()
    assert captured.err == ''
    return code, json.loads(captured.out)


# Tests for text output parity with find_tasks.py

@pytest.mark.parametrize('args', [
    [],
    ['--condensed'],
    ['--format', 'condensed'],
    ['--folder', 'project'],
    ['--folder', 'project/'],
    ['--all', '--folder', 'project', '--status', 'all'],
    ['--all'],
    ['--all', '--later'],
    ['--status', 'all'],
    ['--status', 'completed', '--due', '--date', PAST],
    ['--status', 'rescheduled', '--all'],
    ['--status', 'canceled', '--all'],
    ['--overdue', '--due'],
    ['--overdue', '--due', '--condensed'],
    ['--scheduled', '--date', f'{PAST}..{FUTURE}'],
    ['--future', '--undated'],
    ['--group-by', 'tag'],
    ['--all', '--group-by', 'tag', '--condensed'],
    ['--all', '--tag', 'admin', '--tag', 'mtg'],
    ['--folder', 'nowhere'],
], ids=lambda a: ' '.join(a) or 'default')
def test_cli_tasks_matches_find_tasks(root, capsys, args):
    assert cli_output(capsys, args) == find_tasks_output(root, args)


def test_cli_tasks_matches_find_tasks_from_subfolder(root, capsys, monkeypatch):
    """Run from a subfolder, the root is found and output is the same."""
    monkeypatch.chdir(root / 'project' / 'sub')

    assert cli_output(capsys, []) == find_tasks_output(root, [])


def test_cli_tasks_matches_find_tasks_no_tasks(tmp_path, capsys, monkeypatch):
    for folder in ('plan', 'project', 'area'):
        (tmp_path / folder).mkdir()
    (tmp_path / 'project' / 'a.md').write_text('# a\n')
    (tmp_path / '.meta-notes').write_text('# meta-notes notes root\n')
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.chdir(tmp_path)

    assert cli_output(capsys, []) == find_tasks_output(tmp_path, [])
    assert cli_output(capsys, ['--status', 'all']) == \
        find_tasks_output(tmp_path, ['--status', 'all'])


def test_cli_tasks_invalid_date(root, capsys):
    code, out = cli_json(capsys, ['--date', '2026-W45'])

    assert code == 1
    assert out['ok'] is False
    assert out['error'].startswith('Invalid date: 2026-W45. Use YYYY-MM-DD,')


def test_cli_tasks_reversed_range(root, capsys):
    code, out = cli_json(capsys, ['--date', f'{FUTURE}..{PAST}'])

    assert code == 1
    assert 'start of a range' in out['error']


def test_cli_tasks_removed_option_is_usage_error(root, capsys):
    code = cli.main(['tasks', '--due-on', '2026-09-25'])

    assert code != 0
    assert '--due-on' in capsys.readouterr().err


# Tests for JSON output

def test_cli_tasks_json_fields(root, capsys):
    """Spec scenario: file, line, status, due date, and tags."""
    code, out = cli_json(capsys, ['--folder', 'project', '--all'])

    assert code == 0
    sam = [t for t in out['tasks'] if t['line'] == 3 and t['file'] == 'project/foo.md']
    assert sam == [{
        'file': 'project/foo.md',
        'line': 3,
        'text': '- [ ] #mtg Call Sam 📅 2026-10-01',
        'status': 'incomplete',
        'start': None,
        'due': '2026-10-01',
        'completed': None,
        'tags': ['meeting'],
        'section': 'ready' if date(2026, 10, 1) <= TODAY else 'future',
    }]
    assert all('category' not in t for t in out['tasks'])


def test_cli_tasks_json_section(root, capsys):
    """Spec scenario: a task that is overdue and ready is listed once, as overdue."""
    code, out = cli_json(capsys, ['--overdue', '--ready'])

    overdue = [t for t in out['tasks'] if t['text'].startswith('- [ ] Overdue')]
    assert len(overdue) == 1
    assert overdue[0]['section'] == 'overdue'
    assert [t['section'] for t in out['tasks']] == \
        sorted([t['section'] for t in out['tasks']], key=['overdue', 'ready'].index)


def test_cli_tasks_json_dates(root, capsys):
    code, out = cli_json(capsys, ['--folder', 'project/sub', '--status', 'completed', '--all'])

    assert out['tasks'] == [{
        'file': 'project/sub/bar.md',
        'line': 2,
        'text': f'+ [X] Finished 📅 {PAST} ✅ {PAST}',
        'status': 'completed',
        'start': None,
        'due': PAST,
        'completed': PAST,
        'tags': [],
        'section': 'ready',
    }]


def test_cli_tasks_json_group_by_tag_lists_task_once(tmp_path, capsys, monkeypatch):
    (tmp_path / 'a.md').write_text('- [ ] #x #y both 📅\n')
    (tmp_path / '.meta-notes').write_text('# meta-notes notes root\n')
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.chdir(tmp_path)

    code, out = cli_json(capsys, ['--undated', '--group-by', 'tag'])

    assert [t['text'] for t in out['tasks']] == ['- [ ] #x #y both 📅']
    assert out['tasks'][0]['tags'] == ['x', 'y']


def test_query_run_tasks_appear_in_report(root):
    """The JSON tasks are the tasks in the text report, in the same order."""
    lines, tasks = query.run('.', modes=['overdue', 'due', 'future', 'undated'])

    task_lines = [line for line in lines if line.lstrip().startswith(('-', '*', '+'))]
    assert [t['text'] for t in tasks] == task_lines
    assert {t['section'] for t in tasks} == {'overdue', 'due', 'future', 'undated'}


def test_query_run_later_tasks(root):
    _, without = query.run('.', modes=['all'])
    _, with_later = query.run('.', modes=['all'], later=True)

    assert not any('Someday' in t['text'] for t in without)
    assert [t['section'] for t in with_later if 'Someday' in t['text']] == ['ready']


def test_query_run_empty_root(tmp_path):
    lines, tasks = query.run(str(tmp_path))

    assert lines == ['No markdown files found.']
    assert tasks == []
