"""
Unit tests for scripts/tasks.py

Tests all task-related functions and classes.
"""

import sys
from datetime import date
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

import tasks as tasks_module
from tasks import Task, TaskStatus


# Tests for find_tasks_in_file function

def test_find_tasks_in_file_simple_uncompleted_task(tmp_path):
    """Test finding a simple uncompleted task."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [ ] Simple task 📅\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].line_no == 1
    assert tasks[0].text == "- [ ] Simple task 📅"
    assert tasks[0].status == TaskStatus.INCOMPLETE
    assert tasks[0].filename == str(test_file)


def test_find_tasks_in_file_completed_task_lowercase_x(tmp_path):
    """Test finding completed task with lowercase x."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [x] Completed task 📅\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.COMPLETED


def test_find_tasks_in_file_completed_task_uppercase_x(tmp_path):
    """Test finding completed task with uppercase X."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [X] Completed task 📅\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.COMPLETED


def test_find_tasks_in_file_rescheduled_task(tmp_path):
    """Test finding rescheduled task."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [>] Rescheduled task 📅\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.RESCHEDULED


def test_find_tasks_in_file_canceled_task(tmp_path):
    """Test finding canceled task."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [-] Canceled task 📅\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.CANCELED


def test_find_tasks_in_file_all_bullet_types(tmp_path):
    """Test all three bullet types (-, *, +)."""
    test_file = tmp_path / "test.md"
    content = """- [ ] Dash bullet 📅
* [ ] Asterisk bullet 📅
+ [ ] Plus bullet 📅
"""
    test_file.write_text(content)

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 3
    assert "Dash bullet" in tasks[0].text
    assert "Asterisk bullet" in tasks[1].text
    assert "Plus bullet" in tasks[2].text


def test_find_tasks_in_file_mixed_content(tmp_path):
    """Test file with tasks and non-task content."""
    test_file = tmp_path / "test.md"
    content = """# Header

Some text here.

- [ ] First task 📅
- Not a task (no brackets) 📅
- [x] Second task 📅

More text.

* [ ] Third task 📅
"""
    test_file.write_text(content)

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 3
    assert "First task" in tasks[0].text
    assert "Second task" in tasks[1].text
    assert "Third task" in tasks[2].text


def test_find_tasks_in_file_indented_tasks(tmp_path):
    """Test tasks with various indentation levels."""
    test_file = tmp_path / "test.md"
    content = """- [ ] No indent 📅
  - [ ] Two space indent 📅
    - [ ] Four space indent 📅
\t- [ ] Tab indent 📅
"""
    test_file.write_text(content)

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 4


def test_find_tasks_in_file_line_numbers(tmp_path):
    """Test that line numbers are correctly tracked."""
    test_file = tmp_path / "test.md"
    content = """Line 1
Line 2
- [ ] Task on line 3 📅
Line 4
Line 5
- [ ] Task on line 6 📅
"""
    test_file.write_text(content)

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 2
    assert tasks[0].line_no == 3
    assert tasks[1].line_no == 6


def test_find_tasks_in_file_empty_file(tmp_path):
    """Test empty file returns no tasks."""
    test_file = tmp_path / "test.md"
    test_file.write_text("")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 0


def test_find_tasks_in_file_no_tasks(tmp_path):
    """Test file with no tasks."""
    test_file = tmp_path / "test.md"
    content = """# Header

Just some text.
- Regular list item
* Another list item
"""
    test_file.write_text(content)

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 0


def test_find_tasks_in_file_invalid_task_formats(tmp_path):
    """Test that invalid task formats are not matched."""
    test_file = tmp_path / "test.md"
    content = """- [] Missing space in brackets 📅
- [  ] Two characters in brackets 📅
- [ab] Multiple characters 📅
-[ ] Missing space after dash 📅
- [ ]Missing space after brackets is OK but no text 📅
"""
    test_file.write_text(content)

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    # Only the last one should match (it has proper format)
    assert len(tasks) == 1


def test_find_tasks_in_file_nonexistent_file():
    """Test handling of nonexistent file."""
    tasks = tasks_module.find_tasks_in_file("/nonexistent/file.md")

    assert len(tasks) == 0


def test_find_tasks_in_file_task_attributes(tmp_path):
    """Test that Task object has all required attributes."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [x] Complete task 📅\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    task = tasks[0]

    # Check all attributes exist and have correct types
    assert isinstance(task.text, str)
    assert isinstance(task.status, TaskStatus)
    assert isinstance(task.filename, str)
    assert isinstance(task.line_no, int)


