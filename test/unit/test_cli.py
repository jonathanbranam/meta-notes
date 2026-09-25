"""
Unit tests for scripts/meta_notes/cli.py

Tests notes root resolution and output conventions.
"""

import json
import os
import subprocess
import sys
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
    """A notes root with plan/, project/, and area/, as the current directory."""
    for folder in ('plan', 'project', 'area', 'resource'):
        (tmp_path / folder).mkdir()
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
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


def test_resolve_root_walks_up(notes_root):
    """The nearest ancestor with plan/, project/, and area/ is the root."""
    nested = notes_root / 'project' / 'foo'
    nested.mkdir()
    assert cli.resolve_root(None, None, str(nested)) == str(notes_root)


def test_resolve_root_walk_requires_all_markers(tmp_path):
    """A directory with only project/ and area/ is not a root."""
    (tmp_path / 'project').mkdir()
    (tmp_path / 'area').mkdir()
    with pytest.raises(cli.CliError, match='No notes root found'):
        cli.resolve_root(None, None, str(tmp_path / 'project'))


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


# Tests for bin/meta-notes shim

def test_shim_json_output(notes_root):
    """The shim runs the CLI and keeps stderr empty under --json."""
    (notes_root / 'project' / 'foo.md').write_text('- [ ] Task\n')

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
