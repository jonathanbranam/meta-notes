"""
Unit tests for scripts/meta_notes/cli.py

Tests notes root resolution and output conventions.
"""

import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
repo_dir = Path(__file__).parent.parent.parent
scripts_dir = repo_dir / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import cli

SHIM = repo_dir / 'bin' / 'meta-notes'


@pytest.fixture
def notes_root(tmp_path, monkeypatch):
    """A notes root with its sentinel and PPARA folders, as the current directory."""
    for folder in ('plan', 'project', 'area', 'resource'):
        (tmp_path / folder).mkdir()
    (tmp_path / '.meta-notes').write_text('# meta-notes notes root\n')
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.chdir(tmp_path)
    return tmp_path


def run_json(capsys, argv):
    """Run the CLI with --json and return (exit code, parsed output, stderr)."""
    code = cli.main(argv + ['--json'])
    captured = capsys.readouterr()
    return code, json.loads(captured.out), captured.err


# Tests for resolve_root function

def test_resolve_root_explicit_root_without_plan_folder(tmp_path):
    """--root is used as-is even without plan/."""
    assert cli.resolve_root(str(tmp_path), None, '/') == str(tmp_path)


def test_resolve_root_explicit_root_wins_over_env(tmp_path):
    """--root takes precedence over META_NOTES_ROOT."""
    other = tmp_path / 'other'
    other.mkdir()
    assert cli.resolve_root(str(tmp_path), str(other), '/') == str(tmp_path)


def test_resolve_root_env(tmp_path):
    """META_NOTES_ROOT is used when --root is not given."""
    assert cli.resolve_root(None, str(tmp_path), '/') == str(tmp_path)


def test_resolve_root_explicit_missing_directory(tmp_path):
    """A --root that isn't a directory is an error."""
    with pytest.raises(cli.CliError, match='not a directory'):
        cli.resolve_root(str(tmp_path / 'missing'), None, '/')


def test_resolve_root_walks_up_to_sentinel(notes_root):
    """The nearest ancestor containing .meta-notes is the root."""
    nested = notes_root / 'project' / 'foo'
    nested.mkdir()
    root = cli.resolve_root(None, None, str(nested), str(notes_root))
    assert root == os.path.realpath(notes_root)


def test_resolve_root_folder_markers_alone_not_a_root(tmp_path):
    """plan/, project/, and area/ without .meta-notes are not a root."""
    for folder in ('plan', 'project', 'area'):
        (tmp_path / folder).mkdir()
    with pytest.raises(cli.CliError, match='No notes root found'):
        cli.resolve_root(None, None, str(tmp_path / 'project'), str(tmp_path))


def test_resolve_root_no_root_error_suggests_init(tmp_path):
    """The no-root error says to run meta-notes init or pass --root."""
    with pytest.raises(cli.CliError, match=r'meta-notes init.*--root'):
        cli.resolve_root(None, None, str(tmp_path), str(tmp_path))


# Tests for main function

def test_main_changes_into_root(notes_root, monkeypatch, capsys):
    """Paths are relative to the root even when run from a subfolder."""
    (notes_root / 'project' / 'foo.md').write_text('# project/foo\n')
    monkeypatch.chdir(notes_root / 'project')

    code, out, _ = run_json(capsys, ['rename', 'project/foo.md', 'bar'])

    assert code == 0
    assert out['dest'] == 'project/bar.md'
    assert (notes_root / 'project' / 'bar.md').exists()


def test_main_root_option(tmp_path, monkeypatch, capsys):
    """--root works from outside the root and without plan/."""
    (tmp_path / 'project').mkdir()
    (tmp_path / 'project' / 'foo.md').write_text('# foo\n')
    monkeypatch.chdir('/')

    code, out, _ = run_json(capsys, ['--root', str(tmp_path),
                                     'move', 'project/foo.md', 'area/foo'])

    assert code == 0
    assert out['moves'] == [['project/foo.md', 'area/foo.md']]
    assert (tmp_path / 'area' / 'foo.md').exists()


