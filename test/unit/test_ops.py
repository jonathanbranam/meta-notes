"""
Unit tests for scripts/meta_notes/ops.py

Mirrors test/archive.vader, test/rename.vader, and openspec/specs/archive,
plus folder moves and git behavior.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import cli, ops


@pytest.fixture
def root(tmp_path, monkeypatch):
    """A notes root as the current directory, like the vader fixtures."""
    for folder in ('project', 'area', 'resource'):
        (tmp_path / folder).mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def write(path, *lines):
    """Write lines to a file (with trailing newline), creating parents."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(''.join(line + '\n' for line in lines))


def read_lines(path):
    return Path(path).read_text().splitlines()


# Tests for archive function (test/archive.vader)

def test_archive_single_file_from_project(root):
    write('project/test-archive-file.md', '# Test Project')

    ops.archive(['project/test-archive-file.md'])

    assert Path('archive/project/test-archive-file.md').is_file()
    assert not Path('project/test-archive-file.md').exists()


def test_archive_folder_from_project(root):
    write('project/test-archive-folder/note.md', '# Folder Note')

    ops.archive(['project/test-archive-folder'])

    assert Path('archive/project/test-archive-folder/note.md').is_file()
    assert not Path('project/test-archive-folder').exists()


def test_archive_folder_from_area(root):
    write('area/test-archive-area/note.md', '# Test Area')

    ops.archive(['area/test-archive-area'])

    assert Path('archive/area/test-archive-area/note.md').is_file()
    assert not Path('area/test-archive-area').exists()


def test_archive_file_from_resource(root):
    write('resource/test-archive-resource.md', '# Test Resource')

    ops.archive(['resource/test-archive-resource.md'])

    assert Path('archive/resource/test-archive-resource.md').is_file()
    assert not Path('resource/test-archive-resource.md').exists()


def test_archive_single_item_result(root):
    """A single file reports its archive path and message."""
    write('project/note.md', '# Note')

    [item] = ops.archive(['project/note.md'])

    assert item.ok
    assert item.is_file
    assert item.path == 'project/note.md'
    assert item.archive_path == 'archive/project/note.md'
    assert item.message == 'Archived: project/note.md → archive/project/note.md'


def test_archive_folder_message_counts_files(root):
    """A folder with notes reports the move count."""
    write('project/f/a.md', '# A')
    write('project/f/sub/b.md', '# B')

    [item] = ops.archive(['project/f'])

    assert item.message == 'Archived: project/f → archive/project/f (3 files)'


def test_archive_non_para_folder_fails(root):
    write('test-invalid.md', '# Invalid')

    with pytest.raises(ops.OpError,
                       match=r'^Can only archive items from project/, area/, or resource/ folders$'):
        ops.archive(['test-invalid.md'])

    assert Path('test-invalid.md').is_file()


def test_archive_already_archived_fails(root):
    write('archive/project/test-already-archived.md', '# Already Archived')

    with pytest.raises(ops.OpError, match='Can only archive items from project'):
        ops.archive(['archive/project/test-already-archived.md'])


def test_archive_wildcard_batch(root):
    for n in (1, 2, 3):
        write(f'project/test-batch-folder/file{n}.md', f'# File {n}')

    items = ops.archive(['project/test-batch-folder/*.md'])

    assert [i.ok for i in items] == [True, True, True]
    for n in (1, 2, 3):
        assert Path(f'archive/project/test-batch-folder/file{n}.md').is_file()
        assert not Path(f'project/test-batch-folder/file{n}.md').exists()
    assert Path('project/test-batch-folder').is_dir()


def test_archive_wildcard_mixed_files_and_folders(root):
    write('project/test-batch-mixed/fileA.md', '# File A')
    write('project/test-batch-mixed/fileB.md', '# File B')
    write('project/test-batch-mixed/subfolder/subfile.md', '# Sub File')

    ops.archive(['project/test-batch-mixed/*'])

    assert Path('archive/project/test-batch-mixed/fileA.md').is_file()
    assert Path('archive/project/test-batch-mixed/fileB.md').is_file()
    assert Path('archive/project/test-batch-mixed/subfolder/subfile.md').is_file()


def test_archive_wildcard_continues_past_failures(root):
    """Each match is archived independently; failures are per item."""
    write('project/a.md', '# A')
    write('project/b.md', '# B')
    write('archive/project/a.md', '# existing')

    items = ops.archive(['project/*.md'])

    assert [(i.path, i.ok) for i in items] == [('project/a.md', False),
                                               ('project/b.md', True)]
    assert items[0].error == 'Target file already exists: archive/project/a.md'
    assert items[0].message == ('Failed to archive: project/a.md '
                                '(Target file already exists: archive/project/a.md)')
    assert ops.archive_summary(items) == 'Archived 1 item(s) (1 failed)'
    assert Path('archive/project/b.md').is_file()


