"""
Unit tests for scripts/meta_notes/root.py

Tests the bounded upward search for the .meta-notes sentinel.
"""

import os
import sys
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes.root import SENTINEL, find_root


def make_root(path):
    """Create a notes root sentinel in path and return path."""
    path.mkdir(parents=True, exist_ok=True)
    (path / SENTINEL).write_text('# meta-notes notes root\n')
    return path


@pytest.fixture
def locked(tmp_path):
    """Yield a function that removes write permission; restores it after."""
    changed = []

    def lock(path):
        path.chmod(0o555)
        changed.append(path)

    yield lock
    for path in changed:
        path.chmod(0o755)


# Tests for find_root function

def test_find_root_start_is_root(tmp_path):
    """The start directory itself is checked first."""
    make_root(tmp_path)
    assert find_root(str(tmp_path), None) == os.path.realpath(tmp_path)


def test_find_root_walks_up(tmp_path):
    """The nearest ancestor containing the sentinel is found."""
    make_root(tmp_path)
    nested = tmp_path / 'project' / 'foo'
    nested.mkdir(parents=True)
    assert find_root(str(nested), str(tmp_path)) == os.path.realpath(tmp_path)


def test_find_root_nearest_wins(tmp_path):
    """With sentinels at two levels, the nearest one is returned."""
    make_root(tmp_path)
    inner = make_root(tmp_path / 'inner')
    assert find_root(str(inner), None) == os.path.realpath(inner)


def test_find_root_folder_markers_ignored(tmp_path):
    """plan/, project/, and area/ without a sentinel are not a root."""
    for folder in ('plan', 'project', 'area'):
        (tmp_path / folder).mkdir()
    assert find_root(str(tmp_path / 'project'), str(tmp_path)) is None


def test_find_root_sentinel_directory_ignored(tmp_path):
    """A directory named .meta-notes is not a sentinel."""
    (tmp_path / SENTINEL).mkdir()
    assert find_root(str(tmp_path), str(tmp_path)) is None


def test_find_root_stops_after_home(tmp_path):
    """A sentinel above $HOME is not found."""
    make_root(tmp_path)
    home = tmp_path / 'home'
    start = home / 'notes'
    start.mkdir(parents=True)
    assert find_root(str(start), str(home)) is None


def test_find_root_home_itself_checked(tmp_path):
    """$HOME itself can be a notes root."""
    home = make_root(tmp_path / 'home')
    start = home / 'project'
    start.mkdir()
    assert find_root(str(start), str(home)) == os.path.realpath(home)


def test_find_root_home_through_symlink(tmp_path):
    """$HOME given through a symlink still stops the search."""
    make_root(tmp_path)
    home = tmp_path / 'real-home'
    (home / 'notes').mkdir(parents=True)
    link = tmp_path / 'home-link'
    link.symlink_to(home)
    assert find_root(str(home / 'notes'), str(link)) is None


def test_find_root_stops_at_non_writable_directory(tmp_path, locked):
    """A directory without write permission ends the search, unchecked."""
    root = make_root(tmp_path / 'a')
    start = root / 'b'
    start.mkdir()
    locked(root)
    assert find_root(str(start), str(tmp_path)) is None


def test_find_root_non_writable_start(tmp_path, locked):
    """A non-writable start directory ends the search immediately."""
    make_root(tmp_path)
    start = tmp_path / 'b'
    start.mkdir()
    locked(start)
    assert find_root(str(start), str(tmp_path)) is None


def test_find_root_no_home_bound(tmp_path):
    """Without $HOME the search still finds an ancestor root."""
    make_root(tmp_path)
    nested = tmp_path / 'a' / 'b'
    nested.mkdir(parents=True)
    assert find_root(str(nested), None) == os.path.realpath(tmp_path)


def test_find_root_none_found(tmp_path):
    """No sentinel anywhere up to $HOME returns None."""
    assert find_root(str(tmp_path), str(tmp_path)) is None