def test_main_absolute_paths_made_root_relative(notes_root, capsys):
    """Absolute paths inside the root are treated as root-relative."""
    (notes_root / 'project' / 'foo.md').write_text('# project/foo\n')

    code, out, _ = run_json(capsys, ['move', str(notes_root / 'project' / 'foo.md'),
                                     'area/foo'])

    assert code == 0
    assert out['moves'] == [['project/foo.md', 'area/foo.md']]
    assert (notes_root / 'area' / 'foo.md').read_text() == '# area/foo\n'


def test_main_no_root_found(tmp_path, monkeypatch, capsys):
    """No resolvable root is a non-zero exit with an error."""
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.chdir(tmp_path)

    code, out, err = run_json(capsys, ['tasks'])

    assert code != 0
    assert out['ok'] is False
    assert 'No notes root found' in out['error']
    assert err == ''


def test_main_json_success(notes_root, capsys):
    """--json success is one object with ok and warnings, nothing on stderr."""
    code, out, err = run_json(capsys, ['tasks'])

    assert code == 0
    assert out['ok'] is True
    assert out['warnings'] == []
    assert err == ''


def test_main_json_error(notes_root, capsys):
    """--json failure is one object with ok false and an error."""
    code, out, err = run_json(capsys, ['move', 'project/missing.md', 'area/x'])

    assert code == 1
    assert out == {'ok': False, 'error': 'Source not found: project/missing.md',
                   'warnings': []}
    assert err == ''


def test_main_json_usage_error(notes_root, capsys):
    """Argument errors are reported as JSON too."""
    code, out, err = run_json(capsys, ['move', 'only-one-arg'])

    assert code != 0
    assert out['ok'] is False
    assert 'required' in out['error']
    assert err == ''


def test_main_json_captures_library_warnings(notes_root, capsys):
    """Warnings library code prints to stderr go in the warnings array."""
    (notes_root / 'project' / 'bad.md').write_bytes(b'- [ ] \xff\xfe task\n')

    code, out, err = run_json(capsys, ['tasks'])

    assert code == 0
    assert err == ''
    assert any('Could not read' in w for w in out['warnings'])


def test_main_json_option_after_subcommand(notes_root, capsys):
    """--json and --root are accepted after the subcommand."""
    code = cli.main(['tasks', '--root', str(notes_root), '--json'])
    out = json.loads(capsys.readouterr().out)

    assert code == 0
    assert out['ok'] is True


def test_main_text_error_to_stderr(notes_root, capsys):
    """Without --json, errors go to stderr and the exit is non-zero."""
    code = cli.main(['move', 'project/missing.md', 'area/x'])
    captured = capsys.readouterr()

    assert code == 1
    assert captured.out == ''
    assert 'Source not found: project/missing.md' in captured.err


def test_main_text_success(notes_root, capsys):
    """Without --json, results are human-readable text on stdout."""
    (notes_root / 'project' / 'foo.md').write_text('# foo\n')

    code = cli.main(['move', 'project/foo.md', 'area/foo'])
    captured = capsys.readouterr()

    assert code == 0
    assert captured.out == 'Moved: project/foo.md → area/foo.md\n'
    assert captured.err == ''


# Tests for the note subcommand

DAILY = 'plan/daily/26-Q1/2026-02-13 Fri.md'


@pytest.fixture
def daily_template(notes_root):
    """The shipped daily template in resource/template/."""
    folder = notes_root / 'resource' / 'template'
    folder.mkdir()
    (folder / 'daily.md').write_bytes((repo_dir / 'templates' / 'daily.md').read_bytes())
    return folder / 'daily.md'


def test_note_json_created(daily_template, notes_root, capsys):
    code, out, err = run_json(capsys, ['note', 'daily', '2026-02-13'])

    assert code == 0
    assert err == ''
    assert out == {'ok': True, 'path': DAILY, 'exists': False, 'created': True,
                   'template': 'resource/template/daily.md', 'warnings': []}
    assert (notes_root / DAILY).read_text().startswith('# Daily Note - 2026-02-13 Fri\n')


def test_note_json_rendered(daily_template, notes_root, capsys):
    code, out, _ = run_json(capsys, ['note', 'daily', '2026-02-13', '--render'])

    assert code == 0
    assert (out['exists'], out['created']) == (False, False)
    assert not (notes_root / 'plan' / 'daily').exists()

    code, written, _ = run_json(capsys, ['note', 'daily', '2026-02-13'])
    assert (notes_root / DAILY).read_text() == out['content']


