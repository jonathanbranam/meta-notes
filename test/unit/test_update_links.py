"""Tests for the update_links module."""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import update_links


# Tests for find_markdown_files function


def test_find_markdown_files_empty_directory(tmp_path):
    """Test finding files in an empty directory."""
    files = update_links.find_markdown_files(str(tmp_path))
    assert files == []


def test_find_markdown_files_single_file(tmp_path):
    """Test finding a single markdown file."""
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test")

    files = update_links.find_markdown_files(str(tmp_path))

    assert len(files) == 1
    assert files[0] == test_file


def test_find_markdown_files_multiple_files(tmp_path):
    """Test finding multiple markdown files."""
    file1 = tmp_path / "file1.md"
    file2 = tmp_path / "file2.md"
    file1.write_text("# File 1")
    file2.write_text("# File 2")

    files = update_links.find_markdown_files(str(tmp_path))

    assert len(files) == 2
    assert set(files) == {file1, file2}


def test_find_markdown_files_nested_directories(tmp_path):
    """Test finding files in nested directories."""
    subdir = tmp_path / "project" / "subproject"
    subdir.mkdir(parents=True)

    file1 = tmp_path / "root.md"
    file2 = subdir / "nested.md"
    file1.write_text("# Root")
    file2.write_text("# Nested")

    files = update_links.find_markdown_files(str(tmp_path))

    assert len(files) == 2
    assert set(files) == {file1, file2}


def test_find_markdown_files_skips_hidden_directories(tmp_path):
    """Test that hidden directories are skipped."""
    hidden_dir = tmp_path / ".hidden"
    hidden_dir.mkdir()

    visible_file = tmp_path / "visible.md"
    hidden_file = hidden_dir / "hidden.md"
    visible_file.write_text("# Visible")
    hidden_file.write_text("# Hidden")

    files = update_links.find_markdown_files(str(tmp_path))

    assert len(files) == 1
    assert files[0] == visible_file


def test_find_markdown_files_ignores_non_markdown(tmp_path):
    """Test that non-markdown files are ignored."""
    md_file = tmp_path / "test.md"
    txt_file = tmp_path / "test.txt"
    md_file.write_text("# Markdown")
    txt_file.write_text("Text")

    files = update_links.find_markdown_files(str(tmp_path))

    assert len(files) == 1
    assert files[0] == md_file


# Tests for update_links_in_file function


def test_update_links_in_file_simple_link(tmp_path):
    """Test updating a simple wiki link."""
    test_file = tmp_path / "test.md"
    test_file.write_text("See [[project/kitchen-remodel]]")

    changed, count = update_links.update_links_in_file(
        test_file, "project/kitchen-remodel", "archive/project/kitchen-remodel"
    )

    assert changed is True
    assert count == 1

    content = test_file.read_text()
    assert content == "See [[archive/project/kitchen-remodel]]"


def test_update_links_in_file_multiple_links(tmp_path):
    """Test updating multiple links in one file."""
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "First [[project/old]] and second [[project/old]] reference"
    )

    changed, count = update_links.update_links_in_file(
        test_file, "project/old", "project/new"
    )

    assert changed is True
    assert count == 2

    content = test_file.read_text()
    assert content == "First [[project/new]] and second [[project/new]] reference"


def test_update_links_in_file_nested_paths(tmp_path):
    """Test updating links with nested paths."""
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "See [[project/kitchen/overview]] and [[project/kitchen/tasks]]"
    )

    changed, count = update_links.update_links_in_file(
        test_file, "project/kitchen", "archive/project/kitchen"
    )

    assert changed is True
    assert count == 2

    content = test_file.read_text()
    assert "[[archive/project/kitchen/overview]]" in content
    assert "[[archive/project/kitchen/tasks]]" in content


def test_update_links_in_file_no_matches(tmp_path):
    """Test file with no matching links."""
    test_file = tmp_path / "test.md"
    test_file.write_text("See [[project/other]]")

    changed, count = update_links.update_links_in_file(
        test_file, "project/kitchen", "archive/project/kitchen"
    )

    assert changed is False
    assert count == 0

    # File should be unchanged
    content = test_file.read_text()
    assert content == "See [[project/other]]"