def test_find_tasks_in_file_with_start_date(tmp_path):
    """Test parsing task with start date."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [ ] Task with start 🛫 2026-02-13\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].start_date is not None
    assert tasks[0].start_date.year == 2026
    assert tasks[0].start_date.month == 2
    assert tasks[0].start_date.day == 13
    assert tasks[0].due_date is None
    assert tasks[0].completed_date is None


def test_find_tasks_in_file_with_due_date_spiral_calendar(tmp_path):
    """Test parsing task with due date using 🗓 emoji."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [ ] Task with due date 🗓 2026-03-15\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].due_date is not None
    assert tasks[0].due_date.year == 2026
    assert tasks[0].due_date.month == 3
    assert tasks[0].due_date.day == 15
    assert tasks[0].start_date is None
    assert tasks[0].completed_date is None


def test_find_tasks_in_file_with_due_date_calendar(tmp_path):
    """Test parsing task with due date using 📆 emoji."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [ ] Task with due date 📆 2026-04-20\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].due_date is not None
    assert tasks[0].due_date.year == 2026
    assert tasks[0].due_date.month == 4
    assert tasks[0].due_date.day == 20


def test_find_tasks_in_file_with_completed_date(tmp_path):
    """Test parsing task with completed date."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [x] Completed task 📅 ✅ 2026-02-10\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].completed_date is not None
    assert tasks[0].completed_date.year == 2026
    assert tasks[0].completed_date.month == 2
    assert tasks[0].completed_date.day == 10


def test_find_tasks_in_file_with_all_dates(tmp_path):
    """Test parsing task with all three dates."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [x] Full task 🛫 2026-02-01 🗓 2026-02-28 ✅ 2026-02-15\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    task = tasks[0]
    assert task.start_date.year == 2026
    assert task.start_date.month == 2
    assert task.start_date.day == 1
    assert task.due_date.year == 2026
    assert task.due_date.month == 2
    assert task.due_date.day == 28
    assert task.completed_date.year == 2026
    assert task.completed_date.month == 2
    assert task.completed_date.day == 15


def test_find_tasks_in_file_with_no_dates(tmp_path):
    """Test task with a bare due emoji and no dates."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [ ] Simple task without dates 📅\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].start_date is None
    assert tasks[0].due_date is None
    assert tasks[0].completed_date is None
    assert tasks[0].undated


def test_find_tasks_in_file_with_invalid_date_format(tmp_path):
    """Test that an invalid start date doesn't make a line a task."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [ ] Task with bad date 🛫 02-13-2026\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 0


def test_find_tasks_in_file_with_date_no_whitespace(tmp_path):
    """Test task with date immediately after emoji."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [ ] Task 🛫2026-02-13\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].start_date is not None
    assert tasks[0].start_date.day == 13


# Tests for TaskStatus enum

def test_task_status_enum_values():
    """Test that TaskStatus enum has all expected values."""
    assert TaskStatus.INCOMPLETE.value == "incomplete"
    assert TaskStatus.COMPLETED.value == "completed"
    assert TaskStatus.RESCHEDULED.value == "rescheduled"
    assert TaskStatus.CANCELED.value == "canceled"


# Tests for _extract_date function

def test_extract_date_start_date():
    """Test extracting start date with 🛫 emoji."""
    from datetime import date
    text = "Task 🛫 2026-02-13 description"
    result = tasks_module._extract_date(text, '🛫')
    assert result == date(2026, 2, 13)


def test_extract_date_due_date_spiral():
    """Test extracting due date with 🗓 emoji."""
    from datetime import date
    text = "Task 🗓 2026-03-15"
    result = tasks_module._extract_date(text, '🗓')
    assert result == date(2026, 3, 15)


def test_extract_date_due_date_calendar():
    """Test extracting due date with 📆 emoji."""
    from datetime import date
    text = "Task 📆 2026-04-20"
    result = tasks_module._extract_date(text, '📆')
    assert result == date(2026, 4, 20)


