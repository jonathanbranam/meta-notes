"""
Unit tests for bin/meta-notes

Tests which interpreter the shim runs: the notes root's .venv/bin/python3
when it's executable, otherwise python3 on PATH. Both are stub scripts that
record they were called, so no real Python runs.
"""

import os
import subprocess
from pathlib import Path

import pytest

repo_dir = Path(__file__).parent.parent.parent
SHIM = repo_dir / 'bin' / 'meta-notes'

STUB = '#!/bin/sh\necho "$@" > "{marker}"\n'


def write_stub(path, marker):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(STUB.format(marker=marker))
    path.chmod(0o755)


@pytest.fixture
def setup(tmp_path):
    """
    A notes root at tmp_path/notes with a stub .venv/bin/python3, and a stub
    python3 first on PATH. HOME is tmp_path.
    """
    root = tmp_path / 'notes'
    (root / 'project' / 'foo').mkdir(parents=True)
    (root / '.meta-notes').write_text('# meta-notes notes root\n')
    write_stub(root / '.venv' / 'bin' / 'python3', tmp_path / 'venv-ran')
    write_stub(tmp_path / 'bin' / 'python3', tmp_path / 'system-ran')

    env = {**os.environ, 'HOME': str(tmp_path),
           'PATH': f"{tmp_path / 'bin'}{os.pathsep}{os.environ['PATH']}"}
    env.pop('META_NOTES_ROOT', None)
    return root, env


def run(args, cwd, env):
    proc = subprocess.run([str(SHIM), *args], cwd=str(cwd), env=env,
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return proc


def ran(tmp_path):
    """Which stub ran: 'venv', 'system', or both, as a set."""
    return {name for name in ('venv', 'system')
            if (tmp_path / f'{name}-ran').exists()}


# Tests for the interpreter choice

def test_shim_virtualenv_present_from_subdirectory(tmp_path, setup):
    """Run from inside the root, the virtualenv's python3 runs the CLI."""
    root, env = setup

    run(['calendar'], root / 'project' / 'foo', env)

    assert ran(tmp_path) == {'venv'}
    args = (tmp_path / 'venv-ran').read_text().split()
    assert args == [str(repo_dir / 'scripts' / 'meta_notes' / '__main__.py'),
                    'calendar']


@pytest.mark.parametrize('form', ['separate', 'equals'])
def test_shim_root_passed_after_subcommand(tmp_path, setup, form):
    """--root after the subcommand, from outside the root, finds the virtualenv."""
    root, env = setup
    outside = tmp_path / 'elsewhere'
    outside.mkdir()
    root_args = (['--root', str(root)] if form == 'separate'
                 else [f'--root={root}'])

    run(['calendar', *root_args, '--json'], outside, env)

    assert ran(tmp_path) == {'venv'}


def test_shim_meta_notes_root_env(tmp_path, setup):
    """META_NOTES_ROOT finds the virtualenv from outside the root."""
    root, env = setup
    outside = tmp_path / 'elsewhere'
    outside.mkdir()

    run(['tasks'], outside, {**env, 'META_NOTES_ROOT': str(root)})

    assert ran(tmp_path) == {'venv'}


def test_shim_root_option_wins_over_env(tmp_path, setup):
    """--root is used before META_NOTES_ROOT."""
    root, env = setup
    other = tmp_path / 'other'
    other.mkdir()

    run(['tasks', '--root', str(root)], tmp_path, {**env, 'META_NOTES_ROOT': str(other)})

    assert ran(tmp_path) == {'venv'}


def test_shim_broken_virtualenv_falls_back(tmp_path, setup):
    """A dangling .venv/bin/python3 link falls back to python3 on PATH."""
    root, env = setup
    venv_python = root / '.venv' / 'bin' / 'python3'
    venv_python.unlink()
    venv_python.symlink_to(tmp_path / 'removed' / 'python3')

    run(['tasks'], root, env)

    assert ran(tmp_path) == {'system'}


def test_shim_init_ignores_virtualenv(tmp_path, setup):
    """init runs on python3 on PATH even with a virtualenv."""
    root, env = setup

    run(['init', '--force'], root, env)

    assert ran(tmp_path) == {'system'}


def test_shim_init_after_root_option(tmp_path, setup):
    """init is found as the command after --root and its value."""
    root, env = setup

    run(['--root', str(root), 'init'], tmp_path, env)

    assert ran(tmp_path) == {'system'}


def test_shim_no_virtualenv_falls_back(tmp_path, setup):
    """Without .venv, python3 on PATH runs the CLI."""
    root, env = setup
    (root / '.venv' / 'bin' / 'python3').unlink()

    run(['tasks'], root, env)

    assert ran(tmp_path) == {'system'}


def test_shim_search_stops_after_home(tmp_path, setup):
    """A notes root above $HOME isn't found by the upward search."""
    root, env = setup
    home = root / 'project' / 'foo'

    run(['tasks'], home, {**env, 'HOME': str(home)})

    assert ran(tmp_path) == {'system'}


def test_shim_no_root_falls_back(tmp_path, setup):
    """Outside any notes root, python3 on PATH runs the CLI."""
    _, env = setup

    run(['--version'], tmp_path, env)

    assert ran(tmp_path) == {'system'}
