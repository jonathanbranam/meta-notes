"""
Unit tests for scripts/find_tasks.py

Tests the CLI report generation functions.
"""

import os
import sys
from pathlib import Path
from datetime import date, timedelta

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


# Tests for get_task_relevant_date function

def test_get_task_relevant_date_with_due_date():
    """Test getting relevant date when due_date is present."""
    task_date = date(2026, 2, 15)
    task = Task("- [ ] Task", TaskStatus.INCOMPLETE, "file.md", 1, due_date=task_date)

    result = find_tasks.get_task_relevant_date(task)

    assert result == task_date


def test_get_task_relevant_date_with_start_date_only():
    """Test getting relevant date when only start_date is present."""
    task_date = date(2026, 2, 10)
    task = Task("- [ ] Task", TaskStatus.INCOMPLETE, "file.md", 1, start_date=task_date)

    result = find_tasks.get_task_relevant_date(task)

    assert result == task_date


def test_get_task_relevant_date_with_both_dates():
    """Test that due_date takes precedence over start_date."""
    start = date(2026, 2, 10)
    due = date(2026, 2, 15)
    task = Task("- [ ] Task", TaskStatus.INCOMPLETE, "file.md", 1, start_date=start, due_date=due)

    result = find_tasks.get_task_relevant_date(task)

    assert result == due


def test_get_task_relevant_date_with_no_dates():
    """Test getting relevant date when no dates are present."""
    task = Task("- [ ] Task", TaskStatus.INCOMPLETE, "file.md", 1)

    result = find_tasks.get_task_relevant_date(task)

    assert result is None


# Tests for categorize_task_by_date function

def test_categorize_task_by_date_past():
    """Test categorizing a task with a past due date."""
    today = date(2026, 2, 13)
    week_end = today + timedelta(days=7)
    past_date = date(2026, 2, 1)
    task = Task("- [ ] Task", TaskStatus.INCOMPLETE, "file.md", 1, due_date=past_date)

    result = find_tasks.categorize_task_by_date(task, today, week_end)

    assert result == 'past_or_current'


def test_categorize_task_by_date_current_week():
    """Test categorizing a task due within the current week."""
    today = date(2026, 2, 13)
    week_end = today + timedelta(days=7)
    this_week = date(2026, 2, 18)
    task = Task("- [ ] Task", TaskStatus.INCOMPLETE, "file.md", 1, due_date=this_week)

    result = find_tasks.categorize_task_by_date(task, today, week_end)

    assert result == 'past_or_current'


def test_categorize_task_by_date_future():
    """Test categorizing a task due in the future (beyond this week)."""
    today = date(2026, 2, 13)
    week_end = today + timedelta(days=7)
    future_date = date(2026, 3, 1)
    task = Task("- [ ] Task", TaskStatus.INCOMPLETE, "file.md", 1, due_date=future_date)

    result = find_tasks.categorize_task_by_date(task, today, week_end)

    assert result == 'future'


def test_categorize_task_by_date_no_date():
    """Test categorizing a task without any dates."""
    today = date(2026, 2, 13)
    week_end = today + timedelta(days=7)
    task = Task("- [ ] Task", TaskStatus.INCOMPLETE, "file.md", 1)

    result = find_tasks.categorize_task_by_date(task, today, week_end)

    assert result == 'no_date'


def test_categorize_task_by_date_uses_start_date():
    """Test categorizing uses start_date when due_date is not present."""
    today = date(2026, 2, 13)
    week_end = today + timedelta(days=7)
    start_date = date(2026, 3, 1)
    task = Task("- [ ] Task", TaskStatus.INCOMPLETE, "file.md", 1, start_date=start_date)

    result = find_tasks.categorize_task_by_date(task, today, week_end)

    assert result == 'future'


# Tests for collect_categorized_tasks function

def test_collect_categorized_tasks_empty_directory(tmp_path):
    """Test collecting tasks from empty directory."""
    today = date(2026, 2, 13)
    result = find_tasks.collect_categorized_tasks(str(tmp_path), today)

    assert result == {
        'past_or_current': [],
        'future': [],
        'no_date': []
    }