def test_archive_folder_with_only_non_markdown_files(root):
    write('project/test-image-folder/photo1.jpg', 'FAKEJPG')
    write('project/test-image-folder/photo2.jpg', 'FAKEJPG')

    ops.archive(['project/test-image-folder'])

    assert Path('archive/project/test-image-folder/photo1.jpg').is_file()
    assert Path('archive/project/test-image-folder/photo2.jpg').is_file()
    assert not Path('project/test-image-folder').exists()


def test_archive_updates_link_to_non_markdown_folder(root):
    write('resource/index.md', '# Index', '', 'See [[project/test-link-folder]]')
    write('project/test-link-folder/photo.jpg', 'FAKEJPG')

    ops.archive(['project/test-link-folder'])

    lines = read_lines('resource/index.md')
    assert 'See [[archive/project/test-link-folder]]' in lines
    assert 'See [[project/test-link-folder]]' not in lines


def test_archive_updates_link_to_markdown_folder(root):
    write('resource/index2.md', '# Index', '', 'See [[project/test-md-link-folder]]')
    write('project/test-md-link-folder/note.md', '# Note')

    [item] = ops.archive(['project/test-md-link-folder'])

    assert 'See [[archive/project/test-md-link-folder]]' in read_lines('resource/index2.md')
    assert item.result.links_updated == ['resource/index2.md']


def test_archive_updates_link_to_subfolder(root):
    write('resource/subfolder-index.md', '# Index', '', 'See [[project/test-root/subfolder]]')
    write('project/test-root/subfolder/photo.jpg', 'FAKEJPG')

    ops.archive(['project/test-root'])

    assert Path('archive/project/test-root/subfolder').is_dir()
    lines = read_lines('resource/subfolder-index.md')
    assert 'See [[archive/project/test-root/subfolder]]' in lines
    assert 'See [[project/test-root/subfolder]]' not in lines


def test_archive_file_without_md_extension(root):
    write('project/test-no-ext-file.md', '# No Ext Test')

    [item] = ops.archive(['project/test-no-ext-file'])

    assert Path('archive/project/test-no-ext-file.md').is_file()
    assert not Path('project/test-no-ext-file.md').exists()
    assert item.message == ('Archived: project/test-no-ext-file.md → '
                            'archive/project/test-no-ext-file.md')


def test_archive_file_with_spaces(root):
    write('project/my spaced note.md', '# Spaced Note')

    ops.archive(['project/my spaced note.md'])

    assert Path('archive/project/my spaced note.md').is_file()
    assert not Path('project/my spaced note.md').exists()


def test_archive_wildcard_no_matches(root):
    with pytest.raises(ops.OpError,
                       match=r'^No items match wildcard pattern: project/nonexistent-folder/\*$'):
        ops.archive(['project/nonexistent-folder/*'])


def test_archive_path_not_found(root):
    with pytest.raises(ops.OpError, match=r'^Path not found: project/nonexistent$'):
        ops.archive(['project/nonexistent'])

    assert not Path('archive').exists()


def test_archive_updates_deeply_nested_link(root):
    write('resource/deep-index.md', '# Deep Index', '', 'See [[project/deep-root/a/b/c]]')
    write('project/deep-root/a/b/c/data.txt', 'FAKEFILE')

    ops.archive(['project/deep-root'])

    assert Path('archive/project/deep-root/a/b/c').is_dir()
    assert not Path('project/deep-root').exists()
    assert 'See [[archive/project/deep-root/a/b/c]]' in read_lines('resource/deep-index.md')


# Tests for rename function (test/rename.vader)

def test_rename_bare_name_keeps_directory(root):
    write('project/test-rename-original.md', '# Original Name')

    result = ops.rename('project/test-rename-original.md', 'test-rename-new')

    assert result.dest == 'project/test-rename-new.md'
    assert Path('project/test-rename-new.md').is_file()
    assert not Path('project/test-rename-original.md').exists()


def test_rename_with_md_extension(root):
    write('project/test-rename-ext.md', '# Test')

    ops.rename('project/test-rename-ext.md', 'test-rename-newext.md')

    assert Path('project/test-rename-newext.md').is_file()
    assert not Path('project/test-rename-newext.md.md').exists()


