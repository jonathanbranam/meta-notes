"""
Unit tests for scripts/find_tasks.py

Tests the CLI report generation functions.
"""

import os
import sys
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

import find_tasks
from tasks import Task, TaskStatus


# Tests for filter_incomplete_tasks function

def test_filter_incomplete_tasks_all_incomplete():
    """Test filtering when all tasks are incomplete."""
    tasks = [
        Task("- [ ] Task 1", TaskStatus.INCOMPLETE, "file.md", 1),
        Task("- [ ] Task 2", TaskStatus.INCOMPLETE, "file.md", 2),
    ]

    result = find_tasks.filter_incomplete_tasks(tasks)

    assert len(result) == 2
    assert all(t.status == TaskStatus.INCOMPLETE for t in result)


def test_filter_incomplete_tasks_mixed_statuses():
    """Test filtering with mixed task statuses."""
    tasks = [
        Task("- [ ] Incomplete", TaskStatus.INCOMPLETE, "file.md", 1),
        Task("- [x] Completed", TaskStatus.COMPLETED, "file.md", 2),
        Task("- [>] Rescheduled", TaskStatus.RESCHEDULED, "file.md", 3),
        Task("- [ ] Another incomplete", TaskStatus.INCOMPLETE, "file.md", 4),
        Task("- [-] Canceled", TaskStatus.CANCELED, "file.md", 5),
    ]

    result = find_tasks.filter_incomplete_tasks(tasks)

    assert len(result) == 2
    assert result[0].text == "- [ ] Incomplete"
    assert result[1].text == "- [ ] Another incomplete"


def test_filter_incomplete_tasks_no_incomplete():
    """Test filtering when there are no incomplete tasks."""
    tasks = [
        Task("- [x] Completed", TaskStatus.COMPLETED, "file.md", 1),
        Task("- [>] Rescheduled", TaskStatus.RESCHEDULED, "file.md", 2),
        Task("- [-] Canceled", TaskStatus.CANCELED, "file.md", 3),
    ]

    result = find_tasks.filter_incomplete_tasks(tasks)

    assert len(result) == 0


def test_filter_incomplete_tasks_empty_list():
    """Test filtering with empty task list."""
    result = find_tasks.filter_incomplete_tasks([])

    assert len(result) == 0


# Tests for format_file_tasks function

def test_format_file_tasks_with_tasks(tmp_path):
    """Test formatting tasks from a file."""
    filepath = str(tmp_path / "test.md")
    tasks = [
        Task("- [ ] Task 1", TaskStatus.INCOMPLETE, filepath, 1),
        Task("- [ ] Task 2", TaskStatus.INCOMPLETE, filepath, 2),
    ]

    lines = find_tasks.format_file_tasks(filepath, tasks, str(tmp_path))

    assert len(lines) == 4  # header, empty line, 2 tasks
    assert lines[0] == "## [[test]]"
    assert lines[1] == ""
    assert lines[2] == "- [ ] Task 1"
    assert lines[3] == "- [ ] Task 2"


def test_format_file_tasks_empty_list(tmp_path):
    """Test formatting with no tasks."""
    filepath = str(tmp_path / "test.md")

    lines = find_tasks.format_file_tasks(filepath, [], str(tmp_path))

    assert len(lines) == 0


def test_format_file_tasks_nested_file(tmp_path):
    """Test formatting with nested file path."""
    subdir = tmp_path / "notes" / "work"
    filepath = str(subdir / "tasks.md")
    tasks = [
        Task("- [ ] Task", TaskStatus.INCOMPLETE, filepath, 1),
    ]

    lines = find_tasks.format_file_tasks(filepath, tasks, str(tmp_path))

    assert lines[0] == "## [[notes/work/tasks]]"


# Tests for generate_report function

def test_generate_report_with_incomplete_tasks(tmp_path):
    """Test generating report with incomplete tasks."""
    file1 = tmp_path / "tasks.md"
    file1.write_text("""# Tasks
- [ ] Incomplete task 1
- [x] Completed task
- [ ] Incomplete task 2
""")

    file2 = tmp_path / "notes.md"
    file2.write_text("""# Notes
- [ ] Note task
""")

    lines = find_tasks.generate_report(str(tmp_path))

    # Should include both files with only incomplete tasks
    output = "\n".join(lines)
    assert "[[tasks]]" in output
    assert "[[notes]]" in output
    assert "Incomplete task 1" in output
    assert "Incomplete task 2" in output
    assert "Note task" in output
    assert "Completed task" not in output  # Should be filtered out
    assert "Found 3 incomplete tasks in 2 files" in output


