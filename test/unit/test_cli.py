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