def test_rename_to_different_directory(root):
    write('project/test-rename-source/file.md', '# Move Me')
    Path('project/test-rename-dest').mkdir()

    result = ops.rename('project/test-rename-source/file.md',
                        'project/test-rename-dest/moved-file')

    assert result.dest == 'project/test-rename-dest/moved-file.md'
    assert Path('project/test-rename-dest/moved-file.md').is_file()
    assert not Path('project/test-rename-source/file.md').exists()


def test_rename_target_exists(root):
    write('project/test-rename-file1.md', '# File 1')
    write('project/test-rename-file2.md', '# File 2')

    with pytest.raises(ops.OpError,
                       match=r'^Target file already exists: project/test-rename-file2.md$'):
        ops.rename('project/test-rename-file1.md', 'test-rename-file2')

    assert read_lines('project/test-rename-file1.md') == ['# File 1']
    assert read_lines('project/test-rename-file2.md') == ['# File 2']


def test_rename_creates_target_directory(root):
    write('project/test-rename-createdir.md', '# Test')

    ops.rename('project/test-rename-createdir.md', 'project/test-rename-newdir/subdir/file')

    assert Path('project/test-rename-newdir/subdir/file.md').is_file()
    assert not Path('project/test-rename-createdir.md').exists()


def test_rename_updates_wiki_links(root):
    write('project/test-links/target.md', '# Target File')
    write('project/file1.md', '# File 1', '', 'See [[project/test-links/target]]')
    write('project/file2.md', '# File 2', '', 'Link: [[project/test-links/target]]')
    write('project/file3.md', '# File 3', '', 'No links here')

    result = ops.rename('project/test-links/target.md', 'project/test-links/renamed-target')

    assert read_lines('project/file1.md')[2] == 'See [[project/test-links/renamed-target]]'
    assert read_lines('project/file2.md')[2] == 'Link: [[project/test-links/renamed-target]]'
    assert read_lines('project/file3.md') == ['# File 3', '', 'No links here']
    assert result.links_updated == ['project/file1.md', 'project/file2.md']


def test_rename_updates_wiki_links_across_directories(root):
    write('project/source/moveme.md', '# Moving File')
    write('project/ref.md', '# Reference', '', 'Link: [[project/source/moveme]]')

    ops.rename('project/source/moveme.md', 'project/destination/moved')

    assert read_lines('project/ref.md')[2] == 'Link: [[project/destination/moved]]'


def test_rename_updates_subpath_link(root):
    write('project/folder/index.md', '# Folder Index')
    write('project/links.md', '# Links', '', 'Folder: [[project/folder]]',
          'Index: [[project/folder/index]]')

    ops.rename('project/folder/index.md', 'project/renamed-folder/index')

    lines = read_lines('project/links.md')
    assert 'Index: [[project/renamed-folder/index]]' in lines
    # Only the note moved, so the folder link is untouched
    assert 'Folder: [[project/folder]]' in lines


def test_rename_updates_matching_header(root):
    write('project/test-header/original.md', '# project/test-header/original', '',
          'Some content')

    ops.rename('project/test-header/original.md', 'project/test-header/renamed')

    assert read_lines('project/test-header/renamed.md') == [
        '# project/test-header/renamed', '', 'Some content']


def test_rename_preserves_custom_header(root):
    write('project/test-custom/file.md', '# My Custom Title', '', 'Content here')

    ops.rename('project/test-custom/file.md', 'project/test-custom/newname')

    assert read_lines('project/test-custom/newname.md')[0] == '# My Custom Title'


def test_rename_updates_header_across_directories(root):
    write('project/old-dir/note.md', '# project/old-dir/note', '', 'Content')
    Path('project/new-dir').mkdir()

    ops.rename('project/old-dir/note.md', 'project/new-dir/note')

    assert read_lines('project/new-dir/note.md')[0] == '# project/new-dir/note'


def test_rename_empty_file(root):
    Path('project/empty.md').write_text('')

    ops.rename('project/empty.md', 'project/renamed-empty')

    assert Path('project/renamed-empty.md').read_text() == ''
    assert not Path('project/empty.md').exists()


def test_rename_file_at_root(root):
    """A bare name for a note at the root stays at the root."""
    write('inbox.md', '# inbox')

    result = ops.rename('inbox.md', 'later')

    assert result.dest == 'later.md'
    assert read_lines('later.md') == ['# later']


# Tests for move function

def test_move_source_not_found(root):
    with pytest.raises(ops.OpError, match=r'^Source not found: project/missing.md$'):
        ops.move('project/missing.md', 'area/missing')


