"""
Unit tests for time_tracking module.
"""

import pytest
from datetime import time, timedelta
import sys
import os

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))

from datetime import date

from time_tracking import (
    TimeLogEntry,
    TimeBlockEntry,
    EntryType,
    Tag,
    TAG_GROUPS,
    TAG_TO_GROUP,
    get_tag_group,
    parse_tags_from_text,
    _parse_time,
    _parse_time_block_row,
    _parse_time_log_lines,
    find_time_log_entries,
    find_time_block_entries,
    filter_entries_by_type,
    calculate_duration,
    calculate_total_time_by_tag,
    calculate_time_by_group,
    calculate_work_vs_nonwork,
    format_duration,
    format_duration_long,
    analyze_work_day,
    format_week_summary,
    is_off_plan,
    compare_plan_vs_actual,
    calculate_plan_adherence
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


# Tests for get_tag_group function

def test_get_tag_group_mtg():
    """Test that #mtg maps to Meeting group."""
    assert get_tag_group("#mtg") == "Meeting"


def test_get_tag_group_meeting():
    """Test that #meeting maps to Meeting group."""
    assert get_tag_group("#meeting") == "Meeting"


def test_get_tag_group_personal_aliases():
    """Test that #per, #personal, and #off-task map to Personal group."""
    assert get_tag_group("#per") == "Personal"
    assert get_tag_group("#personal") == "Personal"
    assert get_tag_group("#off-task") == "Personal"


def test_get_tag_group_break():
    """Test that #break maps to Break group."""
    assert get_tag_group("#break") == "Break"


def test_get_tag_group_unknown():
    """Test that an unknown tag returns None."""
    assert get_tag_group("#project-alpha") is None
    assert get_tag_group("#dev") is None


def test_get_tag_group_case_insensitive():
    """Test that group lookup is case-insensitive."""
    assert get_tag_group("#MTG") == "Meeting"
    assert get_tag_group("#Meeting") == "Meeting"


def test_get_tag_group_without_hash():
    """Test that tag without # prefix still works."""
    assert get_tag_group("mtg") == "Meeting"


# Tests for parse_tags_from_text function

def test_parse_tags_from_text_single_tag():
    """Test extracting a single tag from text."""
    result = parse_tags_from_text("meeting #mtg at 9am")
    assert len(result) == 1
    assert result[0].text == "#mtg"


def test_parse_tags_from_text_multiple_tags():
    """Test extracting multiple tags from text."""
    result = parse_tags_from_text("email #admin #communication")
    assert len(result) == 2
    assert result[0].text == "#admin"
    assert result[1].text == "#communication"


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

# Tests for _parse_time_log_lines function

def test_parse_time_log_lines_in_log_section():
    """Test finding time log entries in Log section."""
    lines = [
        "# Daily Note\n",
        "\n",
        "### Log\n",
        "\n",
        "- email review #admin\n",
        "  * start: 2026-02-14 Fri 08:15\n",
        "  * end:   2026-02-14 Fri 08:45\n",
        "\n",
        "### Notes\n",
        "\n",
        "- not a time entry\n",
    ]

    entries = _parse_time_log_lines(lines, "test.md")

    assert len(entries) == 1
    assert entries[0].entry_type == EntryType.ACTIVITY
    assert entries[0].activity == "email review"
    assert len(entries[0].tags) == 1
    assert entries[0].tags[0].text == "#admin"


def test_parse_time_log_lines_no_log_section():
    """Test finding time log entries when no Log section exists."""
    lines = [
        "# Daily Note\n",
        "\n",
        "- arrived: 8:00 am\n",
        "- some task\n",
    ]

    entries = _parse_time_log_lines(lines, "test.md")
    assert len(entries) == 0


def test_parse_time_log_lines_empty_log_section():
    """Test finding time log entries in empty Log section."""
    lines = [
        "# Daily Note\n",
        "\n",
        "### Log\n",
        "\n",
        "### Notes\n",
    ]

    entries = _parse_time_log_lines(lines, "test.md")
    assert len(entries) == 0


def test_parse_time_log_lines_multiple_entries():
    """Test finding multiple time log entries."""
    lines = [
        "### Log\n",
        "\n",
        "- email #admin\n",
        "  * start: 2026-02-14 Fri 08:15\n",
        "  * end:   2026-02-14 Fri 08:30\n",
        "- standup #mtg\n",
        "  * start: 2026-02-14 Fri 09:00\n",
        "  * end:   2026-02-14 Fri 09:15\n",
        "- coding #dev\n",
        "  * start: 2026-02-14 Fri 09:30\n",
        "  * end:   2026-02-14 Fri 11:00\n",
    ]

    entries = _parse_time_log_lines(lines, "test.md")

    assert len(entries) == 3
    assert all(e.entry_type == EntryType.ACTIVITY for e in entries)


# Tests for find_time_log_entries function

def test_find_time_log_entries_reads_file(tmp_path):
    """Test that find_time_log_entries reads a file and returns entries."""
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "### Log\n"
        "\n"
        "- email review #admin\n"
        "  * start: 2026-02-14 Fri 08:15\n"
        "  * end:   2026-02-14 Fri 08:45\n"
    )

    entries = find_time_log_entries(str(test_file))

    assert len(entries) == 1
    assert entries[0].activity == "email review"


