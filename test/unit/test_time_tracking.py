"""
Unit tests for time_tracking module.
"""

import pytest
from datetime import time, timedelta
import sys
import os

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))

from time_tracking import (
    TimeLogEntry,
    TimeBlockEntry,
    EntryType,
    Tag,
    TagType,
    SPECIAL_TAGS,
    categorize_tag,
    parse_tags_from_text,
    _parse_time,
    _extract_tags_from_parentheses,
    _parse_arrived_entry,
    _parse_activity_entry,
    _parse_time_block_row,
    find_time_log_entries,
    find_time_block_entries,
    filter_entries_by_type,
    calculate_duration,
    calculate_total_time_by_tag,
    calculate_work_vs_nonwork,
    format_duration
)


# Tests for _parse_time function

def test_parse_time_morning_single_digit_hour():
    """Test parsing morning time with single digit hour."""
    result = _parse_time("8:00 am")
    assert result == time(8, 0)


def test_parse_time_morning_double_digit_hour():
    """Test parsing morning time with double digit hour."""
    result = _parse_time("10:30 am")
    assert result == time(10, 30)


def test_parse_time_afternoon():
    """Test parsing afternoon time."""
    result = _parse_time("2:45 pm")
    assert result == time(14, 45)


def test_parse_time_noon():
    """Test parsing noon (12:00 pm)."""
    result = _parse_time("12:00 pm")
    assert result == time(12, 0)


def test_parse_time_midnight():
    """Test parsing midnight (12:00 am)."""
    result = _parse_time("12:00 am")
    assert result == time(0, 0)


def test_parse_time_no_space_before_am():
    """Test parsing time without space before am/pm."""
    result = _parse_time("8:30am")
    assert result == time(8, 30)


def test_parse_time_invalid_hour():
    """Test parsing time with invalid hour."""
    result = _parse_time("13:00 am")
    assert result is None


def test_parse_time_invalid_minute():
    """Test parsing time with invalid minute."""
    result = _parse_time("8:60 am")
    assert result is None


def test_parse_time_invalid_format():
    """Test parsing time with invalid format."""
    result = _parse_time("not a time")
    assert result is None


# Tests for categorize_tag function

def test_categorize_tag_special_mtg():
    """Test categorizing #mtg as special tag."""
    result = categorize_tag("#mtg")
    assert result == TagType.SPECIAL


def test_categorize_tag_special_dev():
    """Test categorizing #dev as special tag."""
    result = categorize_tag("#dev")
    assert result == TagType.SPECIAL


def test_categorize_tag_activity():
    """Test categorizing custom tag as activity tag."""
    result = categorize_tag("#project-alpha")
    assert result == TagType.ACTIVITY


def test_categorize_tag_case_insensitive():
    """Test that tag categorization is case-insensitive."""
    result = categorize_tag("#MTG")
    assert result == TagType.SPECIAL


def test_categorize_tag_without_hash():
    """Test categorizing tag without # prefix."""
    result = categorize_tag("admin")
    assert result == TagType.SPECIAL


# Tests for parse_tags_from_text function

def test_parse_tags_from_text_single_tag():
    """Test extracting a single tag from text."""
    result = parse_tags_from_text("meeting #mtg at 9am")
    assert len(result) == 1
    assert result[0].text == "#mtg"
    assert result[0].tag_type == TagType.SPECIAL


def test_parse_tags_from_text_multiple_tags():
    """Test extracting multiple tags from text."""
    result = parse_tags_from_text("email #admin #communication")
    assert len(result) == 2
    assert result[0].text == "#admin"
    assert result[0].tag_type == TagType.SPECIAL
    assert result[1].text == "#communication"
    assert result[1].tag_type == TagType.ACTIVITY


def test_parse_tags_from_text_no_tags():
    """Test extracting tags when none present."""
    result = parse_tags_from_text("activity without tags")
    assert len(result) == 0


def test_parse_tags_from_text_with_hyphens():
    """Test extracting tags with hyphens."""
    result = parse_tags_from_text("work on #project-alpha and #sprint-2")
    assert len(result) == 2
    assert result[0].text == "#project-alpha"
    assert result[1].text == "#sprint-2"


# Tests for _extract_tags_from_parentheses function

def test_extract_tags_from_parentheses_single_tag():
    """Test extracting a single tag from parentheses."""
    result = _extract_tags_from_parentheses("activity (#admin)")
    assert len(result) == 1
    assert result[0].text == "#admin"
    assert result[0].tag_type == TagType.SPECIAL