def test_note_json_existing(daily_template, notes_root, capsys):
    (notes_root / DAILY).parent.mkdir(parents=True)
    (notes_root / DAILY).write_text('# Mine\n')

    code, out, err = run_json(capsys, ['note', 'daily', '2026-02-13', '--render'])

    assert code == 0
    assert err == ''
    assert out == {'ok': True, 'path': DAILY, 'exists': True, 'created': False,
                   'template': None, 'warnings': []}
    assert (notes_root / DAILY).read_text() == '# Mine\n'


def test_note_json_invalid_date(notes_root, capsys):
    code, out, _ = run_json(capsys, ['note', 'daily', '2026-13-45'])

    assert code == 1
    assert out['error'] == 'Invalid date: 2026-13-45 (expected YYYY-MM-DD)'
    assert not (notes_root / 'plan' / 'daily').exists()


def test_note_json_warnings(notes_root, capsys):
    (notes_root / 'project' / 'template.md').write_text(
        '{{% shell exit 1 %}}\n{{% vim echo 1 %}}\n')

    code, out, _ = run_json(capsys, ['note', 'new', 'project/x'])

    assert code == 0
    assert out['warnings'] == [
        'Command failed: {{% shell exit 1 %}}',
        'project/x.md: {{% vim %}} blocks are left as text outside Vim']


def test_note_new_absolute_path(notes_root, capsys):
    code, out, _ = run_json(capsys, ['note', 'new', str(notes_root / 'area' / 'Beds')])

    assert code == 0
    assert out['path'] == 'area/Beds.md'
    assert (notes_root / 'area' / 'Beds.md').read_text() == '# area/Beds\n\n'


def test_note_new_outside_root(notes_root, capsys):
    code, out, _ = run_json(capsys, ['note', 'new', '../elsewhere/note'])

    assert code == 1
    assert 'outside the notes root' in out['error']


def test_note_new_template_option(notes_root, capsys):
    (notes_root / 'resource' / 'template').mkdir()
    (notes_root / 'resource' / 'template' / 'checklist.md').write_text('# {{note_name}}\n')

    code, out, _ = run_json(capsys, ['note', 'new', 'project/trip/Packing',
                                     '--template', 'checklist', '--render'])

    assert code == 0
    assert out['content'] == '# Packing\n'
    assert out['template'] == 'resource/template/checklist.md'


def test_note_text_prints_path(notes_root, capsys):
    for _ in range(2):
        code = cli.main(['note', 'yearly', '2026-02-13'])
        captured = capsys.readouterr()
        assert code == 0
        assert (captured.out, captured.err) == ('plan/year/2026.md\n', '')


def test_note_text_render_prints_content(notes_root, capsys):
    code = cli.main(['note', 'yearly', '2026-02-13', '--render'])
    captured = capsys.readouterr()

    assert code == 0
    assert captured.out == '# Year Plan - 2026\n\n'
    assert not (notes_root / 'plan' / 'year').exists()


def test_note_text_render_existing(notes_root, capsys):
    (notes_root / 'plan' / 'year').mkdir()
    (notes_root / 'plan' / 'year' / '2026.md').write_text('# Mine\n')

    code = cli.main(['note', 'yearly', '2026-02-13', '--render'])
    captured = capsys.readouterr()

    assert code == 0
    assert captured.out == ''
    assert captured.err == 'Note already exists: plan/year/2026.md\n'


def test_note_json_command_output_only_in_content(notes_root):
    """Command-block stdout and stderr end up in content, never on stdout."""
    (notes_root / 'project' / 'template.md').write_text(
        '# T\n'
        '{{% shell echo "{\\"ok\\": false}"; echo to-stderr >&2 %}}\n'
        '{{% python -c "print(\'from python\')" %}}\n')

    proc = subprocess.run([str(SHIM), '--json', 'note', 'new', 'project/x', '--render'],
                          capture_output=True, text=True, cwd=str(notes_root))

    assert proc.returncode == 0
    assert proc.stderr == ''
    out = json.loads(proc.stdout)
    assert out['ok'] is True
    assert out['content'] == '# T\n{"ok": false}\nto-stderr\n\nfrom python\n\n'


