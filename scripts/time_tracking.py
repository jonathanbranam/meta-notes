"""
Time tracking module for markdown files.

Handles time log parsing, time block parsing, and time calculations.
"""

from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
from typing import Optional
import re
import sys


class EntryType(Enum):
    """Enum representing the type of time log entry."""
    ARRIVED = "arrived"
    ACTIVITY = "activity"


@dataclass
class TimeLogEntry:
    """Represents a time log entry found in a markdown file.

    Time log entries can be:
    - Special 'arrived' entry: - arrived: HH:MM am/pm
    - Activity entry: - activity description (tags) HH:MM am/pm - HH:MM am/pm

    Examples:
        - arrived: 8:00 am
        - email review (#admin, #communication) 8:15 am - 8:45 am
        - standup meeting (#mtg, #team) 9:00 am - 9:30 am
    """
    entry_type: EntryType
    text: str
    filename: str
    line_no: int
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    activity: Optional[str] = None
    tags: list[str] = None

    def __post_init__(self):
        """Initialize tags list if None."""
        if self.tags is None:
            self.tags = []


def _parse_time(time_str: str) -> Optional[time]:
    """
    Parse a time string in 12-hour format (e.g., '8:00 am', '2:30 pm').

    Args:
        time_str: Time string to parse (e.g., '8:00 am', '2:30 pm', '10:15am').

    Returns:
        A time object if successfully parsed, None otherwise.
    """
    # Normalize the time string (remove extra spaces, make lowercase)
    time_str = time_str.strip().lower()

    # Pattern: H:MM am/pm or HH:MM am/pm (with optional space before am/pm)
    pattern = re.compile(r'^(\d{1,2}):(\d{2})\s*(am|pm)$')
    match = pattern.match(time_str)

    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2))
    meridiem = match.group(3)

    # Validate hour and minute
    if hour < 1 or hour > 12 or minute < 0 or minute > 59:
        return None

    # Convert to 24-hour format
    if meridiem == 'pm' and hour != 12:
        hour += 12
    elif meridiem == 'am' and hour == 12:
        hour = 0

    try:
        return time(hour=hour, minute=minute)
    except ValueError:
        return None


def _extract_tags(text: str) -> list[str]:
    """
    Extract tags from text enclosed in parentheses.

    Tags are comma-separated and start with #.
    Example: "(#admin, #communication)" returns ["#admin", "#communication"]

    Args:
        text: Text to search for tags.

    Returns:
        List of tags found (including the # prefix).
    """
    # Pattern: parentheses containing comma-separated tags
    pattern = re.compile(r'\(([^)]+)\)')
    match = pattern.search(text)

    if not match:
        return []

    tags_str = match.group(1)
    # Split by comma and strip whitespace
    tags = [tag.strip() for tag in tags_str.split(',')]

    return tags


def _parse_arrived_entry(line: str, filename: str, line_no: int) -> Optional[TimeLogEntry]:
    """
    Parse an 'arrived' time log entry.

    Format: - arrived: HH:MM am/pm

    Args:
        line: Line of text to parse.
        filename: Source file name.
        line_no: Line number in source file.

    Returns:
        TimeLogEntry if successfully parsed, None otherwise.
    """
    # Pattern: - arrived: optionally followed by time
    pattern = re.compile(r'^\s*-\s+arrived:\s*(.*?)$')
    match = pattern.match(line)

    if not match:
        return None

    time_str = match.group(1).strip()
    start_time = None

    if time_str:
        start_time = _parse_time(time_str)

    return TimeLogEntry(
        entry_type=EntryType.ARRIVED,
        text=line.rstrip(),
        filename=filename,
        line_no=line_no,
        start_time=start_time
    )


def _parse_activity_entry(line: str, filename: str, line_no: int) -> Optional[TimeLogEntry]:
    """
    Parse an activity time log entry.

    Format: - activity description (tags) HH:MM am/pm - HH:MM am/pm

    The tags in parentheses and times are optional.

    Args:
        line: Line of text to parse.
        filename: Source file name.
        line_no: Line number in source file.

    Returns:
        TimeLogEntry if successfully parsed, None otherwise.
    """
    # Pattern: - activity (optional tags) optional time range
    # Example: - email review (#admin, #communication) 8:15 am - 8:45 am
    pattern = re.compile(
        r'^\s*-\s+(.+?)'  # Activity description (non-greedy)
        r'(?:\s+(\d{1,2}:\d{2}\s*(?:am|pm)))?'  # Optional start time
        r'(?:\s*-\s*(\d{1,2}:\d{2}\s*(?:am|pm)))?'  # Optional end time
        r'\s*$',
        re.IGNORECASE
    )
    match = pattern.match(line)

    if not match:
        return None

    activity_text = match.group(1).strip()
    start_time_str = match.group(2)
    end_time_str = match.group(3)

    # Extract tags from activity text
    tags = _extract_tags(activity_text)

    # Remove tags from activity text to get clean activity description
    activity = re.sub(r'\s*\([^)]+\)\s*', ' ', activity_text).strip()

    # Parse times
    start_time = _parse_time(start_time_str) if start_time_str else None
    end_time = _parse_time(end_time_str) if end_time_str else None

    return TimeLogEntry(
        entry_type=EntryType.ACTIVITY,
        text=line.rstrip(),
        filename=filename,
        line_no=line_no,
        start_time=start_time,
        end_time=end_time,
        activity=activity,
        tags=tags
    )


def find_time_log_entries(filepath: str) -> list[TimeLogEntry]:
    """
    Find all time log entries in a markdown file.

    Looks for entries under a '### Log' section in the file.

    Args:
        filepath: Path to the markdown file to search.

    Returns:
        A list of TimeLogEntry objects found in the file.
    """
    entries: list[TimeLogEntry] = []
    in_log_section = False

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Check for log section header
                if line.strip() == '### Log':
                    in_log_section = True
                    continue

                # Check if we've left the log section (new section header)
                if in_log_section and line.startswith('#'):
                    in_log_section = False
                    continue

                # Skip if not in log section
                if not in_log_section:
                    continue

                # Try to parse as arrived entry first
                entry = _parse_arrived_entry(line, filepath, line_num)

                # If not an arrived entry, try as activity entry
                if entry is None and line.strip().startswith('-'):
                    entry = _parse_activity_entry(line, filepath, line_num)

                if entry is not None:
                    entries.append(entry)

    except (IOError, UnicodeDecodeError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    return entries


def filter_entries_by_type(entries: list[TimeLogEntry],
                           entry_types: list[EntryType]) -> list[TimeLogEntry]:
    """
    Filter time log entries by type.

    Args:
        entries: List of TimeLogEntry objects to filter.
        entry_types: List of EntryType values to include.

    Returns:
        Filtered list of TimeLogEntry objects.
    """
    return [entry for entry in entries if entry.entry_type in entry_types]