def test_extract_tags_from_parentheses_multiple_tags():
    """Test extracting multiple tags from parentheses."""
    result = _extract_tags_from_parentheses("activity (#admin, #communication)")
    assert len(result) == 2
    assert result[0].text == "#admin"
    assert result[1].text == "#communication"


def test_extract_tags_from_parentheses_with_extra_whitespace():
    """Test extracting tags with extra whitespace."""
    result = _extract_tags_from_parentheses("activity (#admin,  #dev,#team)")
    assert len(result) == 3
    assert result[0].text == "#admin"
    assert result[1].text == "#dev"
    assert result[2].text == "#team"


def test_extract_tags_from_parentheses_no_tags():
    """Test extracting tags when none in parentheses."""
    result = _extract_tags_from_parentheses("activity without tags")
    assert len(result) == 0


# Tests for _parse_arrived_entry function

def test_parse_arrived_entry_with_time():
    """Test parsing arrived entry with time."""
    entry = _parse_arrived_entry("- arrived: 8:00 am", "test.md", 1)

    assert entry is not None
    assert entry.entry_type == EntryType.ARRIVED
    assert entry.start_time == time(8, 0)
    assert entry.filename == "test.md"
    assert entry.line_no == 1


def test_parse_arrived_entry_without_time():
    """Test parsing arrived entry without time."""
    entry = _parse_arrived_entry("- arrived:", "test.md", 1)

    assert entry is not None
    assert entry.entry_type == EntryType.ARRIVED
    assert entry.start_time is None


def test_parse_arrived_entry_with_whitespace():
    """Test parsing arrived entry with extra whitespace."""
    entry = _parse_arrived_entry("  - arrived:  8:30 am  ", "test.md", 1)

    assert entry is not None
    assert entry.entry_type == EntryType.ARRIVED
    assert entry.start_time == time(8, 30)


def test_parse_arrived_entry_not_arrived():
    """Test that non-arrived entries return None."""
    entry = _parse_arrived_entry("- regular task", "test.md", 1)
    assert entry is None


# Tests for _parse_activity_entry function

def test_parse_activity_entry_with_tags_and_times():
    """Test parsing activity entry with tags and time range."""
    line = "- email review (#admin, #communication) 8:15 am - 8:45 am"
    entry = _parse_activity_entry(line, "test.md", 1)

    assert entry is not None
    assert entry.entry_type == EntryType.ACTIVITY
    assert entry.activity == "email review"
    assert len(entry.tags) == 2
    assert entry.tags[0].text == "#admin"
    assert entry.tags[1].text == "#communication"
    assert entry.start_time == time(8, 15)
    assert entry.end_time == time(8, 45)


def test_parse_activity_entry_no_tags():
    """Test parsing activity entry without tags."""
    line = "- standup meeting 9:00 am - 9:30 am"
    entry = _parse_activity_entry(line, "test.md", 1)

    assert entry is not None
    assert entry.activity == "standup meeting"
    assert len(entry.tags) == 0
    assert entry.start_time == time(9, 0)
    assert entry.end_time == time(9, 30)


def test_parse_activity_entry_no_times():
    """Test parsing activity entry without times."""
    line = "- lunch break (#pers)"
    entry = _parse_activity_entry(line, "test.md", 1)

    assert entry is not None
    assert entry.activity == "lunch break"
    assert len(entry.tags) == 1
    assert entry.tags[0].text == "#pers"
    assert entry.start_time is None
    assert entry.end_time is None


def test_parse_activity_entry_only_activity_text():
    """Test parsing activity entry with only activity text."""
    line = "- working on project"
    entry = _parse_activity_entry(line, "test.md", 1)

    assert entry is not None
    assert entry.activity == "working on project"
    assert len(entry.tags) == 0
    assert entry.start_time is None
    assert entry.end_time is None


# Tests for find_time_log_entries function

def test_find_time_log_entries_in_log_section(tmp_path):
    """Test finding time log entries in Log section."""
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "# Daily Note\n"
        "\n"
        "### Log\n"
        "\n"
        "- arrived: 8:00 am\n"
        "- email review (#admin) 8:15 am - 8:45 am\n"
        "\n"
        "### Notes\n"
        "\n"
        "- not a time entry\n"
    )

    entries = find_time_log_entries(str(test_file))

    assert len(entries) == 2
    assert entries[0].entry_type == EntryType.ARRIVED
    assert entries[1].entry_type == EntryType.ACTIVITY
    assert entries[1].activity == "email review"