# Tests for the time subcommand

TIME_LOG = """# 2026-09-22

### Log

- June DMC Connect #meeting
  * start: 15:00
  * end:   15:50
- Tanul & Melissa
  * start: 16:00
  * end:   16:40
- review #horz position paper
  * start: 16:40

### Notes
"""


@pytest.fixture
def daily_note(notes_root):
    """The notes root with a 2026-09-22 daily note that has a time log."""
    folder = notes_root / 'plan' / 'daily' / '26-Q3'
    folder.mkdir(parents=True)
    (folder / '2026-09-22 Tue.md').write_text(TIME_LOG)
    return notes_root


def snapshot(root):
    """Every file under root with its contents and modification time."""
    return {p: (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file()}


def test_time_from_subfolder(daily_note, monkeypatch, capsys):
    """The day report is found from a subfolder of the notes root."""
    sub = daily_note / 'project' / 'foo'
    sub.mkdir()
    monkeypatch.chdir(sub)

    code = cli.main(['time', '--date', '2026-09-22'])
    out = capsys.readouterr().out

    assert code == 0
    assert 'File: 2026-09-22 Tue.md' in out
    assert '## Summary for 2026-09-21 to 2026-09-27' in out


def test_time_json_entry_fields(daily_note, capsys):
    """The first entry has its line, text, times, minutes, and tags."""
    code, data, _ = run_json(capsys, ['time', '--date', '2026-09-22'])

    assert code == 0
    assert data['ok'] is True
    assert data['kind'] == 'day'
    assert (data['start'], data['end']) == ('2026-09-22', '2026-09-22')
    assert data['file'] == 'plan/daily/26-Q3/2026-09-22 Tue.md'
    assert data['entries'][0] == {'kind': 'entry', 'line': 5,
                                  'text': 'June DMC Connect #meeting',
                                  'start': '15:00', 'end': '15:50',
                                  'minutes': 50, 'tags': ['meeting']}
    assert data['warnings'] == []


def test_time_json_gap(daily_note, capsys):
    """A 10-minute gap sits between its two entries."""
    _, data, _ = run_json(capsys, ['time', '--date', '2026-09-22'])

    assert data['entries'][1] == {'kind': 'gap', 'minutes': 10,
                                  'start': '15:50', 'end': '16:00'}
    assert data['entries'][2]['text'] == 'Tanul & Melissa'


def test_time_json_missing_times_null(daily_note, capsys):
    """An entry without an end has null end and minutes."""
    _, data, _ = run_json(capsys, ['time', '--date', '2026-09-22'])

    last = data['entries'][-1]
    assert last['end'] is None
    assert last['minutes'] is None


def test_time_json_report_matches_text(daily_note, capsys):
    """report is the text output without its trailing newline."""
    cli.main(['time', '--date', '2026-09-22'])
    text = capsys.readouterr().out
    _, data, _ = run_json(capsys, ['time', '--date', '2026-09-22'])

    assert data['report'] == text.removesuffix('\n')


def test_time_json_period(daily_note, capsys):
    """A month is the period report."""
    code, data, _ = run_json(capsys, ['time', '--date', '2026-09'])

    assert code == 0
    assert data['kind'] == 'period'
    assert len(data['days']) == 30
    assert data['by_tag'] == {'meeting': 50}
    assert data['report'].startswith('# Time Tracking Report\n\n'
                                     '## Summary for 2026-09-01 to 2026-09-30')


def test_time_json_invalid_date(notes_root, capsys):
    """An invalid --date is one JSON error object naming the value."""
    code, data, err = run_json(capsys, ['time', '--date', 'next-week'])

    assert code == 1
    assert data['ok'] is False
    assert 'next-week' in data['error']
    assert err == ''


def test_time_missing_note(notes_root, capsys):
    """A day without a daily note fails with its path."""
    code = cli.main(['time', '--date', '2026-09-22'])

    assert code == 1
    assert ('Daily note not found: plan/daily/26-Q3/2026-09-22 Tue.md'
            in capsys.readouterr().err)


def test_time_read_only(daily_note, capsys):
    """The time report changes no file in the notes root."""
    before = snapshot(daily_note)

    cli.main(['time', '--date', '2026-09-22'])
    capsys.readouterr()
    run_json(capsys, ['time', '--date', '2026-09'])

    assert snapshot(daily_note) == before


def test_time_shim(daily_note):
    """The shim runs the time report."""
    proc = subprocess.run([str(SHIM), '--json', 'time', '--date', '2026-09-22'],
                          capture_output=True, text=True, cwd=str(daily_note))

    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert json.loads(proc.stdout)['entries'][0]['minutes'] == 50


# Tests for git_commit function

def git(cwd, *args):
    """Run git in cwd with a throwaway identity."""
    subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=t@example.com',
                    *args], cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def plugin_repo(tmp_path):
    """A git repository with one commit, standing in for the plugin checkout."""
    repo = tmp_path / 'plugin'
    repo.mkdir()
    (repo / 'file.txt').write_text('one\n')
    git(repo, 'init', '-q')
    git(repo, 'add', 'file.txt')
    git(repo, 'commit', '-q', '-m', 'initial')
    return repo