def test_generate_report_no_incomplete_tasks(tmp_path):
    """Test generating report when no incomplete tasks exist."""
    file1 = tmp_path / "tasks.md"
    file1.write_text("""# Tasks
- [x] Completed task
- [>] Rescheduled task
- [-] Canceled task
""")

    lines = find_tasks.generate_report(str(tmp_path))

    assert len(lines) == 1
    assert lines[0] == "No incomplete tasks found in any markdown files."


def test_generate_report_file_with_only_completed_tasks(tmp_path):
    """Test that files with only completed tasks are not shown."""
    file1 = tmp_path / "incomplete.md"
    file1.write_text("- [ ] Incomplete task\n")

    file2 = tmp_path / "completed.md"
    file2.write_text("- [x] Completed task\n")

    lines = find_tasks.generate_report(str(tmp_path))

    output = "\n".join(lines)
    assert "[[incomplete]]" in output
    assert "[[completed]]" not in output  # File should not appear
    assert "Found 1 incomplete task" in output


def test_generate_report_no_markdown_files(tmp_path):
    """Test generating report with no markdown files."""
    lines = find_tasks.generate_report(str(tmp_path))

    assert len(lines) == 1
    assert lines[0] == "No markdown files found."


def test_generate_report_empty_files(tmp_path):
    """Test generating report with empty files."""
    file1 = tmp_path / "empty.md"
    file1.write_text("# Header\n\nJust text, no tasks.\n")

    lines = find_tasks.generate_report(str(tmp_path))

    assert len(lines) == 1
    assert lines[0] == "No incomplete tasks found in any markdown files."


# Tests for main function (integration tests)

def test_main_with_incomplete_tasks(tmp_path, capsys, monkeypatch):
    """Test main function with incomplete tasks."""
    file1 = tmp_path / "tasks.md"
    file1.write_text("""# Tasks
- [ ] Task 1
- [x] Task 2
- [ ] Task 3
""")

    monkeypatch.setattr(sys, "argv", ["find_tasks.py", str(tmp_path)])

    find_tasks.main()

    captured = capsys.readouterr()
    assert "[[tasks]]" in captured.out
    assert "Task 1" in captured.out
    assert "Task 3" in captured.out
    assert "Task 2" not in captured.out  # Completed task should not appear
    assert "Found 2 incomplete tasks in 1 file" in captured.out


def test_main_no_incomplete_tasks(tmp_path, capsys, monkeypatch):
    """Test main function with no incomplete tasks."""
    file1 = tmp_path / "completed.md"
    file1.write_text("""# Tasks
- [x] Completed 1
- [x] Completed 2
""")

    monkeypatch.setattr(sys, "argv", ["find_tasks.py", str(tmp_path)])

    find_tasks.main()

    captured = capsys.readouterr()
    assert "No incomplete tasks found" in captured.out


def test_main_mixed_files(tmp_path, capsys, monkeypatch):
    """Test main with files having different task types."""
    file1 = tmp_path / "incomplete.md"
    file1.write_text("- [ ] Incomplete\n")

    file2 = tmp_path / "completed.md"
    file2.write_text("- [x] Completed\n")

    file3 = tmp_path / "mixed.md"
    file3.write_text("""- [ ] Incomplete 2
- [x] Completed 2
- [>] Rescheduled
""")

    monkeypatch.setattr(sys, "argv", ["find_tasks.py", str(tmp_path)])

    find_tasks.main()

    captured = capsys.readouterr()
    # Only files with incomplete tasks should appear
    assert "[[incomplete]]" in captured.out
    assert "[[completed]]" not in captured.out
    assert "[[mixed]]" in captured.out
    assert "Found 2 incomplete tasks in 2 files" in captured.out


def test_main_invalid_directory(capsys, monkeypatch):
    """Test main function with invalid directory."""
    monkeypatch.setattr(sys, "argv", ["find_tasks.py", "/nonexistent/path"])

    with pytest.raises(SystemExit) as exc_info:
        find_tasks.main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "not a directory" in captured.err


def test_main_default_directory(capsys, monkeypatch, tmp_path):
    """Test main function uses current directory by default."""
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
