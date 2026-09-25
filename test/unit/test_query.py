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
from notes import calculate_week_end

FIND_TASKS = scripts_dir / 'find_tasks.py'

TODAY = date.today()
PAST = (TODAY - timedelta(days=3)).isoformat()
FUTURE = (TODAY + timedelta(days=30)).isoformat()


@pytest.fixture
def root(tmp_path, monkeypatch):
    """A notes root with tasks of every status, date, and folder."""
    files = {
        'plan/daily/today.md': [
            '# today',
            f'- [ ] Overdue 📆 {PAST}',
            f'- [x] Done ✅ {PAST}',
            '- [>] Moved',
        ],
        'project/foo.md': [
            '# project/foo',
            '',
            '- [ ] Call Sam 📆 2026-10-01',
            f'- [ ] Later 🛫 {FUTURE}',
            '  - [/] Nested in progress',
            '- [-] Dropped',
        ],
        'project/sub/bar.md': [
            '* [ ] No date',
            f'+ [X] Finished 📆 {PAST} ✅ {PAST}',
        ],
        'area/home.md': [
            f'- [ ] Fix sink 🗓 {FUTURE}',
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
    ['--folder', 'project', '--status', 'all'],
    ['--status', 'all'],
    ['--status', 'completed'],
    ['--status', 'rescheduled'],
    ['--status', 'canceled'],
    ['--due-on', '2026-10-01'],
    ['--due-by', TODAY.isoformat()],
    ['--due-between', PAST, FUTURE],
    ['--due-between', PAST, FUTURE, '--status', 'all', '--condensed'],
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
    code, out = cli_json(capsys, ['--due-on', '2026-13-01'])

    assert code == 1
    assert out['ok'] is False
    assert out['error'] == 'Invalid date format: 2026-13-01. Use YYYY-MM-DD format.'


def test_cli_tasks_reversed_range(root, capsys):
    code, out = cli_json(capsys, ['--due-between', FUTURE, PAST])

    assert code == 1
    assert out['error'] == 'Start date must be before or equal to end date'


# Tests for JSON output

def test_cli_tasks_json_fields(root, capsys):
    """Spec scenario: file, line, status, and due date."""
    code, out = cli_json(capsys, ['--folder', 'project'])

    assert code == 0
    assert out['tasks'][0] == {
        'file': 'project/foo.md',
        'line': 3,
        'text': '- [ ] Call Sam 📆 2026-10-01',
        'status': 'incomplete',
        'start': None,
        'due': '2026-10-01',
        'completed': None,
    }


def test_cli_tasks_json_filtered_same_tasks_as_text(root, capsys):
    code, out = cli_json(capsys, ['--status', 'all'])

    assert [(t['file'], t['line']) for t in out['tasks']] == [
        ('area/home.md', 1),
        ('plan/daily/today.md', 2),
        ('plan/daily/today.md', 3),
        ('plan/daily/today.md', 4),
        ('project/foo.md', 3),
        ('project/foo.md', 4),
        ('project/foo.md', 5),
        ('project/foo.md', 6),
        ('project/sub/bar.md', 1),
        ('project/sub/bar.md', 2),
    ]
    assert [t['status'] for t in out['tasks']][1:4] == [
        'incomplete', 'completed', 'rescheduled']
    assert 'category' not in out['tasks'][0]


def test_cli_tasks_json_dates(root, capsys):
    code, out = cli_json(capsys, ['--folder', 'project/sub', '--status', 'completed'])

    assert out['tasks'] == [{
        'file': 'project/sub/bar.md',
        'line': 2,
        'text': f'+ [X] Finished 📆 {PAST} ✅ {PAST}',
        'status': 'completed',
        'start': None,
        'due': PAST,
        'completed': PAST,
    }]


def test_cli_tasks_json_default_report_categories(root, capsys):
    """Without filters, tasks carry the report category in report order."""
    sam_is_current = date(2026, 10, 1) <= calculate_week_end(TODAY)
    sam = ('past_or_current' if sam_is_current else 'future', 'project/foo.md', 3)

    code, out = cli_json(capsys, [])

    assert code == 0
    assert [(t['category'], t['file'], t['line']) for t in out['tasks']] == sorted(
        [('past_or_current', 'plan/daily/today.md', 2),
         ('future', 'area/home.md', 1),
         ('future', 'project/foo.md', 4),
         sam,
         ('no_date', 'project/foo.md', 5),
         ('no_date', 'project/sub/bar.md', 1)],
        key=lambda t: (query.CATEGORIES.index(t[0]), t[1], t[2]))


def test_query_run_tasks_appear_in_report(root):
    """The JSON tasks are the tasks in the text report."""
    lines, tasks = query.run('.')

    task_lines = [line for line in lines if line.lstrip().startswith(('-', '*', '+'))]
    assert [t['text'] for t in tasks] == task_lines


def test_query_run_empty_root(tmp_path):
    lines, tasks = query.run(str(tmp_path))

    assert lines == ['No markdown files found.']
    assert tasks == []