def test_move_appends_md_extension(root):
    write('project/foo.md', '# project/foo')

    result = ops.move('project/foo.md', 'area/foo')

    assert result.dest == 'area/foo.md'
    assert result.moves == [('project/foo.md', 'area/foo.md')]
    assert read_lines('area/foo.md') == ['# area/foo']


def test_move_header_only_exact_match(root):
    """The header is rewritten only when the first line is exactly `# <path>`."""
    write('project/a.md', '# project/a extra')
    write('project/b.md', 'intro', '# project/b')

    ops.move('project/a.md', 'area/a')
    ops.move('project/b.md', 'area/b')

    assert read_lines('area/a.md') == ['# project/a extra']
    assert read_lines('area/b.md') == ['intro', '# project/b']


def test_move_header_preserves_rest_of_file(root):
    """Only the first line changes; the rest of the bytes are kept."""
    Path('project/foo.md').write_bytes(b'# project/foo\r\nbody\n')
    Path('project/bar.md').write_bytes(b'# project/bar\nbody')

    ops.move('project/foo.md', 'area/foo')
    ops.move('project/bar.md', 'area/bar')

    # CRLF first line doesn't match exactly, same as Vim's readfile()
    assert Path('area/foo.md').read_bytes() == b'# project/foo\r\nbody\n'
    assert Path('area/bar.md').read_bytes() == b'# area/bar\nbody'


def test_move_project_converted_to_area(root):
    """Spec scenario: all contents move and every link beneath is rewritten."""
    write('project/foo.md', '# project/foo')
    write('project/foo/tasks.md', '# project/foo/tasks')
    write('project/foo/notes/meeting.md', '# project/foo/notes/meeting')
    write('project/foo/plans/drawing.pdf', 'PDF')
    write('resource/index.md', '[[project/foo]]', '[[project/foo/tasks]]',
          '[[project/foo/notes/meeting]]', '[[project/foo/plans]]',
          '[[project/foobar]]')

    ops.move('project/foo', 'area/foo')
    ops.move('project/foo.md', 'area/foo')

    assert Path('area/foo/tasks.md').is_file()
    assert Path('area/foo/notes/meeting.md').is_file()
    assert Path('area/foo/plans/drawing.pdf').is_file()
    assert not Path('project/foo').exists()
    assert read_lines('area/foo.md') == ['# area/foo']
    assert read_lines('area/foo/tasks.md') == ['# area/foo/tasks']
    assert read_lines('area/foo/notes/meeting.md') == ['# area/foo/notes/meeting']
    assert read_lines('resource/index.md') == [
        '[[area/foo]]', '[[area/foo/tasks]]', '[[area/foo/notes/meeting]]',
        '[[area/foo/plans]]', '[[project/foobar]]']


def test_move_folder_move_list(root):
    """Each note under the folder once, then the folder itself."""
    write('project/f/a.md', '# A')
    write('project/f/sub/b.md', '# B')
    write('project/f/sub/c.txt', 'C')
    write('project/f/.hidden/d.md', '# D')

    result = ops.move('project/f', 'area/g')

    assert result.moves == [('project/f/a.md', 'area/g/a.md'),
                            ('project/f/sub/b.md', 'area/g/sub/b.md'),
                            ('project/f', 'area/g')]
    assert Path('area/g/sub/c.txt').is_file()
    assert Path('area/g/.hidden/d.md').is_file()


def test_move_folder_trailing_slash(root):
    write('project/f/a.md', '# project/f/a')

    result = ops.move('project/f/', 'area/f/')

    assert result.moves == [('project/f/a.md', 'area/f/a.md'), ('project/f', 'area/f')]
    assert read_lines('area/f/a.md') == ['# area/f/a']


def test_move_folder_creates_parent(root):
    write('project/f/a.md', '# A')

    ops.move('project/f', 'area/deep/nested/f')

    assert Path('area/deep/nested/f/a.md').is_file()


def test_move_file_onto_directory_fails(root):
    write('project/foo.md', '# foo')
    Path('area/foo.md').mkdir()

    with pytest.raises(ops.OpError, match='Target file already exists'):
        ops.move('project/foo.md', 'area/foo.md')

    assert Path('project/foo.md').is_file()


def test_move_folder_into_itself_fails(root):
    write('project/f/a.md', '# A')

    with pytest.raises(ops.OpError, match='^Failed to move directory: project/f'):
        ops.move('project/f', 'project/f/inner')

    assert Path('project/f/a.md').is_file()