def head(repo):
    return subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=repo,
                          capture_output=True, text=True, check=True).stdout.strip()


def test_git_commit_clean(plugin_repo):
    """A clean checkout reports its short hash and not dirty."""
    assert cli.git_commit(str(plugin_repo)) == (head(plugin_repo), False)


def test_git_commit_dirty(plugin_repo):
    """A modified tracked file makes the checkout dirty."""
    (plugin_repo / 'file.txt').write_text('two\n')

    assert cli.git_commit(str(plugin_repo)) == (head(plugin_repo), True)


def test_git_commit_untracked_not_dirty(plugin_repo):
    """Untracked files alone don't make the checkout dirty."""
    (plugin_repo / 'Session.vim').write_text('')

    assert cli.git_commit(str(plugin_repo)) == (head(plugin_repo), False)


def test_git_commit_inside_other_repo(plugin_repo):
    """A plugin directory inside another repository reports no commit."""
    nested = plugin_repo / 'bundle' / 'meta-notes'
    nested.mkdir(parents=True)

    assert cli.git_commit(str(nested)) == (None, False)


def test_git_commit_not_a_repo(tmp_path):
    """A directory outside any repository reports no commit."""
    assert cli.git_commit(str(tmp_path)) == (None, False)


def test_git_commit_git_missing(plugin_repo, monkeypatch):
    """No commit is reported when git can't be run."""
    monkeypatch.setenv('PATH', '')

    assert cli.git_commit(str(plugin_repo)) == (None, False)


# Tests for --version

def test_version_text(tmp_path, monkeypatch, capsys):
    """--version prints the name, version, and commit, with no notes root."""
    monkeypatch.setattr(cli, 'git_commit', lambda d: ('abc1234', False))
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.chdir(tmp_path)

    assert cli.main(['--version']) == 0
    captured = capsys.readouterr()
    assert captured.out == f'meta-notes {cli.__version__} (abc1234)\n'
    assert captured.err == ''


def test_version_text_dirty(monkeypatch, capsys):
    """A dirty checkout is marked -dirty."""
    monkeypatch.setattr(cli, 'git_commit', lambda d: ('abc1234', True))

    cli.main(['--version'])

    assert capsys.readouterr().out == f'meta-notes {cli.__version__} (abc1234-dirty)\n'


def test_version_text_no_commit(monkeypatch, capsys):
    """Without a commit, only the name and version are printed."""
    monkeypatch.setattr(cli, 'git_commit', lambda d: (None, False))

    cli.main(['--version'])

    captured = capsys.readouterr()
    assert captured.out == f'meta-notes {cli.__version__}\n'
    assert captured.err == ''


def test_version_json(tmp_path, monkeypatch, capsys):
    """--version --json reports the fields and keeps stderr empty."""
    monkeypatch.setattr(cli, 'git_commit', lambda d: (None, False))
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.chdir(tmp_path)

    code, out, err = run_json(capsys, ['--version'])

    assert code == 0
    assert out == {'ok': True, 'version': cli.__version__, 'commit': None,
                   'dirty': False, 'warnings': []}
    assert err == ''