def test_extract_date_completed_date():
    """Test extracting completed date with ✅ emoji."""
    from datetime import date
    text = "Task ✅ 2026-02-10"
    result = tasks_module._extract_date(text, '✅')
    assert result == date(2026, 2, 10)


def test_extract_date_no_whitespace():
    """Test extracting date without whitespace after emoji."""
    from datetime import date
    text = "Task 🛫2026-12-25"
    result = tasks_module._extract_date(text, '🛫')
    assert result == date(2026, 12, 25)


def test_extract_date_not_found():
    """Test when emoji is not in text."""
    text = "Task without date"
    result = tasks_module._extract_date(text, '🛫')
    assert result is None


def test_extract_date_invalid_format():
    """Test with invalid date format."""
    text = "Task 🛫 02-13-2026"
    result = tasks_module._extract_date(text, '🛫')
    assert result is None


def test_extract_date_invalid_date():
    """Test with invalid date values."""
    text = "Task 🛫 2026-13-45"
    result = tasks_module._extract_date(text, '🛫')
    assert result is None


# Tests for _parse_task_dates function

def test_parse_task_dates_all_dates():
    """Test parsing all three dates."""
    from datetime import date
    text = "Task 🛫 2026-02-01 🗓 2026-02-28 ✅ 2026-02-15"
    start, due, completed = tasks_module._parse_task_dates(text)
    assert start == date(2026, 2, 1)
    assert due == date(2026, 2, 28)
    assert completed == date(2026, 2, 15)


def test_parse_task_dates_only_start_date():
    """Test parsing only start date."""
    from datetime import date
    text = "Task 🛫 2026-02-01"
    start, due, completed = tasks_module._parse_task_dates(text)
    assert start == date(2026, 2, 1)
    assert due is None
    assert completed is None


def test_parse_task_dates_only_due_date_spiral():
    """Test parsing only due date with 🗓."""
    from datetime import date
    text = "Task 🗓 2026-02-28"
    start, due, completed = tasks_module._parse_task_dates(text)
    assert start is None
    assert due == date(2026, 2, 28)
    assert completed is None


def test_parse_task_dates_only_due_date_calendar():
    """Test parsing only due date with 📆."""
    from datetime import date
    text = "Task 📆 2026-03-15"
    start, due, completed = tasks_module._parse_task_dates(text)
    assert start is None
    assert due == date(2026, 3, 15)
    assert completed is None


def test_parse_task_dates_no_dates():
    """Test parsing text with no dates."""
    text = "Task without any dates"
    start, due, completed = tasks_module._parse_task_dates(text)
    assert start is None
    assert due is None
    assert completed is None


def test_parse_task_dates_prefers_first_due_date_emoji():
    """Test that 🗓 is preferred over 📆 if both present."""
    from datetime import date
    text = "Task 🗓 2026-02-28 📆 2026-03-15"
    start, due, completed = tasks_module._parse_task_dates(text)
    # Should use the first emoji found (🗓)
    assert due == date(2026, 2, 28)


# Tests for _char_to_status function

def test_char_to_status_completed_lowercase():
    """Test completed status with lowercase x."""
    assert tasks_module._char_to_status("x") == TaskStatus.COMPLETED


def test_char_to_status_completed_uppercase():
    """Test completed status with uppercase X."""
    assert tasks_module._char_to_status("X") == TaskStatus.COMPLETED


def test_char_to_status_rescheduled():
    """Test rescheduled status."""
    assert tasks_module._char_to_status(">") == TaskStatus.RESCHEDULED


def test_char_to_status_canceled():
    """Test canceled status."""
    assert tasks_module._char_to_status("-") == TaskStatus.CANCELED


def test_char_to_status_incomplete():
    """Test incomplete status for common and unrecognized characters."""
    assert tasks_module._char_to_status(" ") == TaskStatus.INCOMPLETE
    assert tasks_module._char_to_status(".") == TaskStatus.INCOMPLETE
    assert tasks_module._char_to_status("o") == TaskStatus.INCOMPLETE
    assert tasks_module._char_to_status("O") == TaskStatus.INCOMPLETE
    assert tasks_module._char_to_status("/") == TaskStatus.INCOMPLETE
    # Unrecognized characters should also be incomplete
    assert tasks_module._char_to_status("?") == TaskStatus.INCOMPLETE
    assert tasks_module._char_to_status("!") == TaskStatus.INCOMPLETE
    assert tasks_module._char_to_status("*") == TaskStatus.INCOMPLETE