def test_find_time_log_entries_no_log_section(tmp_path):
    """Test finding time log entries when no Log section exists."""
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "# Daily Note\n"
        "\n"
        "- arrived: 8:00 am\n"
        "- some task\n"
    )

    entries = find_time_log_entries(str(test_file))
    assert len(entries) == 0


def test_find_time_log_entries_empty_log_section(tmp_path):
    """Test finding time log entries in empty Log section."""
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "# Daily Note\n"
        "\n"
        "### Log\n"
        "\n"
        "### Notes\n"
    )

    entries = find_time_log_entries(str(test_file))
    assert len(entries) == 0


def test_find_time_log_entries_multiple_entries(tmp_path):
    """Test finding multiple time log entries."""
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "### Log\n"
        "\n"
        "- arrived: 8:00 am\n"
        "- email (#admin) 8:15 am - 8:30 am\n"
        "- standup (#mtg) 9:00 am - 9:15 am\n"
        "- coding (#dev) 9:30 am - 11:00 am\n"
    )

    entries = find_time_log_entries(str(test_file))

    assert len(entries) == 4
    assert entries[0].entry_type == EntryType.ARRIVED
    assert all(e.entry_type == EntryType.ACTIVITY for e in entries[1:])


# Tests for filter_entries_by_type function

def test_filter_entries_by_type_arrived_only():
    """Test filtering to show only ARRIVED entries."""
    entries = [
        TimeLogEntry(EntryType.ARRIVED, "- arrived: 8:00 am", "test.md", 1, time(8, 0)),
        TimeLogEntry(EntryType.ACTIVITY, "- work", "test.md", 2, time(8, 15), time(9, 0)),
        TimeLogEntry(EntryType.ACTIVITY, "- meeting", "test.md", 3, time(9, 0), time(10, 0)),
    ]

    filtered = filter_entries_by_type(entries, [EntryType.ARRIVED])

    assert len(filtered) == 1
    assert filtered[0].entry_type == EntryType.ARRIVED


def test_filter_entries_by_type_activity_only():
    """Test filtering to show only ACTIVITY entries."""
    entries = [
        TimeLogEntry(EntryType.ARRIVED, "- arrived: 8:00 am", "test.md", 1, time(8, 0)),
        TimeLogEntry(EntryType.ACTIVITY, "- work", "test.md", 2, time(8, 15), time(9, 0)),
        TimeLogEntry(EntryType.ACTIVITY, "- meeting", "test.md", 3, time(9, 0), time(10, 0)),
    ]

    filtered = filter_entries_by_type(entries, [EntryType.ACTIVITY])

    assert len(filtered) == 2
    assert all(e.entry_type == EntryType.ACTIVITY for e in filtered)


# Tests for _parse_time_block_row function

def test_parse_time_block_row_with_plan_and_actual():
    """Test parsing time block row with both plan and actual."""
    line = "|  8:00am | email #admin        | meeting #mtg        |"
    entry = _parse_time_block_row(line, "test.md", 1)

    assert entry is not None
    assert entry.time_slot == time(8, 0)
    assert entry.plan == "email #admin"
    assert entry.actual == "meeting #mtg"
    assert len(entry.plan_tags) == 1
    assert entry.plan_tags[0].text == "#admin"
    assert len(entry.actual_tags) == 1
    assert entry.actual_tags[0].text == "#mtg"


def test_parse_time_block_row_plan_only():
    """Test parsing time block row with only plan."""
    line = "|  9:00am | coding #dev         |                     |"
    entry = _parse_time_block_row(line, "test.md", 1)

    assert entry is not None
    assert entry.time_slot == time(9, 0)
    assert entry.plan == "coding #dev"
    assert entry.actual is None
    assert len(entry.plan_tags) == 1
    assert entry.plan_tags[0].text == "#dev"
    assert len(entry.actual_tags) == 0


def test_parse_time_block_row_actual_only():
    """Test parsing time block row with only actual."""
    line = "| 10:00am |                     | break #break        |"
    entry = _parse_time_block_row(line, "test.md", 1)

    assert entry is not None
    assert entry.time_slot == time(10, 0)
    assert entry.plan is None
    assert entry.actual == "break #break"
    assert len(entry.plan_tags) == 0
    assert len(entry.actual_tags) == 1
    assert entry.actual_tags[0].text == "#break"