def test_find_time_log_entries_missing_file():
    """Test that find_time_log_entries returns empty list for missing file."""
    entries = find_time_log_entries("/nonexistent/path/test.md")
    assert entries == []


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
            [Tag("#dev")]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- more work", "test.md", 2,
            time(9, 0), time(10, 30), "more work",
            [Tag("#dev")]
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
            [Tag("#admin")]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- meeting", "test.md", 2,
            time(9, 0), time(10, 0), "meeting",
            [Tag("#mtg")]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- coding", "test.md", 3,
            time(10, 0), time(12, 0), "coding",
            [Tag("#dev")]
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
            [Tag("#dev"), Tag("#project-x")]
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
            [Tag("#dev")]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- more work", "test.md", 2,
            time(9, 0), time(10, 0), "more work",
            [Tag("#dev")]
        ),
    ]

    result = calculate_total_time_by_tag(entries)

    # Only the second entry should be counted
    assert result["#dev"] == timedelta(hours=1)


# Tests for calculate_time_by_group function

def test_calculate_time_by_group_merges_aliases():
    """Test that alias tags (#mtg and #meeting) merge into one group total."""
    entries = [
        TimeLogEntry(
            EntryType.ACTIVITY, "- standup", "test.md", 1,
            time(9, 0), time(9, 30), "standup",
            [Tag("#mtg")]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- team sync", "test.md", 2,
            time(10, 0), time(11, 0), "team sync",
            [Tag("#meeting")]
        ),
    ]

    result = calculate_time_by_group(entries)

    assert result["Meeting"] == timedelta(hours=1, minutes=30)
    assert "Personal" not in result
    assert "Break" not in result


def test_calculate_time_by_group_no_double_count():
    """Test that an entry with both #mtg and #meeting counts Meeting only once."""
    entries = [
        TimeLogEntry(
            EntryType.ACTIVITY, "- meeting", "test.md", 1,
            time(9, 0), time(10, 0), "meeting",
            [Tag("#mtg"), Tag("#meeting")]
        ),
    ]

    result = calculate_time_by_group(entries)

    assert result["Meeting"] == timedelta(hours=1)


def test_calculate_time_by_group_multiple_groups():
    """Test entries belonging to different groups."""
    entries = [
        TimeLogEntry(
            EntryType.ACTIVITY, "- standup", "test.md", 1,
            time(9, 0), time(9, 30), "standup",
            [Tag("#mtg")]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- lunch break", "test.md", 2,
            time(12, 0), time(12, 30), "lunch break",
            [Tag("#break")]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- personal errand", "test.md", 3,
            time(17, 0), time(17, 30), "personal errand",
            [Tag("#personal")]
        ),
    ]

    result = calculate_time_by_group(entries)

    assert result["Meeting"] == timedelta(minutes=30)
    assert result["Break"] == timedelta(minutes=30)
    assert result["Personal"] == timedelta(minutes=30)


def test_calculate_time_by_group_ungrouped_tags_ignored():
    """Test that tags not in any group don't appear in the result."""
    entries = [
        TimeLogEntry(
            EntryType.ACTIVITY, "- coding", "test.md", 1,
            time(9, 0), time(11, 0), "coding",
            [Tag("#dev"), Tag("#project-x")]
        ),
    ]

    result = calculate_time_by_group(entries)

    assert len(result) == 0


def test_calculate_time_by_group_skips_entries_without_times():
    """Test that entries without start/end times are skipped."""
    entries = [
        TimeLogEntry(
            EntryType.ACTIVITY, "- meeting", "test.md", 1,
            None, None, "meeting",
            [Tag("#mtg")]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- standup", "test.md", 2,
            time(9, 0), time(9, 30), "standup",
            [Tag("#mtg")]
        ),
    ]

    result = calculate_time_by_group(entries)

    assert result["Meeting"] == timedelta(minutes=30)