# Tests for categorize_status function

def test_categorize_status_completed_lowercase():
    """Test completed status with lowercase x."""
    assert tasks_module.categorize_status("x") == "completed"


def test_categorize_status_completed_uppercase():
    """Test completed status with uppercase X."""
    assert tasks_module.categorize_status("X") == "completed"


def test_categorize_status_rescheduled():
    """Test rescheduled status."""
    assert tasks_module.categorize_status(">") == "rescheduled"


def test_categorize_status_canceled():
    """Test canceled status."""
    assert tasks_module.categorize_status("-") == "canceled"


def test_categorize_status_incomplete():
    """Test incomplete status for all unrecognized characters."""
    assert tasks_module.categorize_status(" ") == "incomplete"
    assert tasks_module.categorize_status(".") == "incomplete"
    assert tasks_module.categorize_status("?") == "incomplete"
    assert tasks_module.categorize_status("!") == "incomplete"


# Tests for filter_tasks_by_status function

def test_filter_tasks_by_status_single_status():
    """Test filtering tasks by a single status."""
    tasks = [
        Task("- [ ] Incomplete", TaskStatus.INCOMPLETE, "file.md", 1),
        Task("- [x] Completed", TaskStatus.COMPLETED, "file.md", 2),
        Task("- [>] Rescheduled", TaskStatus.RESCHEDULED, "file.md", 3),
    ]

    result = tasks_module.filter_tasks_by_status(tasks, [TaskStatus.INCOMPLETE])

    assert len(result) == 1
    assert result[0].status == TaskStatus.INCOMPLETE


def test_filter_tasks_by_status_multiple_statuses():
    """Test filtering tasks by multiple statuses."""
    tasks = [
        Task("- [ ] Incomplete", TaskStatus.INCOMPLETE, "file.md", 1),
        Task("- [x] Completed", TaskStatus.COMPLETED, "file.md", 2),
        Task("- [>] Rescheduled", TaskStatus.RESCHEDULED, "file.md", 3),
        Task("- [-] Canceled", TaskStatus.CANCELED, "file.md", 4),
        Task("- [ ] Incomplete 2", TaskStatus.INCOMPLETE, "file.md", 5),
    ]

    result = tasks_module.filter_tasks_by_status(
        tasks,
        [TaskStatus.INCOMPLETE, TaskStatus.COMPLETED]
    )

    assert len(result) == 3
    assert result[0].text == "- [ ] Incomplete"
    assert result[1].text == "- [x] Completed"
    assert result[2].text == "- [ ] Incomplete 2"


def test_filter_tasks_by_status_all_statuses():
    """Test filtering with all statuses (returns all tasks)."""
    tasks = [
        Task("- [ ] Incomplete", TaskStatus.INCOMPLETE, "file.md", 1),
        Task("- [x] Completed", TaskStatus.COMPLETED, "file.md", 2),
        Task("- [>] Rescheduled", TaskStatus.RESCHEDULED, "file.md", 3),
        Task("- [-] Canceled", TaskStatus.CANCELED, "file.md", 4),
    ]

    result = tasks_module.filter_tasks_by_status(
        tasks,
        [TaskStatus.INCOMPLETE, TaskStatus.COMPLETED, TaskStatus.RESCHEDULED, TaskStatus.CANCELED]
    )

    assert len(result) == 4


def test_filter_tasks_by_status_no_matches():
    """Test filtering when no tasks match the statuses."""
    tasks = [
        Task("- [x] Completed", TaskStatus.COMPLETED, "file.md", 1),
        Task("- [>] Rescheduled", TaskStatus.RESCHEDULED, "file.md", 2),
    ]

    result = tasks_module.filter_tasks_by_status(tasks, [TaskStatus.INCOMPLETE])

    assert len(result) == 0


def test_filter_tasks_by_status_empty_task_list():
    """Test filtering with empty task list."""
    result = tasks_module.filter_tasks_by_status([], [TaskStatus.INCOMPLETE])

    assert len(result) == 0