def test_parse_time_block_row_no_tags():
    """Test parsing time block row without tags."""
    line = "|  2:00pm | write documentation |                     |"
    entry = _parse_time_block_row(line, "test.md", 1)

    assert entry is not None
    assert entry.time_slot == time(14, 0)
    assert entry.plan == "write documentation"
    assert len(entry.plan_tags) == 0
    assert len(entry.actual_tags) == 0


def test_parse_time_block_row_multiple_tags():
    """Test parsing time block row with multiple tags."""
    line = "|  3:00pm | review #admin #urgent | coding #dev #project-x |"
    entry = _parse_time_block_row(line, "test.md", 1)

    assert entry is not None
    assert len(entry.plan_tags) == 2
    assert entry.plan_tags[0].text == "#admin"
    assert entry.plan_tags[1].text == "#urgent"
    assert len(entry.actual_tags) == 2
    assert entry.actual_tags[0].text == "#dev"
    assert entry.actual_tags[1].text == "#project-x"


def test_parse_time_block_row_not_table():
    """Test that non-table rows return None."""
    line = "This is not a table row"
    entry = _parse_time_block_row(line, "test.md", 1)
    assert entry is None


# Tests for find_time_block_entries function

def test_find_time_block_entries_in_time_block_section(tmp_path):
    """Test finding time block entries in Time Block section."""
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "# Daily Note\n"
        "\n"
        "### Time Block\n"
        "\n"
        "| Time    | Plan                | Actual              |\n"
        "| ------- | -------------------- | ------------------- |\n"
        "|  8:00am | email #admin        | meeting #mtg        |\n"
        "|  8:15am | coding #dev         |                     |\n"
        "\n"
        "### Notes\n"
    )

    entries = find_time_block_entries(str(test_file))

    assert len(entries) == 2
    assert entries[0].time_slot == time(8, 0)
    assert entries[1].time_slot == time(8, 15)


def test_find_time_block_entries_no_section(tmp_path):
    """Test finding time block entries when no Time Block section exists."""
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "# Daily Note\n"
        "\n"
        "|  8:00am | email #admin        |                     |\n"
    )

    entries = find_time_block_entries(str(test_file))
    assert len(entries) == 0


def test_find_time_block_entries_empty_table(tmp_path):
    """Test finding time block entries in empty table."""
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "### Time Block\n"
        "\n"
        "| Time    | Plan                | Actual              |\n"
        "| ------- | -------------------- | ------------------- |\n"
        "\n"
        "### Notes\n"
    )

    entries = find_time_block_entries(str(test_file))
    assert len(entries) == 0


# Tests for calculate_duration function

def test_calculate_duration_simple():
    """Test calculating duration between two times."""
    start = time(8, 0)
    end = time(9, 30)
    duration = calculate_duration(start, end)
    assert duration == timedelta(hours=1, minutes=30)


def test_calculate_duration_same_hour():
    """Test calculating duration within same hour."""
    start = time(8, 15)
    end = time(8, 45)
    duration = calculate_duration(start, end)
    assert duration == timedelta(minutes=30)


def test_calculate_duration_across_noon():
    """Test calculating duration across noon."""
    start = time(11, 30)
    end = time(13, 15)  # 1:15 PM
    duration = calculate_duration(start, end)
    assert duration == timedelta(hours=1, minutes=45)


def test_calculate_duration_across_midnight():
    """Test calculating duration when end is before start (assumes next day)."""
    start = time(23, 30)
    end = time(1, 0)
    duration = calculate_duration(start, end)
    assert duration == timedelta(hours=1, minutes=30)


# Tests for calculate_total_time_by_tag function

def test_calculate_total_time_by_tag_single_tag():
    """Test calculating total time for a single tag."""
    entries = [
        TimeLogEntry(
            EntryType.ACTIVITY, "- work", "test.md", 1,
            time(8, 0), time(9, 0), "work",
            [Tag("#dev", TagType.SPECIAL)]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- more work", "test.md", 2,
            time(9, 0), time(10, 30), "more work",
            [Tag("#dev", TagType.SPECIAL)]
        ),
    ]

    result = calculate_total_time_by_tag(entries)

    assert "#dev" in result
    assert result["#dev"] == timedelta(hours=2, minutes=30)


