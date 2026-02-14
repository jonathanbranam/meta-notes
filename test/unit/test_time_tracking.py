"""
Unit tests for time_tracking module.
"""

import pytest
from datetime import time
import sys
import os

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))

from time_tracking import (
    TimeLogEntry,
    EntryType,
    _parse_time,
    _extract_tags,
    _parse_arrived_entry,
    _parse_activity_entry,
    find_time_log_entries,
    filter_entries_by_type
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


# Tests for _extract_tags function

def test_extract_tags_single_tag():
    """Test extracting a single tag."""
    result = _extract_tags("activity (#admin)")
    assert result == ["#admin"]


def test_extract_tags_multiple_tags():
    """Test extracting multiple tags."""
    result = _extract_tags("activity (#admin, #communication)")
    assert result == ["#admin", "#communication"]


def test_extract_tags_with_extra_whitespace():
    """Test extracting tags with extra whitespace."""
    result = _extract_tags("activity (#admin,  #communication,#team)")
    assert result == ["#admin", "#communication", "#team"]


def test_extract_tags_no_tags():
    """Test extracting tags when none present."""
    result = _extract_tags("activity without tags")
    assert result == []


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
    assert entry.tags == ["#admin", "#communication"]
    assert entry.start_time == time(8, 15)
    assert entry.end_time == time(8, 45)


def test_parse_activity_entry_no_tags():
    """Test parsing activity entry without tags."""
    line = "- standup meeting 9:00 am - 9:30 am"
    entry = _parse_activity_entry(line, "test.md", 1)

    assert entry is not None
    assert entry.activity == "standup meeting"
    assert entry.tags == []
    assert entry.start_time == time(9, 0)
    assert entry.end_time == time(9, 30)


def test_parse_activity_entry_no_times():
    """Test parsing activity entry without times."""
    line = "- lunch break (#pers)"
    entry = _parse_activity_entry(line, "test.md", 1)

    assert entry is not None
    assert entry.activity == "lunch break"
    assert entry.tags == ["#pers"]
    assert entry.start_time is None
    assert entry.end_time is None


def test_parse_activity_entry_only_activity_text():
    """Test parsing activity entry with only activity text."""
    line = "- working on project"
    entry = _parse_activity_entry(line, "test.md", 1)

    assert entry is not None
    assert entry.activity == "working on project"
    assert entry.tags == []
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
