"""
Unit tests for scripts/notes.py

Tests all notes and wiki link management functions.
"""

import os
import sys
from pathlib import Path
from datetime import date

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

import notes as notes_module


# Tests for get_wiki_link function

def test_get_wiki_link_simple_filename(tmp_path):
    """Test wiki link for simple filename."""
    filepath = tmp_path / "test.md"
    wiki_link = notes_module.get_wiki_link(str(filepath), str(tmp_path))

    assert wiki_link == "[[test]]"


def test_get_wiki_link_nested_file(tmp_path):
    """Test wiki link for nested file."""
    subdir = tmp_path / "notes" / "work"
    filepath = subdir / "tasks.md"

    wiki_link = notes_module.get_wiki_link(str(filepath), str(tmp_path))

    assert wiki_link == "[[notes/work/tasks]]"


def test_get_wiki_link_file_without_md_extension(tmp_path):
    """Test file without .md extension."""
    filepath = tmp_path / "test.txt"
    wiki_link = notes_module.get_wiki_link(str(filepath), str(tmp_path))

    assert wiki_link == "[[test.txt]]"


def test_get_wiki_link_file_in_root(tmp_path):
    """Test file in root directory."""
    filepath = tmp_path / "README.md"
    wiki_link = notes_module.get_wiki_link(str(filepath), str(tmp_path))

    assert wiki_link == "[[README]]"


# Tests for find_all_markdown_files function

def test_find_all_markdown_files_single_file(tmp_path):
    """Test finding a single markdown file."""
    (tmp_path / "test.md").write_text("content")

    files = notes_module.find_all_markdown_files(str(tmp_path))

    assert len(files) == 1
    assert files[0].endswith("test.md")


def test_find_all_markdown_files_multiple_files(tmp_path):
    """Test finding multiple markdown files."""
    (tmp_path / "file1.md").write_text("content")
    (tmp_path / "file2.md").write_text("content")
    (tmp_path / "file3.md").write_text("content")

    files = notes_module.find_all_markdown_files(str(tmp_path))

    assert len(files) == 3


def test_find_all_markdown_files_nested_files(tmp_path):
    """Test finding files in nested directories."""
    (tmp_path / "root.md").write_text("content")

    subdir1 = tmp_path / "notes"
    subdir1.mkdir()
    (subdir1 / "note1.md").write_text("content")

    subdir2 = subdir1 / "work"
    subdir2.mkdir()
    (subdir2 / "note2.md").write_text("content")

    files = notes_module.find_all_markdown_files(str(tmp_path))

    assert len(files) == 3


def test_find_all_markdown_files_ignore_non_markdown_files(tmp_path):
    """Test that non-markdown files are ignored."""
    (tmp_path / "test.md").write_text("content")
    (tmp_path / "test.txt").write_text("content")
    (tmp_path / "test.pdf").write_text("content")
    (tmp_path / "README").write_text("content")

    files = notes_module.find_all_markdown_files(str(tmp_path))

    assert len(files) == 1
    assert files[0].endswith(".md")


def test_find_all_markdown_files_ignore_hidden_directories(tmp_path):
    """Test that hidden directories are skipped."""
    (tmp_path / "visible.md").write_text("content")

    hidden_dir = tmp_path / ".hidden"
    hidden_dir.mkdir()
    (hidden_dir / "hidden.md").write_text("content")

    files = notes_module.find_all_markdown_files(str(tmp_path))

    assert len(files) == 1
    assert ".hidden" not in files[0]


def test_find_all_markdown_files_empty_directory(tmp_path):
    """Test empty directory returns no files."""
    files = notes_module.find_all_markdown_files(str(tmp_path))

    assert len(files) == 0


def test_find_all_markdown_files_are_sorted(tmp_path):
    """Test that returned files are sorted."""
    (tmp_path / "c.md").write_text("content")
    (tmp_path / "a.md").write_text("content")
    (tmp_path / "b.md").write_text("content")

    files = notes_module.find_all_markdown_files(str(tmp_path))

    filenames = [os.path.basename(f) for f in files]
    assert filenames == ["a.md", "b.md", "c.md"]


# Tests for calculate_week_start function

def test_calculate_week_start_on_monday():
    """Test that Monday returns the same day."""
    # 2026-02-09 is a Monday
    today = date(2026, 2, 9)

    result = notes_module.calculate_week_start(today)

    assert result == today


def test_calculate_week_start_on_tuesday():
    """Test that Tuesday returns the previous Monday."""
    # 2026-02-10 is a Tuesday
    today = date(2026, 2, 10)
    expected = date(2026, 2, 9)  # Previous Monday

    result = notes_module.calculate_week_start(today)

    assert result == expected


def test_calculate_week_start_on_sunday():
    """Test that Sunday returns the previous Monday."""
    # 2026-02-15 is a Sunday
    today = date(2026, 2, 15)
    expected = date(2026, 2, 9)  # Previous Monday

    result = notes_module.calculate_week_start(today)

    assert result == expected


def test_calculate_week_start_on_saturday():
    """Test that Saturday returns the previous Monday."""
    # 2026-02-14 is a Saturday
    today = date(2026, 2, 14)
    expected = date(2026, 2, 9)  # Previous Monday (5 days ago)

    result = notes_module.calculate_week_start(today)

    assert result == expected


def test_calculate_week_start_midweek():
    """Test calculation from middle of the week (Thursday)."""
    # 2026-02-12 is a Thursday
    today = date(2026, 2, 12)
    expected = date(2026, 2, 9)  # Previous Monday

    result = notes_module.calculate_week_start(today)

    assert result == expected


# Tests for calculate_week_end function

def test_calculate_week_end_on_sunday():
    """Test that Sunday returns the same day."""
    # 2026-02-15 is a Sunday
    today = date(2026, 2, 15)

    result = notes_module.calculate_week_end(today)

    assert result == today


def test_calculate_week_end_on_monday():
    """Test that Monday returns the following Sunday."""
    # 2026-02-09 is a Monday
    today = date(2026, 2, 9)
    expected = date(2026, 2, 15)  # Following Sunday

    result = notes_module.calculate_week_end(today)

    assert result == expected


def test_calculate_week_end_on_tuesday():
    """Test that Tuesday returns the following Sunday."""
    # 2026-02-10 is a Tuesday
    today = date(2026, 2, 10)
    expected = date(2026, 2, 15)  # Following Sunday

    result = notes_module.calculate_week_end(today)

    assert result == expected


def test_calculate_week_end_on_saturday():
    """Test that Saturday returns the next day (Sunday)."""
    # 2026-02-14 is a Saturday
    today = date(2026, 2, 14)
    expected = date(2026, 2, 15)  # Next day (Sunday)

    result = notes_module.calculate_week_end(today)

    assert result == expected


def test_calculate_week_end_midweek():
    """Test calculation from middle of the week (Thursday)."""
    # 2026-02-12 is a Thursday
    today = date(2026, 2, 12)
    expected = date(2026, 2, 15)  # Following Sunday

    result = notes_module.calculate_week_end(today)

    assert result == expected