def test_calculate_total_time_by_tag_multiple_tags():
    """Test calculating total time for multiple tags."""
    entries = [
        TimeLogEntry(
            EntryType.ACTIVITY, "- email", "test.md", 1,
            time(8, 0), time(8, 30), "email",
            [Tag("#admin", TagType.SPECIAL)]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- meeting", "test.md", 2,
            time(9, 0), time(10, 0), "meeting",
            [Tag("#mtg", TagType.SPECIAL)]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- coding", "test.md", 3,
            time(10, 0), time(12, 0), "coding",
            [Tag("#dev", TagType.SPECIAL)]
        ),
    ]

    result = calculate_total_time_by_tag(entries)

    assert result["#admin"] == timedelta(minutes=30)
    assert result["#mtg"] == timedelta(hours=1)
    assert result["#dev"] == timedelta(hours=2)


def test_calculate_total_time_by_tag_entry_with_multiple_tags():
    """Test entry with multiple tags counts toward all tags."""
    entries = [
        TimeLogEntry(
            EntryType.ACTIVITY, "- work", "test.md", 1,
            time(8, 0), time(9, 0), "work",
            [Tag("#dev", TagType.SPECIAL), Tag("#project-x", TagType.ACTIVITY)]
        ),
    ]

    result = calculate_total_time_by_tag(entries)

    assert result["#dev"] == timedelta(hours=1)
    assert result["#project-x"] == timedelta(hours=1)


def test_calculate_total_time_by_tag_skip_entries_without_times():
    """Test that entries without start/end times are skipped."""
    entries = [
        TimeLogEntry(
            EntryType.ACTIVITY, "- work", "test.md", 1,
            None, None, "work",
            [Tag("#dev", TagType.SPECIAL)]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- more work", "test.md", 2,
            time(9, 0), time(10, 0), "more work",
            [Tag("#dev", TagType.SPECIAL)]
        ),
    ]

    result = calculate_total_time_by_tag(entries)

    # Only the second entry should be counted
    assert result["#dev"] == timedelta(hours=1)


# Tests for calculate_work_vs_nonwork function

def test_calculate_work_vs_nonwork_work_only():
    """Test calculating work vs non-work with only work entries."""
    entries = [
        TimeLogEntry(
            EntryType.ACTIVITY, "- coding", "test.md", 1,
            time(8, 0), time(10, 0), "coding",
            [Tag("#dev", TagType.SPECIAL)]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- meeting", "test.md", 2,
            time(10, 0), time(11, 0), "meeting",
            [Tag("#mtg", TagType.SPECIAL)]
        ),
    ]

    work, nonwork = calculate_work_vs_nonwork(entries)

    assert work == timedelta(hours=3)
    assert nonwork == timedelta()


def test_calculate_work_vs_nonwork_mixed():
    """Test calculating work vs non-work with mixed entries."""
    entries = [
        TimeLogEntry(
            EntryType.ACTIVITY, "- coding", "test.md", 1,
            time(8, 0), time(10, 0), "coding",
            [Tag("#dev", TagType.SPECIAL)]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- lunch", "test.md", 2,
            time(12, 0), time(13, 0), "lunch",
            [Tag("#break", TagType.SPECIAL)]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- personal", "test.md", 3,
            time(17, 0), time(18, 0), "personal",
            [Tag("#pers", TagType.SPECIAL)]
        ),
    ]

    work, nonwork = calculate_work_vs_nonwork(entries)

    assert work == timedelta(hours=2)
    assert nonwork == timedelta(hours=2)


def test_calculate_work_vs_nonwork_untagged():
    """Test that untagged or uncategorized entries don't count."""
    entries = [
        TimeLogEntry(
            EntryType.ACTIVITY, "- something", "test.md", 1,
            time(8, 0), time(9, 0), "something",
            [Tag("#unknown", TagType.ACTIVITY)]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- work", "test.md", 2,
            time(9, 0), time(10, 0), "work",
            [Tag("#dev", TagType.SPECIAL)]
        ),
    ]

    work, nonwork = calculate_work_vs_nonwork(entries)

    # Only the #dev entry should count
    assert work == timedelta(hours=1)
    assert nonwork == timedelta()


# Tests for format_duration function

def test_format_duration_hours_and_minutes():
    """Test formatting duration with hours and minutes."""
    duration = timedelta(hours=2, minutes=30)
    result = format_duration(duration)
    assert result == "2h 30m"


def test_format_duration_hours_only():
    """Test formatting duration with only hours."""
    duration = timedelta(hours=3)
    result = format_duration(duration)
    assert result == "3h 0m"


def test_format_duration_minutes_only():
    """Test formatting duration with only minutes."""
    duration = timedelta(minutes=45)
    result = format_duration(duration)
    assert result == "45m"


def test_format_duration_zero():
    """Test formatting zero duration."""
    duration = timedelta()
    result = format_duration(duration)
    assert result == "0m"