def test_update_links_in_file_partial_match_not_updated(tmp_path):
    """Test that partial matches are not updated."""
    test_file = tmp_path / "test.md"
    test_file.write_text("See [[project/kitchen-remodel-v2]]")

    changed, count = update_links.update_links_in_file(
        test_file, "project/kitchen-remodel", "archive/project/kitchen-remodel"
    )

    assert changed is False
    assert count == 0

    # File should be unchanged
    content = test_file.read_text()
    assert content == "See [[project/kitchen-remodel-v2]]"


def test_update_links_in_file_dry_run(tmp_path):
    """Test dry run mode doesn't modify files."""
    test_file = tmp_path / "test.md"
    original_content = "See [[project/old]]"
    test_file.write_text(original_content)

    changed, count = update_links.update_links_in_file(
        test_file, "project/old", "project/new", dry_run=True
    )

    assert changed is True
    assert count == 1

    # File should be unchanged in dry run mode
    content = test_file.read_text()
    assert content == original_content


def test_update_links_in_file_multiline_content(tmp_path):
    """Test updating links in multiline content."""
    test_file = tmp_path / "test.md"
    test_file.write_text(
        """# Daily Note

## Tasks
- [[project/kitchen/task1]]
- [[project/kitchen/task2]]

## Notes
See [[project/kitchen/overview]]
"""
    )

    changed, count = update_links.update_links_in_file(
        test_file, "project/kitchen", "archive/project/kitchen"
    )

    assert changed is True
    assert count == 3

    content = test_file.read_text()
    assert "[[archive/project/kitchen/task1]]" in content
    assert "[[archive/project/kitchen/task2]]" in content
    assert "[[archive/project/kitchen/overview]]" in content


# Tests for update_all_links function


def test_update_all_links_multiple_files(tmp_path):
    """Test updating links across multiple files."""
    file1 = tmp_path / "file1.md"
    file2 = tmp_path / "file2.md"
    file3 = tmp_path / "file3.md"

    file1.write_text("Reference to [[project/old]]")
    file2.write_text("Another [[project/old]] reference")
    file3.write_text("No matching links here")

    stats = update_links.update_all_links(str(tmp_path), "project/old", "project/new")

    assert stats["files_scanned"] == 3
    assert stats["files_modified"] == 2
    assert stats["total_replacements"] == 2

    # Check files were actually updated
    assert "[[project/new]]" in file1.read_text()
    assert "[[project/new]]" in file2.read_text()


def test_update_all_links_nested_directories(tmp_path):
    """Test updating links in nested directory structure."""
    subdir = tmp_path / "area" / "finance"
    subdir.mkdir(parents=True)

    root_file = tmp_path / "root.md"
    nested_file = subdir / "budget.md"

    root_file.write_text("See [[project/expenses]]")
    nested_file.write_text("Also [[project/expenses/2026]]")

    stats = update_links.update_all_links(
        str(tmp_path), "project/expenses", "archive/project/expenses"
    )

    assert stats["files_modified"] == 2
    assert stats["total_replacements"] == 2


def test_update_all_links_strips_slashes(tmp_path):
    """Test that leading/trailing slashes are stripped from paths."""
    test_file = tmp_path / "test.md"
    test_file.write_text("Link: [[project/test]]")

    # Paths with slashes should work the same
    stats = update_links.update_all_links(
        str(tmp_path), "/project/test/", "/project/new/"
    )

    assert stats["total_replacements"] == 1
    assert "[[project/new]]" in test_file.read_text()


def test_update_all_links_dry_run_mode(tmp_path):
    """Test dry run mode across all files."""
    file1 = tmp_path / "file1.md"
    file2 = tmp_path / "file2.md"

    original1 = "Link: [[project/old]]"
    original2 = "Another: [[project/old]]"
    file1.write_text(original1)
    file2.write_text(original2)

    stats = update_links.update_all_links(
        str(tmp_path), "project/old", "project/new", dry_run=True
    )

    assert stats["files_modified"] == 2
    assert stats["total_replacements"] == 2

    # Files should be unchanged
    assert file1.read_text() == original1
    assert file2.read_text() == original2
