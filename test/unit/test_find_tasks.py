"""
Unit tests for scripts/find_tasks.py

Tests all functions in the task finder script.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

# Add scripts directory to path to import the module
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

import find_tasks


class TestFindTasksInFile:
    """Tests for find_tasks_in_file function."""

    def test_find_simple_uncompleted_task(self, tmp_path):
        """Test finding a simple uncompleted task."""
        test_file = tmp_path / "test.md"
        test_file.write_text("- [ ] Simple task\n")

        tasks = find_tasks.find_tasks_in_file(str(test_file))

        assert len(tasks) == 1
        assert tasks[0][0] == 1  # line number
        assert tasks[0][1] == "- [ ] Simple task"
        assert tasks[0][2] == " "  # status

    def test_find_completed_task_lowercase_x(self, tmp_path):
        """Test finding completed task with lowercase x."""
        test_file = tmp_path / "test.md"
        test_file.write_text("- [x] Completed task\n")

        tasks = find_tasks.find_tasks_in_file(str(test_file))

        assert len(tasks) == 1
        assert tasks[0][2] == "x"

    def test_find_completed_task_uppercase_x(self, tmp_path):
        """Test finding completed task with uppercase X."""
        test_file = tmp_path / "test.md"
        test_file.write_text("- [X] Completed task\n")

        tasks = find_tasks.find_tasks_in_file(str(test_file))

        assert len(tasks) == 1
        assert tasks[0][2] == "X"

    def test_find_rescheduled_task(self, tmp_path):
        """Test finding rescheduled task."""
        test_file = tmp_path / "test.md"
        test_file.write_text("- [>] Rescheduled task\n")

        tasks = find_tasks.find_tasks_in_file(str(test_file))

        assert len(tasks) == 1
        assert tasks[0][2] == ">"

    def test_find_canceled_task(self, tmp_path):
        """Test finding canceled task."""
        test_file = tmp_path / "test.md"
        test_file.write_text("- [-] Canceled task\n")

        tasks = find_tasks.find_tasks_in_file(str(test_file))

        assert len(tasks) == 1
        assert tasks[0][2] == "-"

    def test_all_bullet_types(self, tmp_path):
        """Test all three bullet types (-, *, +)."""
        test_file = tmp_path / "test.md"
        content = """- [ ] Dash bullet
* [ ] Asterisk bullet
+ [ ] Plus bullet
"""
        test_file.write_text(content)

        tasks = find_tasks.find_tasks_in_file(str(test_file))

        assert len(tasks) == 3
        assert "Dash bullet" in tasks[0][1]
        assert "Asterisk bullet" in tasks[1][1]
        assert "Plus bullet" in tasks[2][1]

    def test_mixed_content(self, tmp_path):
        """Test file with tasks and non-task content."""
        test_file = tmp_path / "test.md"
        content = """# Header

Some text here.

- [ ] First task
- Not a task (no brackets)
- [x] Second task

More text.

* [ ] Third task
"""
        test_file.write_text(content)

        tasks = find_tasks.find_tasks_in_file(str(test_file))

        assert len(tasks) == 3
        assert "First task" in tasks[0][1]
        assert "Second task" in tasks[1][1]
        assert "Third task" in tasks[2][1]

    def test_indented_tasks(self, tmp_path):
        """Test tasks with various indentation levels."""
        test_file = tmp_path / "test.md"
        content = """- [ ] No indent
  - [ ] Two space indent
    - [ ] Four space indent
\t- [ ] Tab indent
"""
        test_file.write_text(content)

        tasks = find_tasks.find_tasks_in_file(str(test_file))

        assert len(tasks) == 4

    def test_line_numbers(self, tmp_path):
        """Test that line numbers are correctly tracked."""
        test_file = tmp_path / "test.md"
        content = """Line 1
Line 2
- [ ] Task on line 3
Line 4
Line 5
- [ ] Task on line 6
"""
        test_file.write_text(content)

        tasks = find_tasks.find_tasks_in_file(str(test_file))

        assert len(tasks) == 2
        assert tasks[0][0] == 3
        assert tasks[1][0] == 6

    def test_empty_file(self, tmp_path):
        """Test empty file returns no tasks."""
        test_file = tmp_path / "test.md"
        test_file.write_text("")

        tasks = find_tasks.find_tasks_in_file(str(test_file))

        assert len(tasks) == 0

    def test_no_tasks(self, tmp_path):
        """Test file with no tasks."""
        test_file = tmp_path / "test.md"
        content = """# Header