def test_collect_categorized_tasks_with_mixed_dates(tmp_path):
    """Test collecting tasks with various date configurations."""
    # 2026-02-13 is a Friday, so week_end will be 2026-02-15 (Sunday)
    today = date(2026, 2, 13)
    past = date(2026, 2, 8).isoformat()  # Last Sunday (past)
    current = date(2026, 2, 14).isoformat()  # Tomorrow Saturday (this week)
    future = date(2026, 2, 16).isoformat()  # Next Monday (after this Sunday)

    file1 = tmp_path / "tasks.md"
    file1.write_text(f"""# Tasks
- [ ] Past task 🗓 {past}
- [ ] Current week task 🗓 {current}
- [ ] Future task 🗓 {future}
- [ ] No date task
""")

    result = find_tasks.collect_categorized_tasks(str(tmp_path), today)

    # Check that we have tasks in each category
    assert len(result['past_or_current']) == 1
    assert len(result['past_or_current'][0][1]) == 2  # 2 tasks (past + current)
    assert len(result['future']) == 1
    assert len(result['future'][0][1]) == 1  # 1 task
    assert len(result['no_date']) == 1
    assert len(result['no_date'][0][1]) == 1  # 1 task


def test_collect_categorized_tasks_filters_completed(tmp_path):
    """Test that completed tasks are not collected."""
    # 2026-02-13 is a Friday, so week_end will be 2026-02-15 (Sunday)
    today = date(2026, 2, 13)
    task_date = date(2026, 2, 14).isoformat()  # Tomorrow Saturday (this week)

    file1 = tmp_path / "tasks.md"
    file1.write_text(f"""# Tasks
- [ ] Incomplete 🗓 {task_date}
- [x] Completed 🗓 {task_date}
""")

    result = find_tasks.collect_categorized_tasks(str(tmp_path), today)

    # Only incomplete task should be collected
    assert len(result['past_or_current']) == 1
    assert len(result['past_or_current'][0][1]) == 1
    assert "Incomplete" in result['past_or_current'][0][1][0].text


# Tests for format_section function

def test_format_section_with_tasks(tmp_path):
    """Test formatting a section with tasks."""
    filepath = str(tmp_path / "test.md")
    tasks = [
        Task("- [ ] Task 1", TaskStatus.INCOMPLETE, filepath, 1),
        Task("- [ ] Task 2", TaskStatus.INCOMPLETE, filepath, 2),
    ]
    file_tasks = [(filepath, tasks)]

    lines = find_tasks.format_section('no_date', '# No Date', file_tasks, str(tmp_path))

    assert "# No Date" in lines
    assert "## [[test]]" in lines
    assert "- [ ] Task 1" in lines
    assert "- [ ] Task 2" in lines


def test_format_section_empty_list(tmp_path):
    """Test formatting a section with no tasks."""
    lines = find_tasks.format_section('no_date', '# No Date', [], str(tmp_path))

    assert len(lines) == 0


def test_format_section_multiple_files(tmp_path):
    """Test formatting a section with multiple files."""
    file1 = str(tmp_path / "test1.md")
    file2 = str(tmp_path / "test2.md")
    tasks1 = [Task("- [ ] Task 1", TaskStatus.INCOMPLETE, file1, 1)]
    tasks2 = [Task("- [ ] Task 2", TaskStatus.INCOMPLETE, file2, 1)]
    file_tasks = [(file1, tasks1), (file2, tasks2)]

    lines = find_tasks.format_section('no_date', '# No Date', file_tasks, str(tmp_path))

    output = "\n".join(lines)
    assert "# No Date" in output
    assert "## [[test1]]" in output
    assert "## [[test2]]" in output
    assert "- [ ] Task 1" in output
    assert "- [ ] Task 2" in output


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
    """Test generating report with incomplete tasks (no dates)."""
    today = date(2026, 2, 13)
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

    lines = find_tasks.generate_report(str(tmp_path), today)

    # Should include both files with only incomplete tasks in "No Date" section
    output = "\n".join(lines)
    assert "# No Date" in output
    assert "[[tasks]]" in output
    assert "[[notes]]" in output
    assert "Incomplete task 1" in output
    assert "Incomplete task 2" in output
    assert "Note task" in output
    assert "Completed task" not in output  # Should be filtered out
    assert "Found 3 incomplete tasks in 2 file sections" in output