# Tests for calculate_work_vs_nonwork function

def test_calculate_work_vs_nonwork_work_only():
    """Test calculating work vs non-work with only work entries."""
    entries = [
        TimeLogEntry(
            EntryType.ACTIVITY, "- coding", "test.md", 1,
            time(8, 0), time(10, 0), "coding",
            [Tag("#dev")]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- meeting", "test.md", 2,
            time(10, 0), time(11, 0), "meeting",
            [Tag("#mtg")]
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
            [Tag("#dev")]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- lunch", "test.md", 2,
            time(12, 0), time(13, 0), "lunch",
            [Tag("#break")]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- personal", "test.md", 3,
            time(17, 0), time(18, 0), "personal",
            [Tag("#pers")]
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
            [Tag("#unknown")]
        ),
        TimeLogEntry(
            EntryType.ACTIVITY, "- work", "test.md", 2,
            time(9, 0), time(10, 0), "work",
            [Tag("#dev")]
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


# Tests for is_off_plan function

def test_is_off_plan_plan_wrapped_in_tildes():
    """Test that a plan wrapped in ~tildes~ is off-plan."""
    block = TimeBlockEntry(time(8, 0), "~email #admin~", "did something else", [], [], "test.md", 1)
    assert is_off_plan(block) is True


def test_is_off_plan_actual_has_off_plan_tag():
    """Test that #off-plan tag in actual marks block as off-plan."""
    block = TimeBlockEntry(time(8, 0), "coding #dev", "browsing internet #off-plan", [], [], "test.md", 1)
    assert is_off_plan(block) is True


def test_is_off_plan_on_plan():
    """Test that a normal planned block is not off-plan."""
    block = TimeBlockEntry(time(8, 0), "coding #dev", "coding #dev", [], [], "test.md", 1)
    assert is_off_plan(block) is False


def test_is_off_plan_tilde_in_actual_not_off_plan():
    """Test that tildes in actual (without #off-plan) do not mark block as off-plan."""
    block = TimeBlockEntry(time(8, 0), "coding #dev", "~something~", [], [], "test.md", 1)
    assert is_off_plan(block) is False


def test_is_off_plan_none():
    """Test that None block returns False."""
    assert is_off_plan(None) is False


def test_is_off_plan_empty_plan():
    """Test that block with empty plan is not off-plan (it is unplanned)."""
    block = TimeBlockEntry(time(8, 0), "", "some activity", [], [], "test.md", 1)
    assert is_off_plan(block) is False


# Tests for compare_plan_vs_actual function

def test_compare_plan_vs_actual_all_on_plan():
    """Test that blocks with plans and no off-plan indicators are on-plan."""
    blocks = [
        TimeBlockEntry(time(8, 0), "coding #dev", "anything", [], [], "test.md", 1),
        TimeBlockEntry(time(8, 15), "email #admin", None, [], [], "test.md", 2),
        TimeBlockEntry(time(8, 30), "meeting #mtg", "", [], [], "test.md", 3),
    ]

    on_plan, off_plan, unplanned = compare_plan_vs_actual(blocks)

    assert on_plan == 3
    assert off_plan == 0
    assert unplanned == 0


def test_compare_plan_vs_actual_plan_with_tildes():
    """Test that plan wrapped in tildes is off-plan."""
    blocks = [
        TimeBlockEntry(time(8, 0), "coding #dev", "coding #dev", [], [], "test.md", 1),
        TimeBlockEntry(time(8, 15), "~email #admin~", "emergency call", [], [], "test.md", 2),
    ]

    on_plan, off_plan, unplanned = compare_plan_vs_actual(blocks)

    assert on_plan == 1
    assert off_plan == 1
    assert unplanned == 0


def test_compare_plan_vs_actual_off_plan_tag_in_actual():
    """Test that #off-plan tag in actual marks block as off-plan."""
    blocks = [
        TimeBlockEntry(time(8, 0), "coding #dev", "coding #dev", [], [], "test.md", 1),
        TimeBlockEntry(time(8, 15), "email #admin", "browsing internet #off-plan", [], [], "test.md", 2),
    ]

    on_plan, off_plan, unplanned = compare_plan_vs_actual(blocks)

    assert on_plan == 1
    assert off_plan == 1
    assert unplanned == 0


def test_compare_plan_vs_actual_unplanned():
    """Test that blocks without plans are counted as unplanned."""
    blocks = [
        TimeBlockEntry(time(8, 0), "coding #dev", "coding #dev", [], [], "test.md", 1),
        TimeBlockEntry(time(8, 15), None, "something unexpected", [], [], "test.md", 2),
        TimeBlockEntry(time(8, 30), "", "another unplanned thing", [], [], "test.md", 3),
    ]

    on_plan, off_plan, unplanned = compare_plan_vs_actual(blocks)

    assert on_plan == 1
    assert off_plan == 0
    assert unplanned == 2


def test_compare_plan_vs_actual_actual_content_ignored():
    """Test that actual content does not affect on-plan status when no off-plan indicators."""
    blocks = [
        TimeBlockEntry(time(8, 0), "coding #dev", "completely different thing", [], [], "test.md", 1),
        TimeBlockEntry(time(8, 15), "email", "email #admin #urgent", [], [], "test.md", 2),
    ]

    on_plan, off_plan, unplanned = compare_plan_vs_actual(blocks)

    assert on_plan == 2
    assert off_plan == 0


# Tests for calculate_plan_adherence function

def test_calculate_plan_adherence_perfect():
    """Test plan adherence calculation with 100% on-plan."""
    blocks = [
        TimeBlockEntry(time(8, 0), "coding #dev", "coding #dev", [], [], "test.md", 1),
        TimeBlockEntry(time(8, 15), "email #admin", "email #admin", [], [], "test.md", 2),
    ]

    stats = calculate_plan_adherence(blocks)

    assert stats['on_plan_percent'] == 100.0
    assert stats['off_plan_percent'] == 0.0
    assert stats['unplanned_percent'] == 0.0
    assert stats['on_plan_count'] == 2
    assert stats['off_plan_count'] == 0
    assert stats['unplanned_count'] == 0
    assert stats['total_blocks'] == 2


def test_calculate_plan_adherence_mixed():
    """Test plan adherence calculation with mixed results."""
    blocks = [
        TimeBlockEntry(time(8, 0), "coding #dev", "coding #dev", [], [], "test.md", 1),
        TimeBlockEntry(time(8, 15), "~email #admin~", "emergency meeting", [], [], "test.md", 2),
        TimeBlockEntry(time(8, 30), "meeting #mtg", "distracted #off-plan", [], [], "test.md", 3),
        TimeBlockEntry(time(8, 45), None, "random thing", [], [], "test.md", 4),
    ]

    stats = calculate_plan_adherence(blocks)

    assert stats['on_plan_count'] == 1
    assert stats['off_plan_count'] == 2
    assert stats['unplanned_count'] == 1
    assert stats['total_blocks'] == 4
    assert stats['on_plan_percent'] == 25.0
    assert stats['off_plan_percent'] == 50.0
    assert stats['unplanned_percent'] == 25.0


def test_calculate_plan_adherence_empty():
    """Test plan adherence calculation with no blocks."""
    blocks = []

    stats = calculate_plan_adherence(blocks)

    assert stats['on_plan_percent'] == 0.0
    assert stats['off_plan_percent'] == 0.0
    assert stats['unplanned_percent'] == 0.0
    assert stats['total_blocks'] == 0


# Tests for format_duration_long function

def test_format_duration_long_hours_and_minutes():
    """Test formatting duration with hours and minutes."""
    assert format_duration_long(timedelta(hours=7, minutes=46)) == "7 hr 46 min"


def test_format_duration_long_minutes_only():
    """Test formatting duration with only minutes."""
    assert format_duration_long(timedelta(minutes=30)) == "30 min"


def test_format_duration_long_zero_minutes():
    """Test formatting duration with whole hours."""
    assert format_duration_long(timedelta(hours=8)) == "8 hr 0 min"


# Tests for analyze_work_day function

def _make_entry(start_h, start_m, end_h, end_m, tags, d=date(2026, 2, 16)):
    """Helper to build a TimeLogEntry for a given day."""
    from datetime import datetime
    start_dt = datetime(d.year, d.month, d.day, start_h, start_m)
    end_dt = datetime(d.year, d.month, d.day, end_h, end_m)
    return TimeLogEntry(
        EntryType.ACTIVITY, "- entry", "test.md", 1,
        start_dt, end_dt, "entry",
        [Tag(t) for t in tags]
    )


def test_analyze_work_day_basic():
    """Test basic work day analysis with no personal time."""
    entries = [
        _make_entry(8, 0, 9, 0, ['#dev']),
        _make_entry(9, 0, 10, 0, ['#mtg']),
        _make_entry(10, 0, 17, 0, ['#dev']),
    ]
    result = analyze_work_day(entries)

    assert result is not None
    assert result['start'].hour == 8
    assert result['end'].hour == 17
    assert result['total_time'] == timedelta(hours=9)
    assert result['hours_worked'] == timedelta(hours=9)


def test_analyze_work_day_strips_personal_from_start():
    """Test that #personal entries at the start are excluded from the work window."""
    entries = [
        _make_entry(8, 0, 10, 0, ['#personal']),   # 2 hrs personal at start
        _make_entry(10, 0, 17, 0, ['#dev']),
    ]
    result = analyze_work_day(entries)

    assert result is not None
    assert result['start'].hour == 10
    assert result['end'].hour == 17
    assert result['total_time'] == timedelta(hours=7)
    assert result['hours_worked'] == timedelta(hours=7)


def test_analyze_work_day_strips_personal_from_end():
    """Test that #personal entries at the end are excluded from the work window."""
    entries = [
        _make_entry(9, 0, 17, 0, ['#dev']),
        _make_entry(17, 0, 18, 0, ['#per']),       # personal at end
    ]
    result = analyze_work_day(entries)

    assert result is not None
    assert result['start'].hour == 9
    assert result['end'].hour == 17
    assert result['total_time'] == timedelta(hours=8)
    assert result['hours_worked'] == timedelta(hours=8)


def test_analyze_work_day_break_not_stripped_from_boundary():
    """Test that #break at the start is NOT stripped — it counts as at work."""
    entries = [
        _make_entry(8, 0, 8, 30, ['#break']),      # break at start, not stripped
        _make_entry(8, 30, 17, 0, ['#dev']),
    ]
    result = analyze_work_day(entries)

    assert result is not None
    assert result['start'].hour == 8
    assert result['end'].hour == 17
    assert result['total_time'] == timedelta(hours=9)
    assert result['hours_worked'] == timedelta(hours=8, minutes=30)


def test_analyze_work_day_break_excluded_from_hours_worked():
    """Test that #break mid-day is included in total time but not hours worked."""
    entries = [
        _make_entry(9, 0, 12, 0, ['#dev']),
        _make_entry(12, 0, 12, 30, ['#break']),
        _make_entry(12, 30, 17, 0, ['#dev']),
    ]
    result = analyze_work_day(entries)

    assert result is not None
    assert result['total_time'] == timedelta(hours=8)
    assert result['hours_worked'] == timedelta(hours=7, minutes=30)


def test_analyze_work_day_off_task_not_stripped_but_not_worked():
    """Test that #off-task is inside the boundary but excluded from hours worked."""
    entries = [
        _make_entry(9, 0, 10, 0, ['#off-task']),   # not stripped from boundary
        _make_entry(10, 0, 17, 0, ['#dev']),
    ]
    result = analyze_work_day(entries)

    assert result is not None
    assert result['start'].hour == 9    # off-task keeps the early start
    assert result['hours_worked'] == timedelta(hours=7)


def test_analyze_work_day_no_entries():
    """Test that an empty day returns None."""
    assert analyze_work_day([]) is None


def test_analyze_work_day_all_personal():
    """Test that a day of only personal time returns None."""
    entries = [
        _make_entry(8, 0, 17, 0, ['#personal']),
    ]
    assert analyze_work_day(entries) is None


# Tests for format_week_summary function

def test_format_week_summary_with_data():
    """Test formatting a week summary with data for some days."""
    from datetime import datetime
    days = [
        (date(2026, 2, 16), {
            'start': datetime(2026, 2, 16, 8, 20),
            'end': datetime(2026, 2, 16, 17, 0),
            'total_time': timedelta(hours=8, minutes=40),
            'hours_worked': timedelta(hours=7, minutes=46),
        }),
        (date(2026, 2, 17), None),
    ]

    result = format_week_summary(days)

    assert '2026-02-16 Mon' in result
    assert 'time tracked:   08:20 - 17:00' in result
    assert 'hours worked:   7 hr 46 min' in result
    assert 'total time:     8 hr 40 min' in result
    assert '2026-02-17 Tue' in result
    assert '(no data)' in result
    assert 'Weekly total worked: 7 hr 46 min' in result


def test_format_week_summary_no_data():
    """Test formatting a week summary with no data for any day."""
    days = [(date(2026, 2, 16 + i), None) for i in range(5)]

    result = format_week_summary(days)

    assert result.count('(no data)') == 5
    assert 'Weekly total worked: 0 min' in result