Just some text.
- Regular list item
* Another list item
"""
        test_file.write_text(content)

        tasks = find_tasks.find_tasks_in_file(str(test_file))

        assert len(tasks) == 0

    def test_invalid_task_formats(self, tmp_path):
        """Test that invalid task formats are not matched."""
        test_file = tmp_path / "test.md"
        content = """- [] Missing space in brackets
- [  ] Two characters in brackets
- [ab] Multiple characters
-[ ] Missing space after dash
- [ ]Missing space after brackets is OK but no text
"""
        test_file.write_text(content)

        tasks = find_tasks.find_tasks_in_file(str(test_file))

        # Only the last one should match (it has proper format)
        assert len(tasks) == 1

    def test_nonexistent_file(self):
        """Test handling of nonexistent file."""
        tasks = find_tasks.find_tasks_in_file("/nonexistent/file.md")

        assert len(tasks) == 0


class TestGetWikiLink:
    """Tests for get_wiki_link function."""

    def test_simple_filename(self, tmp_path):
        """Test wiki link for simple filename."""
        filepath = tmp_path / "test.md"
        wiki_link = find_tasks.get_wiki_link(str(filepath), str(tmp_path))

        assert wiki_link == "[[test]]"

    def test_nested_file(self, tmp_path):
        """Test wiki link for nested file."""
        subdir = tmp_path / "notes" / "work"
        filepath = subdir / "tasks.md"

        wiki_link = find_tasks.get_wiki_link(str(filepath), str(tmp_path))

        assert wiki_link == "[[notes/work/tasks]]"

    def test_file_without_md_extension(self, tmp_path):
        """Test file without .md extension."""
        filepath = tmp_path / "test.txt"
        wiki_link = find_tasks.get_wiki_link(str(filepath), str(tmp_path))

        assert wiki_link == "[[test.txt]]"

    def test_file_in_root(self, tmp_path):
        """Test file in root directory."""
        filepath = tmp_path / "README.md"
        wiki_link = find_tasks.get_wiki_link(str(filepath), str(tmp_path))

        assert wiki_link == "[[README]]"


class TestFindAllMarkdownFiles:
    """Tests for find_all_markdown_files function."""

    def test_find_single_file(self, tmp_path):
        """Test finding a single markdown file."""
        (tmp_path / "test.md").write_text("content")

        files = find_tasks.find_all_markdown_files(str(tmp_path))

        assert len(files) == 1
        assert files[0].endswith("test.md")

    def test_find_multiple_files(self, tmp_path):
        """Test finding multiple markdown files."""
        (tmp_path / "file1.md").write_text("content")
        (tmp_path / "file2.md").write_text("content")
        (tmp_path / "file3.md").write_text("content")

        files = find_tasks.find_all_markdown_files(str(tmp_path))

        assert len(files) == 3

    def test_find_nested_files(self, tmp_path):
        """Test finding files in nested directories."""
        (tmp_path / "root.md").write_text("content")

        subdir1 = tmp_path / "notes"
        subdir1.mkdir()
        (subdir1 / "note1.md").write_text("content")

        subdir2 = subdir1 / "work"
        subdir2.mkdir()
        (subdir2 / "note2.md").write_text("content")

        files = find_tasks.find_all_markdown_files(str(tmp_path))

        assert len(files) == 3

    def test_ignore_non_markdown_files(self, tmp_path):
        """Test that non-markdown files are ignored."""
        (tmp_path / "test.md").write_text("content")
        (tmp_path / "test.txt").write_text("content")
        (tmp_path / "test.pdf").write_text("content")
        (tmp_path / "README").write_text("content")

        files = find_tasks.find_all_markdown_files(str(tmp_path))

        assert len(files) == 1
        assert files[0].endswith(".md")

    def test_ignore_hidden_directories(self, tmp_path):
        """Test that hidden directories are skipped."""
        (tmp_path / "visible.md").write_text("content")

        hidden_dir = tmp_path / ".hidden"
        hidden_dir.mkdir()
        (hidden_dir / "hidden.md").write_text("content")

        files = find_tasks.find_all_markdown_files(str(tmp_path))

        assert len(files) == 1
        assert ".hidden" not in files[0]

    def test_empty_directory(self, tmp_path):
        """Test empty directory returns no files."""
        files = find_tasks.find_all_markdown_files(str(tmp_path))

        assert len(files) == 0

    def test_files_are_sorted(self, tmp_path):
        """Test that returned files are sorted."""
        (tmp_path / "c.md").write_text("content")
        (tmp_path / "a.md").write_text("content")
        (tmp_path / "b.md").write_text("content")

        files = find_tasks.find_all_markdown_files(str(tmp_path))

        filenames = [os.path.basename(f) for f in files]
        assert filenames == ["a.md", "b.md", "c.md"]


class TestCategorizeStatus:
    """Tests for categorize_status function."""

    def test_completed_lowercase(self):
        """Test completed status with lowercase x."""
        assert find_tasks.categorize_status("x") == "completed"

    def test_completed_uppercase(self):
        """Test completed status with uppercase X."""
        assert find_tasks.categorize_status("X") == "completed"

    def test_rescheduled(self):
        """Test rescheduled status."""
        assert find_tasks.categorize_status(">") == "rescheduled"

    def test_canceled(self):
        """Test canceled status."""
        assert find_tasks.categorize_status("-") == "canceled"

    def test_pending(self):
        """Test pending status (space)."""
        assert find_tasks.categorize_status(" ") == "pending"

    def test_other_status(self):
        """Test other/unknown status."""
        assert find_tasks.categorize_status("?") == "other"
        assert find_tasks.categorize_status("!") == "other"


class TestMainFunction:
    """Integration tests for main function."""

    def test_main_with_tasks(self, tmp_path, capsys, monkeypatch):
        """Test main function with files containing tasks."""
        # Create test files
        file1 = tmp_path / "tasks.md"
        file1.write_text("""# Tasks