def test_move_links_updated_deduplicated(root):
    """A file rewritten for several moves is listed once."""
    write('project/f/a.md', '# A')
    write('resource/index.md', '[[project/f]] [[project/f/a]]')

    result = ops.move('project/f', 'area/f')

    assert result.links_updated == ['resource/index.md']
    assert read_lines('resource/index.md') == ['[[area/f]] [[area/f/a]]']


# Tests for CLI file commands

def test_cli_archive_json_batch(root, capsys, monkeypatch):
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    write('project/b/one.md', '# project/b/one')
    write('project/b/two.md', '# two')
    write('resource/index.md', '[[project/b/one]]')

    code = cli.main(['--root', str(root), '--json', 'archive', 'project/b/*.md'])
    out = json.loads(capsys.readouterr().out)

    assert code == 0
    assert out['ok'] is True
    assert out['batch'] is True
    assert out['archived'] == 2
    assert out['failed'] == 0
    assert out['moves'] == [['project/b/one.md', 'archive/project/b/one.md'],
                            ['project/b/two.md', 'archive/project/b/two.md']]
    assert out['links_updated'] == ['resource/index.md']
    assert [i['archive_path'] for i in out['items']] == [
        'archive/project/b/one.md', 'archive/project/b/two.md']


def test_cli_archive_json_partial_failure(root, capsys):
    write('project/a.md', '# A')
    write('project/b.md', '# B')
    write('archive/project/a.md', '# existing')

    code = cli.main(['--root', str(root), '--json', 'archive', 'project/*.md'])
    out = json.loads(capsys.readouterr().out)

    assert code == 1
    assert out['ok'] is False
    assert out['error'] == '1 of 2 item(s) failed to archive'
    assert [i['ok'] for i in out['items']] == [False, True]
    assert out['items'][0]['error'] == 'Target file already exists: archive/project/a.md'


def test_cli_archive_multiple_paths(root, capsys):
    """Shell-expanded wildcards arrive as several paths."""
    write('project/a.md', '# A')
    write('area/b.md', '# B')

    code = cli.main(['--root', str(root), 'archive', 'project/a.md', 'area/b'])

    assert code == 0
    assert capsys.readouterr().out == (
        'Archived: project/a.md → archive/project/a.md\n'
        'Archived: area/b.md → archive/area/b.md\n'
        'Archived 2 item(s)\n')


def test_cli_rename_json(root, capsys):
    write('project/foo.md', '# project/foo')
    write('resource/index.md', '[[project/foo]]')

    code = cli.main(['--root', str(root), '--json', 'rename', 'project/foo.md', 'bar'])
    out = json.loads(capsys.readouterr().out)

    assert code == 0
    assert out == {'ok': True, 'source': 'project/foo.md', 'dest': 'project/bar.md',
                   'moves': [['project/foo.md', 'project/bar.md']],
                   'links_updated': ['resource/index.md'], 'warnings': []}


def test_cli_move_target_exists_makes_no_changes(root, capsys):
    write('project/foo.md', '# project/foo')
    write('area/foo.md', '# area/foo')
    write('resource/index.md', '[[project/foo]]')

    code = cli.main(['--root', str(root), '--json', 'move', 'project/foo.md', 'area/foo'])
    out = json.loads(capsys.readouterr().out)

    assert code == 1
    assert out['error'] == 'Target file already exists: area/foo.md'
    assert read_lines('project/foo.md') == ['# project/foo']
    assert read_lines('resource/index.md') == ['[[project/foo]]']


# Tests for git behavior

@pytest.mark.skipif(shutil.which('git') is None, reason='git not installed')
def test_cli_rename_in_git_repo_leaves_index_and_history(root, capsys):
    def git(*args):
        return subprocess.run(['git', *args], cwd=root, check=True,
                              capture_output=True, text=True).stdout

    write('project/foo.md', '# project/foo')
    write('resource/index.md', '[[project/foo]]')
    git('init', '-q')
    git('add', '-A')
    git('-c', 'user.name=Test', '-c', 'user.email=test@example.com',
        'commit', '-q', '-m', 'initial')
    head = git('rev-parse', 'HEAD')
    index = git('ls-files', '--stage')

    code = cli.main(['--root', str(root), 'rename', 'project/foo.md', 'bar'])

    assert code == 0
    assert read_lines('project/bar.md') == ['# project/bar']
    assert read_lines('resource/index.md') == ['[[project/bar]]']
    assert git('rev-parse', 'HEAD') == head
    assert git('ls-files', '--stage') == index
    assert git('diff', '--cached', '--name-only') == ''
    assert git('rev-list', '--count', 'HEAD').strip() == '1'
