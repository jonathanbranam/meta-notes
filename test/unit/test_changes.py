"""
Unit tests for scripts/meta_notes/changes.py

Tests run against a temporary git repository with fixed commit dates.
"""

import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import changes

pytestmark = pytest.mark.skipif(shutil.which('git') is None,
                                reason='git is not installed')

TODAY = date(2026, 9, 25)
WEEK = '2026-09-21..2026-09-25'


def git(root, *args, env=None):
    """Run git in root and return its stdout."""
    result = subprocess.run(
        ['git', '-C', str(root), '-c', 'user.name=Test',
         '-c', 'user.email=test@example.com', *args],
        capture_output=True, text=True, check=True,
        env=os.environ | (env or {}))
    return result.stdout


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A notes root that is the top level of a new git repository."""
    root = tmp_path / 'notes'
    root.mkdir()
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
        monkeypatch.delenv(key, raising=False)
    git(root, 'init', '-q')
    (root / '.meta-notes').write_text('# meta-notes notes root\n')
    return root


def write(root, files):
    """Write each {path: text}, creating folders."""
    for path, text in files.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)


def commit(root, when, write_files=None, moves=None, deletes=None):
    """
    Commit file writes, then moves, then deletes, dated when.

    Args:
        root: The repository.
        when: ISO 8601 date and time with offset, for author and committer.
        write_files: {path: text} to write.
        moves: [(old, new)] to git mv.
        deletes: [path] to git rm.
    """
    write(root, write_files or {})
    git(root, 'add', '-A')
    for old, new in moves or []:
        (root / new).parent.mkdir(parents=True, exist_ok=True)
        git(root, 'mv', old, new)
    for path in deletes or []:
        git(root, 'rm', '-q', path)
    git(root, 'commit', '-q', '--allow-empty', '-m', when,
        env={'GIT_AUTHOR_DATE': when, 'GIT_COMMITTER_DATE': when})


def run(root, date_text=WEEK, today=TODAY):
    return changes.run(str(root), date_text, today)


def entries(root, date_text=WEEK, today=TODAY):
    """The change entries, keyed by path."""
    _, data = run(root, date_text, today)
    return {c['path']: c for c in data['changes']}


# Tests for the test repository helper

def test_commit_helper_sets_author_date(repo):
    commit(repo, '2026-09-23T10:00:00-07:00', {'area/health.md': 'a\n'})

    assert git(repo, 'log', '--format=%aI').strip() == '2026-09-23T10:00:00-07:00'


# Tests for run: errors

def test_run_not_a_git_repository(tmp_path):
    with pytest.raises(ValueError, match='not a git repository'):
        run(tmp_path)


def test_run_root_below_top_level(repo):
    (repo / 'sub').mkdir()

    with pytest.raises(ValueError, match='must be the top level'):
        run(repo / 'sub')


def test_run_invalid_date(repo):
    with pytest.raises(ValueError, match='Invalid date: next-week'):
        run(repo, 'next-week')


# Tests for run: committed changes in the period

def test_run_commit_inside_week(repo):
    commit(repo, '2026-09-19T10:00:00-07:00', {'area/health.md': 'a\n'})
    commit(repo, '2026-09-23T10:00:00-07:00', {'area/health.md': 'a\nb\n'})

    assert list(entries(repo)) == ['area/health.md']


def test_run_commit_outside_week(repo):
    commit(repo, '2026-09-19T10:00:00-07:00', {'area/health.md': 'a\n'})
    commit(repo, '2026-09-26T10:00:00-07:00', {'area/health.md': 'a\nb\n'})

    assert entries(repo) == {}


def test_run_author_timezone_decides_day(repo):
    # 2026-09-26 06:30 in UTC
    commit(repo, '2026-09-25T23:30:00-07:00', {'area/health.md': 'a\n'})

    assert list(entries(repo, '2026-09-25', today=date(2026, 9, 27))) == [
        'area/health.md']
    assert entries(repo, '2026-09-26', today=date(2026, 9, 27)) == {}


def test_run_author_timezone_ahead_of_utc(repo):
    """A commit early on START, well ahead of UTC, is still found."""
    commit(repo, '2026-09-21T00:30:00+14:00', {'area/health.md': 'a\n'})

    assert list(entries(repo)) == ['area/health.md']


def test_run_path_with_space(repo):
    commit(repo, '2026-09-22T10:00:00-07:00',
           {'project/kitchen remodel/Home Note.md': 'a\n'})
    commit(repo, '2026-09-23T10:00:00-07:00',
           {'project/kitchen remodel/Home Note.md': 'a\nb\n'},
           moves=[('project/kitchen remodel/Home Note.md',
                   'archive/project/kitchen remodel/Home Note.md')])

    found = entries(repo)

    assert list(found) == ['archive/project/kitchen remodel/Home Note.md']
    assert found['archive/project/kitchen remodel/Home Note.md']['added'] == 2


# Tests for run: one entry per note

def test_run_non_note_files_ignored(repo):
    commit(repo, '2026-09-23T10:00:00-07:00', {
        'project/kitchen/plan.pdf': 'pdf\n',
        'templates/daily.md': '# daily\n',
        'project/kitchen/Home.md': '# Kitchen\n',
    })

    assert list(entries(repo)) == ['project/kitchen/Home.md']


def test_run_archived_note_listed(repo):
    commit(repo, '2026-09-18T10:00:00-07:00', {'archive/project/trip.md': 'a\n'})
    commit(repo, '2026-09-23T10:00:00-07:00',
           {'archive/project/trip.md': 'a\nb\n'})

    assert entries(repo)['archive/project/trip.md']['kind'] == 'modified'


def test_run_several_edits_to_one_note(repo):
    commit(repo, '2026-09-18T10:00:00-07:00',
           {'project/kitchen/Home.md': 'old\n'})
    commit(repo, '2026-09-21T10:00:00-07:00',
           {'project/kitchen/Home.md': 'old\n1\n2\n3\n4\n'})
    commit(repo, '2026-09-22T10:00:00-07:00',
           {'project/kitchen/Home.md': 'old\n1\n2\n3\n4\n5\n6\n'})
    commit(repo, '2026-09-23T10:00:00-07:00',
           {'project/kitchen/Home.md': '1\n2\n3\n4\n5\n6\n7\n'})

    assert entries(repo) == {'project/kitchen/Home.md': {
        'path': 'project/kitchen/Home.md', 'kind': 'modified',
        'old_path': None, 'added': 7, 'removed': 1, 'rename_only': False}}


def test_run_archive_is_rename_only(repo):
    commit(repo, '2026-09-18T10:00:00-07:00', {'project/trip.md': 'a\nb\nc\n'})
    commit(repo, '2026-09-23T10:00:00-07:00',
           moves=[('project/trip.md', 'archive/project/trip.md')])

    assert entries(repo) == {'archive/project/trip.md': {
        'path': 'archive/project/trip.md', 'kind': 'renamed',
        'old_path': 'project/trip.md', 'added': 0, 'removed': 0,
        'rename_only': True}}


def test_run_worked_on_then_archived(repo):
    commit(repo, '2026-09-18T10:00:00-07:00', {'project/trip.md': 'a\nb\nc\n'})
    commit(repo, '2026-09-22T10:00:00-07:00',
           {'project/trip.md': 'a\nb\nc\nd\n'})
    commit(repo, '2026-09-23T10:00:00-07:00',
           moves=[('project/trip.md', 'archive/project/trip.md')])

    entry = entries(repo)['archive/project/trip.md']

    assert entry['kind'] == 'renamed'
    assert entry['old_path'] == 'project/trip.md'
    assert entry['rename_only'] is False
    assert entry['added'] == 1


def test_run_created_this_week(repo):
    commit(repo, '2026-09-22T10:00:00-07:00', {'resource/sourdough.md': 'a\n'})
    commit(repo, '2026-09-23T10:00:00-07:00',
           {'resource/sourdough.md': 'a\nb\n'})

    entry = entries(repo)['resource/sourdough.md']

    assert entry['kind'] == 'added'
    assert entry['added'] == 2
    assert entry['old_path'] is None


def test_run_deleted_this_week(repo):
    commit(repo, '2026-09-18T10:00:00-07:00', {'project/old.md': 'a\nb\n'})
    commit(repo, '2026-09-23T10:00:00-07:00', deletes=['project/old.md'])

    entry = entries(repo)['project/old.md']

    assert entry['kind'] == 'deleted'
    assert entry['removed'] == 2


def test_run_deleted_then_restored_is_modified(repo):
    commit(repo, '2026-09-18T10:00:00-07:00', {'project/old.md': 'a\n'})
    commit(repo, '2026-09-22T10:00:00-07:00', deletes=['project/old.md'])
    commit(repo, '2026-09-23T10:00:00-07:00', {'project/old.md': 'a\nb\n'})

    assert entries(repo)['project/old.md']['kind'] == 'modified'


def test_run_renamed_from_non_note_is_added(repo):
    commit(repo, '2026-09-18T10:00:00-07:00', {'resource/vim.txt': 'a\nb\nc\n'})
    commit(repo, '2026-09-23T10:00:00-07:00',
           moves=[('resource/vim.txt', 'resource/vim.md')])

    entry = entries(repo)['resource/vim.md']

    assert entry['kind'] == 'added'
    assert entry['old_path'] is None


# Tests for run: uncommitted changes

def test_run_unstaged_edit_today(repo):
    commit(repo, '2026-09-18T10:00:00-07:00', {'resource/vim.md': 'a\n'})
    write(repo, {'resource/vim.md': 'a\nb\n'})

    assert entries(repo)['resource/vim.md']['kind'] == 'modified'


def test_run_staged_edit_today(repo):
    commit(repo, '2026-09-18T10:00:00-07:00', {'resource/vim.md': 'a\n'})
    write(repo, {'resource/vim.md': 'a\nb\n'})
    git(repo, 'add', 'resource/vim.md')

    assert entries(repo)['resource/vim.md']['added'] == 1


def test_run_untracked_note_today(repo):
    commit(repo, '2026-09-18T10:00:00-07:00', {'area/health.md': 'a\n'})
    write(repo, {'project/new-idea.md': 'a\nb\nc'})

    entry = entries(repo, None)['project/new-idea.md']

    assert entry['kind'] == 'added'
    assert entry['added'] == 3


def test_run_ignored_note_not_listed(repo):
    commit(repo, '2026-09-18T10:00:00-07:00',
           {'.gitignore': 'scratch.md\n', 'area/health.md': 'a\n'})
    write(repo, {'project/scratch.md': 'a\n'})

    assert entries(repo) == {}


def test_run_past_period_ignores_working_tree(repo):
    commit(repo, '2026-09-10T10:00:00-07:00', {'resource/vim.md': 'a\n'})
    write(repo, {'resource/vim.md': 'a\nb\n', 'project/new-idea.md': 'a\n'})

    assert entries(repo, '2026-09-14..2026-09-18') == {}


def test_run_committed_and_uncommitted_combined(repo):
    commit(repo, '2026-09-18T10:00:00-07:00', {'area/health.md': 'a\n'})
    commit(repo, '2026-09-23T10:00:00-07:00',
           {'area/health.md': 'a\n1\n2\n3\n'})
    write(repo, {'area/health.md': 'a\n1\n2\n3\n4\n5\n'})

    assert entries(repo) == {'area/health.md': {
        'path': 'area/health.md', 'kind': 'modified', 'old_path': None,
        'added': 5, 'removed': 0, 'rename_only': False}}


def test_run_repository_with_no_commits(repo):
    write(repo, {'project/foo.md': 'a\n'})

    assert entries(repo, None)['project/foo.md']['kind'] == 'added'


def test_run_repository_with_no_commits_staged(repo):
    write(repo, {'project/foo.md': 'a\n'})
    git(repo, 'add', 'project/foo.md')

    assert entries(repo, None)['project/foo.md']['kind'] == 'added'


# Tests for run: read-only

def test_run_leaves_repository_unchanged(repo):
    commit(repo, '2026-09-18T10:00:00-07:00',
           {'area/health.md': 'a\n', 'resource/vim.md': 'a\n'})
    write(repo, {'area/health.md': 'a\nb\n'})
    git(repo, 'add', 'area/health.md')
    write(repo, {'resource/vim.md': 'a\nb\n', 'project/new.md': 'a\n'})
    # git status may refresh the index, so run it before reading the index
    status, head = (git(repo, 'status', '--porcelain'),
                    git(repo, 'rev-parse', 'HEAD'))
    # Make the index stat info stale, so a refresh would rewrite it
    os.utime(repo / 'resource' / 'vim.md', ns=(1, 1))
    index = repo / '.git' / 'index'
    before = (index.read_bytes(), index.stat().st_mtime_ns)

    run(repo)

    assert (index.read_bytes(), index.stat().st_mtime_ns) == before
    assert git(repo, 'status', '--porcelain') == status
    assert git(repo, 'rev-parse', 'HEAD') == head
    assert not (repo / '.git' / 'index.lock').exists()


# Tests for run: output

def test_run_json_data(repo):
    commit(repo, '2026-09-18T10:00:00-07:00', {'area/health.md': 'a\nb\n'})
    commit(repo, '2026-09-23T10:00:00-07:00',
           {'area/health.md': 'a\n1\n2\n3\n4\n5\n'})

    _, data = run(repo)

    assert data == {'start': '2026-09-21', 'end': '2026-09-25', 'changes': [{
        'path': 'area/health.md', 'kind': 'modified', 'old_path': None,
        'added': 5, 'removed': 1, 'rename_only': False}]}


def test_run_text_lines(repo):
    commit(repo, '2026-09-18T10:00:00-07:00',
           {'area/health.md': 'a\nb\n', 'project/trip.md': 'a\n'})
    commit(repo, '2026-09-23T10:00:00-07:00',
           {'area/health.md': 'a\n1\n2\n3\n4\n5\n',
            'resource/sourdough.md': ''.join(f'{i}\n' for i in range(12))},
           moves=[('project/trip.md', 'archive/project/trip.md')])

    lines, _ = run(repo)

    assert lines == [
        'R   +0  -0  archive/project/trip.md  <- project/trip.md  (rename only)',
        'M   +5  -1  area/health.md',
        'A  +12  -0  resource/sourdough.md',
    ]


def test_run_nothing_changed(repo):
    commit(repo, '2026-09-18T10:00:00-07:00', {'area/health.md': 'a\n'})

    lines, data = run(repo)

    assert lines == []
    assert data['changes'] == []