def test_generate_report_no_incomplete_tasks(tmp_path):
    """Test generating report when no incomplete tasks exist."""
    today = date(2026, 2, 13)
    file1 = tmp_path / "tasks.md"
    file1.write_text("""# Tasks
- [x] Completed task
- [>] Rescheduled task
- [-] Canceled task
""")

    lines = find_tasks.generate_report(str(tmp_path), today)

    assert len(lines) == 1
    assert lines[0] == "No incomplete tasks found in any markdown files."


def test_generate_report_file_with_only_completed_tasks(tmp_path):
    """Test that files with only completed tasks are not shown."""
    today = date(2026, 2, 13)
    file1 = tmp_path / "incomplete.md"
    file1.write_text("- [ ] Incomplete task\n")

    file2 = tmp_path / "completed.md"
    file2.write_text("- [x] Completed task\n")

    lines = find_tasks.generate_report(str(tmp_path), today)

    output = "\n".join(lines)
    assert "# No Date" in output
    assert "[[incomplete]]" in output
    assert "[[completed]]" not in output  # File should not appear
    assert "Found 1 incomplete task in 1 file section" in output


def test_generate_report_no_markdown_files(tmp_path):
    """Test generating report with no markdown files."""
    today = date(2026, 2, 13)
    lines = find_tasks.generate_report(str(tmp_path), today)

    assert len(lines) == 1
    assert lines[0] == "No markdown files found."


def test_generate_report_empty_files(tmp_path):
    """Test generating report with empty files."""
    today = date(2026, 2, 13)
    file1 = tmp_path / "empty.md"
    file1.write_text("# Header\n\nJust text, no tasks.\n")

    lines = find_tasks.generate_report(str(tmp_path), today)

    assert len(lines) == 1
    assert lines[0] == "No incomplete tasks found in any markdown files."


def test_generate_report_with_all_three_sections(tmp_path):
    """Test generating report with tasks in all three date categories."""
    # 2026-02-13 is a Friday, so week_end will be 2026-02-15 (Sunday)
    today = date(2026, 2, 13)
    past = date(2026, 2, 8).isoformat()  # Last Sunday (past)
    current = date(2026, 2, 14).isoformat()  # Tomorrow Saturday (this week)
    future = date(2026, 2, 16).isoformat()  # Next Monday (after this Sunday)

    file1 = tmp_path / "tasks.md"
    file1.write_text(f"""# Tasks
- [ ] Past task 🗓 {past}
- [ ] Current week task 🗓 {current}
- [ ] Future task 🗓 {future}
- [ ] No date task
""")

    lines = find_tasks.generate_report(str(tmp_path), today)
    output = "\n".join(lines)

    # Check all three sections are present
    assert "# Past & Current Week" in output
    assert "# Future (>1 Week)" in output
    assert "# No Date" in output

    # Check tasks are in output
    assert "Past task" in output
    assert "Current week task" in output
    assert "Future task" in output
    assert "No date task" in output

    # Check summary
    assert "Found 4 incomplete tasks" in output


def test_generate_report_only_future_tasks(tmp_path):
    """Test report with only future tasks."""
    # 2026-02-13 is a Friday, so week_end will be 2026-02-15 (Sunday)
    today = date(2026, 2, 13)
    future = date(2026, 2, 16).isoformat()  # Next Monday (after this Sunday)

    file1 = tmp_path / "tasks.md"
    file1.write_text(f"""# Tasks
- [ ] Future task 1 🗓 {future}
- [ ] Future task 2 🗓 {future}
""")

    lines = find_tasks.generate_report(str(tmp_path), today)
    output = "\n".join(lines)

    # Only future section should be present
    assert "# Future (>1 Week)" in output
    assert "# Past & Current Week" not in output
    assert "# No Date" not in output
    assert "Future task 1" in output
    assert "Future task 2" in output


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
    assert "# No Date" in captured.out
    assert "[[tasks]]" in captured.out
    assert "Task 1" in captured.out
    assert "Task 3" in captured.out
    assert "Task 2" not in captured.out  # Completed task should not appear
    assert "Found 2 incomplete tasks in 1 file section" in captured.out


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
    assert "# No Date" in captured.out
    assert "[[incomplete]]" in captured.out
    assert "[[completed]]" not in captured.out
    assert "[[mixed]]" in captured.out
    assert "Found 2 incomplete tasks in 2 file sections" in captured.out


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