def test_version_with_subcommand(notes_root, monkeypatch, capsys):
    """--version after a subcommand reports the version and runs nothing."""
    monkeypatch.setattr(cli, 'git_commit', lambda d: (None, False))
    (notes_root / 'project' / 'foo.md').write_text('# Foo\n')

    code, out, _ = run_json(capsys, ['archive', 'project/foo.md', '--version'])

    assert code == 0
    assert out['version'] == cli.__version__
    assert (notes_root / 'project' / 'foo.md').exists()


def test_version_matches_semver():
    """The version is MAJOR.MINOR.PATCH."""
    assert re.fullmatch(r'\d+\.\d+\.\d+', cli.__version__)


# Tests for bin/meta-notes shim

def test_shim_json_output(notes_root):
    """The shim runs the CLI and keeps stderr empty under --json."""
    (notes_root / 'project' / 'foo.md').write_text('- [ ] Task 📅 2000-01-01\n')

    proc = subprocess.run([str(SHIM), '--root', str(notes_root), '--json', 'tasks'],
                          capture_output=True, text=True, cwd='/')

    assert proc.returncode == 0
    assert proc.stderr == ''
    assert json.loads(proc.stdout)['tasks'][0]['file'] == 'project/foo.md'


def test_shim_error_exit_code(notes_root):
    """The shim passes through a non-zero exit on failure."""
    proc = subprocess.run([str(SHIM), '--json', 'archive', 'plan'],
                          capture_output=True, text=True, cwd=str(notes_root))

    assert proc.returncode == 1
    assert json.loads(proc.stdout)['ok'] is False


def test_shim_not_shadowed_by_notes_root_modules(notes_root):
    """A tasks.py in the notes root doesn't replace the CLI's modules."""
    (notes_root / 'tasks.py').write_text('raise SystemExit("shadowed")\n')

    proc = subprocess.run([str(SHIM), '--json', 'tasks'],
                          capture_output=True, text=True, cwd=str(notes_root))

    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_shim_version_outside_notes_root(tmp_path):
    """The shim reports the version from a directory with no notes root."""
    env = {**os.environ, 'HOME': str(tmp_path)}
    env.pop('META_NOTES_ROOT', None)

    proc = subprocess.run([str(SHIM), '--version'], capture_output=True,
                          text=True, cwd=str(tmp_path), env=env)

    assert proc.returncode == 0
    assert re.match(r'meta-notes \d+\.\d+\.\d+', proc.stdout)
    assert proc.stderr == ''


# Tests for the task update subcommand

@pytest.fixture
def task_note(notes_root):
    """project/foo.md with a task on line 3."""
    path = notes_root / 'project' / 'foo.md'
    path.write_text('# project/foo\n\n- [ ] call Sam 📅 2026-09-22\n')
    return path


TASK = '- [ ] call Sam 📅 2026-09-22'


@pytest.mark.parametrize('args, message', [
    ([], 'at least one of'),
    (['--status', 'done'], 'invalid choice'),
    (['--due', '2026-02-30'], 'invalid value'),
    (['--due', '20260930'], 'invalid value'),
    (['--due', 'someday'], 'invalid value'),
    (['--start', 'undated'], 'invalid value'),
    (['--add-tag', 'two words'], 'invalid tag'),
    (['--remove-tag', '#a.b'], 'invalid tag'),
    (['--add-tag', 'later', '--remove-tag', '#Later'], 'both'),
    (['--add-tag', 'mtg', '--remove-tag', 'meeting'], 'both'),
])
def test_task_update_usage_errors(task_note, capsys, args, message):
    """Invalid options fail before the file is read, and nothing is written."""
    before = task_note.read_bytes()
    code, out, _ = run_json(
        capsys, ['task', 'update', 'project/foo.md:3', '--expect', TASK] + args)
    assert code == 1
    assert out['ok'] is False
    assert message in out['error']
    assert task_note.read_bytes() == before


def test_task_update_expect_required(task_note, capsys):
    code, out, _ = run_json(capsys, ['task', 'update', 'project/foo.md:3',
                                     '--status', 'x'])
    assert code == 1
    assert '--expect' in out['error']