- [ ] Task 1
- [x] Task 2
""")

        file2 = tmp_path / "notes.md"
        file2.write_text("""# Notes
* [ ] Note task
""")

        # Mock sys.argv
        monkeypatch.setattr(sys, "argv", ["find_tasks.py", str(tmp_path)])

        # Run main
        find_tasks.main()

        # Check output
        captured = capsys.readouterr()
        assert "[[tasks]]" in captured.out
        assert "[[notes]]" in captured.out
        assert "Task 1" in captured.out
        assert "Task 2" in captured.out
        assert "Note task" in captured.out
        assert "Found 3 tasks in 2 files" in captured.out

    def test_main_no_tasks(self, tmp_path, capsys, monkeypatch):
        """Test main function with no tasks."""
        file1 = tmp_path / "empty.md"
        file1.write_text("# No tasks here\n")

        monkeypatch.setattr(sys, "argv", ["find_tasks.py", str(tmp_path)])

        find_tasks.main()

        captured = capsys.readouterr()
        assert "No tasks found" in captured.out

    def test_main_no_markdown_files(self, tmp_path, capsys, monkeypatch):
        """Test main function with no markdown files."""
        monkeypatch.setattr(sys, "argv", ["find_tasks.py", str(tmp_path)])

        with pytest.raises(SystemExit) as exc_info:
            find_tasks.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "No markdown files found" in captured.err

    def test_main_default_directory(self, capsys, monkeypatch, tmp_path):
        """Test main function uses current directory by default."""
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            file1 = tmp_path / "test.md"
            file1.write_text("- [ ] Test task\n")

            monkeypatch.setattr(sys, "argv", ["find_tasks.py"])

            find_tasks.main()

            captured = capsys.readouterr()
            assert "Test task" in captured.out
        finally:
            os.chdir(original_dir)

    def test_main_invalid_directory(self, capsys, monkeypatch):
        """Test main function with invalid directory."""
        monkeypatch.setattr(sys, "argv", ["find_tasks.py", "/nonexistent/path"])

        with pytest.raises(SystemExit) as exc_info:
            find_tasks.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "not a directory" in captured.err