def test_filter_tasks_by_status_empty_status_list():
    """Test filtering with empty status list (returns nothing)."""
    tasks = [
        Task("- [ ] Incomplete", TaskStatus.INCOMPLETE, "file.md", 1),
        Task("- [x] Completed", TaskStatus.COMPLETED, "file.md", 2),
    ]

    result = tasks_module.filter_tasks_by_status(tasks, [])

    assert len(result) == 0


def test_filter_tasks_by_status_preserves_order():
    """Test that filtering preserves task order."""
    tasks = [
        Task("- [ ] Task 1", TaskStatus.INCOMPLETE, "file.md", 1),
        Task("- [x] Task 2", TaskStatus.COMPLETED, "file.md", 2),
        Task("- [ ] Task 3", TaskStatus.INCOMPLETE, "file.md", 3),
        Task("- [ ] Task 4", TaskStatus.INCOMPLETE, "file.md", 4),
    ]

    result = tasks_module.filter_tasks_by_status(tasks, [TaskStatus.INCOMPLETE])

    assert len(result) == 3
    assert result[0].text == "- [ ] Task 1"
    assert result[1].text == "- [ ] Task 3"
    assert result[2].text == "- [ ] Task 4"


# Tests for find_tasks_in_file: task definition, due emojis, and tags

def test_find_tasks_in_file_plain_checkbox_skipped(tmp_path):
    """A checkbox with no due emoji or start date is not a task."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [ ] buy milk\n- [x] done item\n")

    assert tasks_module.find_tasks_in_file(str(test_file)) == []


def test_find_tasks_in_file_start_date_only_kept(tmp_path):
    """A checkbox with only a start date is a task."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [ ] draft outline 🛫 2026-10-05\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].start_date == date(2026, 10, 5)
    assert tasks[0].due_date is None
    assert not tasks[0].undated


@pytest.mark.parametrize('emoji', ['📅', '📆', '🗓'])
def test_find_tasks_in_file_each_due_emoji(tmp_path, emoji):
    """Each due emoji gives a due date."""
    test_file = tmp_path / "test.md"
    test_file.write_text(f"- [ ] a {emoji} 2026-10-01\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].due_date == date(2026, 10, 1)
    assert not tasks[0].undated


def test_find_tasks_in_file_due_emoji_variation_selector(tmp_path):
    """🗓 followed by an emoji variation selector still gives a due date."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [ ] a 🗓️ 2026-10-01\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert tasks[0].due_date == date(2026, 10, 1)


@pytest.mark.parametrize('emoji', ['📅', '📆', '🗓'])
def test_find_tasks_in_file_bare_due_emoji_undated(tmp_path, emoji):
    """A bare due emoji makes an undated task."""
    test_file = tmp_path / "test.md"
    test_file.write_text(f"- [ ] someday task {emoji}\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].due_date is None
    assert tasks[0].undated


def test_find_tasks_in_file_invalid_due_date_undated(tmp_path):
    """A due emoji followed by an impossible date makes an undated task."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [ ] bad date 📅 2026-02-30\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].due_date is None
    assert tasks[0].undated


def test_find_tasks_in_file_tags(tmp_path):
    """Tags are read from anywhere on the line, with aliases applied."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [ ] #aftr #design follow up 📅 2026-07-08\n"
                         "- [ ] #mtg prep 📅 2026-10-01 #Admin\n"
                         "- [ ] untagged 📅\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert tasks[0].tags == ['aftr', 'design']
    assert tasks[1].tags == ['meeting', 'Admin']
    assert tasks[2].tags == []


# Tests for Task.effective_due property

def test_task_effective_due_completed_with_completion_date():
    task = Task("- [x] ship it", TaskStatus.COMPLETED, "f.md", 1,
                due_date=date(2026, 10, 1), completed_date=date(2026, 10, 3))
    assert task.effective_due == date(2026, 10, 3)


def test_task_effective_due_completed_without_completion_date():
    task = Task("- [x] ship it", TaskStatus.COMPLETED, "f.md", 1,
                due_date=date(2026, 10, 1))
    assert task.effective_due == date(2026, 10, 1)


def test_task_effective_due_incomplete_ignores_completion_date():
    task = Task("- [ ] ship it", TaskStatus.INCOMPLETE, "f.md", 1,
                due_date=date(2026, 10, 1), completed_date=date(2026, 10, 3))
    assert task.effective_due == date(2026, 10, 1)