@pytest.mark.parametrize('target', ['project/foo.md', 'project/foo.md:',
                                    'project/foo.md:x', ':3'])
def test_task_update_bad_target(task_note, capsys, target):
    code, out, _ = run_json(capsys, ['task', 'update', target,
                                     '--expect', TASK, '--status', 'x'])
    assert code == 1
    assert '<file>:<line>' in out['error']


def test_task_update_target_split_on_last_colon(notes_root, capsys):
    """A path containing : is split at the last one."""
    path = notes_root / 'project' / 'a:b.md'
    path.write_text(TASK + '\n')
    code, out, _ = run_json(capsys, ['task', 'update', 'project/a:b.md:1',
                                     '--expect', TASK, '--status', '-'])
    assert code == 0
    assert out['file'] == 'project/a:b.md'
    assert path.read_text() == '- [-] call Sam 📅 2026-09-22\n'


def test_task_update_absolute_path(task_note, notes_root, capsys):
    code, out, _ = run_json(capsys, ['task', 'update', f'{task_note}:3',
                                     '--expect', TASK, '--status', '-'])
    assert code == 0
    assert out['file'] == 'project/foo.md'


def test_task_update_json_success(notes_root, capsys):
    path = notes_root / 'project' / 'foo.md'
    path.write_text('# project/foo\n\n- [ ] call Sam 📅 2000-01-01\n')
    code, out, _ = run_json(capsys, ['task', 'update', 'project/foo.md:3',
                                     '--expect', '- [ ] call Sam 📅 2000-01-01',
                                     '--status', 'x'])
    assert code == 0
    assert out == {
        'ok': True, 'file': 'project/foo.md', 'line': 3,
        'old': '- [ ] call Sam 📅 2000-01-01',
        'new': f'- [x] call Sam 📅 2000-01-01 ✅ {date.today().isoformat()}',
        'changed': True, 'warnings': []}
    assert path.read_text().splitlines()[2] == out['new']


def test_task_update_json_mismatch(task_note, capsys):
    before = task_note.read_bytes()
    code, out, _ = run_json(capsys, ['task', 'update', 'project/foo.md:3',
                                     '--expect', '- [ ] call Sam 📅 2026-09-21',
                                     '--status', 'x'])
    assert code == 1
    assert out['ok'] is False
    assert out['current'] == TASK
    assert task_note.read_bytes() == before


def test_task_update_json_warning(task_note, capsys):
    code, out, _ = run_json(capsys, ['task', 'update', 'project/foo.md:3',
                                     '--expect', TASK, '--due', 'none'])
    assert code == 0
    assert out['new'] == '- [ ] call Sam'
    assert any('no longer a task' in w for w in out['warnings'])


def test_task_update_text_output(task_note, capsys):
    code = cli.main(['task', 'update', 'project/foo.md:3', '--expect', TASK,
                     '--status', '-'])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.splitlines() == [
        'project/foo.md:3', f'- {TASK}', '+ - [-] call Sam 📅 2026-09-22']


def test_task_update_text_unchanged(task_note, capsys):
    code = cli.main(['task', 'update', 'project/foo.md:3', '--expect', TASK,
                     '--status', ' '])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == 'project/foo.md:3 unchanged\n'


def test_task_update_text_mismatch(task_note, capsys):
    code = cli.main(['task', 'update', 'project/foo.md:3', '--expect', 'x',
                     '--status', '-'])
    captured = capsys.readouterr()
    assert code == 1
    assert TASK in captured.err


def test_task_update_not_a_checkbox(task_note, capsys):
    code, out, _ = run_json(capsys, ['task', 'update', 'project/foo.md:1',
                                     '--expect', '# project/foo', '--status', 'x'])
    assert code == 1
    assert 'not a checkbox' in out['error']
    assert 'current' not in out


# Tests for the conventions command

def test_conventions_outside_notes_root(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.chdir(tmp_path)

    code = cli.main(['conventions'])

    out = capsys.readouterr().out
    assert code == 0
    assert out.startswith('# meta-notes conventions\n')
    assert '--expect <text>' in out


def test_conventions_json(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.chdir(tmp_path)

    code, data, err = run_json(capsys, ['conventions'])

    assert code == 0
    assert data['ok'] is True
    assert data['version'] == cli.__version__
    assert data['text'].startswith('# meta-notes conventions\n')
    assert err == ''


# Tests for the ceremony status command

def _write_note(root, path, text):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def test_ceremony_status_all_four(notes_root, capsys):
    _write_note(notes_root, 'plan/daily/26-Q3/2026-09-25 Fri.md',
                '- [x] plan complete\n- [ ] shutdown complete\n')
    _write_note(notes_root, 'plan/week/26-Q3/2026-09-21.md',
                '- [x] review complete ✅ 2026-09-25\n- [ ] plan complete\n')

    code = cli.main(['ceremony', 'status', '--date', '2026-09-25'])

    assert code == 0
    assert capsys.readouterr().out.splitlines() == [
        'daily-plan:     done',
        'daily-shutdown: not done',
        'weekly-review:  done 2026-09-25',
        'weekly-plan:    not done',
    ]


def test_ceremony_status_missing_weekly_note(notes_root, capsys):
    _write_note(notes_root, 'plan/daily/26-Q3/2026-09-25 Fri.md',
                '- [ ] plan complete\n- [ ] shutdown complete\n')

    code, data, _ = run_json(capsys, ['ceremony', 'status', '--date',
                                      '2026-09-25'])

    assert code == 0
    weekly = [c for c in data['ceremonies'] if c['name'].startswith('weekly')]
    assert len(weekly) == 2
    assert all(not c['note_exists'] and not c['done'] for c in weekly)


@pytest.mark.parametrize('value', ['2026-09-21..2026-09-25', '2026-09',
                                   '2026-02-30', 'today'])
def test_ceremony_status_rejects_non_day(notes_root, capsys, value):
    code, data, _ = run_json(capsys, ['ceremony', 'status', '--date', value])

    assert code == 1
    assert data['ok'] is False
    assert 'expected YYYY-MM-DD' in data['error']


def test_ceremony_status_json(notes_root, capsys):
    _write_note(notes_root, 'plan/daily/26-Q3/2026-09-25 Fri.md',
                '- [ ] plan complete\n- [x] shutdown complete ✅ 2026-09-25\n')

    code, data, _ = run_json(capsys, ['ceremony', 'status', '--date',
                                      '2026-09-25'])

    assert code == 0
    assert data['date'] == '2026-09-25'
    assert data['week_start'] == '2026-09-21'
    shutdown = [c for c in data['ceremonies'] if c['name'] == 'daily-shutdown'][0]
    assert shutdown == {'name': 'daily-shutdown',
                        'note': 'plan/daily/26-Q3/2026-09-25 Fri.md',
                        'note_exists': True, 'marker_present': True,
                        'done': True, 'completed': '2026-09-25'}


def test_ceremony_status_writes_nothing(notes_root, capsys):
    before = sorted(p for p in notes_root.rglob('*'))

    assert cli.main(['ceremony', 'status', '--date', '2026-09-25']) == 0

    assert sorted(p for p in notes_root.rglob('*')) == before


# Tests for the projects command

def test_projects_only_warnings(notes_root, capsys):
    _write_note(notes_root, 'project/done.md', '# Done\n\n- status: done\n')
    _write_note(notes_root, 'project/stale.md', '# Stale\n')

    code = cli.main(['projects', '--warnings'])

    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert len(out) == 1
    assert out[0].startswith('project/stale.md  active')


def test_projects_json(notes_root, capsys):
    _write_note(notes_root, 'project/make-bread.md',
                '# Make Bread\n\n- tag: make-bread\n')

    code, data, _ = run_json(capsys, ['projects'])

    assert code == 0
    [entry] = data['projects']
    assert entry['path'] == 'project/make-bread.md'
    assert entry['tag'] == 'make-bread'
    assert entry['last_review'] is None
    assert 'review-overdue' in entry['warnings']
    assert set(entry) == {'path', 'home', 'status', 'tag', 'last_review',
                          'latest_date', 'open_tasks', 'completed_tasks',
                          'warnings'}
