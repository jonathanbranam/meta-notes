"""
Time tracking module for markdown files.

Handles time log parsing, time block parsing, and time calculations.
"""

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum
from typing import Optional
from collections import defaultdict
import re
import sys


class EntryType(Enum):
    """Enum representing the type of time log entry."""
    ARRIVED = "arrived"
    ACTIVITY = "activity"


class TagType(Enum):
    """Enum representing the category of a tag."""
    SPECIAL = "special"  # Tags like #mtg, #dev, #pers, #admin
    ACTIVITY = "activity"  # User-defined activity tags


# Define special tag categories
SPECIAL_TAGS = {
    '#mtg',      # Meetings
    '#dev',      # Development work
    '#pers',     # Personal time
    '#admin',    # Administrative tasks
    '#break',    # Break time
}


@dataclass
class Tag:
    """Represents a tag with its type and text.

    Examples:
        Tag('#mtg', TagType.SPECIAL)
        Tag('#project-alpha', TagType.ACTIVITY)
    """
    text: str
    tag_type: TagType

    def __post_init__(self):
        """Ensure tag text starts with #."""
        if not self.text.startswith('#'):
            self.text = '#' + self.text


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
    tags: list[Tag] = field(default_factory=list)


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


def categorize_tag(tag_text: str) -> TagType:
    """
    Categorize a tag as special or activity.

    Args:
        tag_text: Tag text (with or without # prefix).

    Returns:
        TagType.SPECIAL if the tag is a known special tag, TagType.ACTIVITY otherwise.
    """
    # Normalize tag text to lowercase with # prefix
    normalized = tag_text.lower()
    if not normalized.startswith('#'):
        normalized = '#' + normalized

    return TagType.SPECIAL if normalized in SPECIAL_TAGS else TagType.ACTIVITY


def parse_tags_from_text(text: str) -> list[Tag]:
    """
    Extract all tags from text (both in parentheses and standalone).

    Tags start with # and can be:
    - In parentheses: (#admin, #communication)
    - Standalone: #project-alpha #urgent

    Args:
        text: Text to search for tags.

    Returns:
        List of Tag objects found.
    """
    tags = []

    # Pattern to match tags: # followed by word characters (letters, numbers, underscore, hyphen)
    pattern = re.compile(r'#[\w-]+')
    matches = pattern.findall(text)

    for match in matches:
        tag_type = categorize_tag(match)
        tags.append(Tag(match, tag_type))

    return tags


def _extract_tags_from_parentheses(text: str) -> list[Tag]:
    """
    Extract tags from text enclosed in parentheses.

    Tags are comma-separated and start with #.
    Example: "(#admin, #communication)" returns [Tag('#admin'), Tag('#communication')]

    Args:
        text: Text to search for tags.

    Returns:
        List of Tag objects found in parentheses.
    """
    # Pattern: parentheses containing comma-separated tags
    pattern = re.compile(r'\(([^)]+)\)')
    match = pattern.search(text)

    if not match:
        return []

    tags_str = match.group(1)
    # Split by comma and strip whitespace
    tag_texts = [tag.strip() for tag in tags_str.split(',')]

    # Create Tag objects
    tags = []
    for tag_text in tag_texts:
        if tag_text:  # Skip empty strings
            tag_type = categorize_tag(tag_text)
            tags.append(Tag(tag_text, tag_type))

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

    # Extract tags from activity text (use parentheses extraction for backward compatibility)
    tags = _extract_tags_from_parentheses(activity_text)

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


@dataclass
class TimeBlockEntry:
    """Represents a time block table entry found in a markdown file.

    Time blocks are markdown tables with Time, Plan, and Actual columns.

    Examples:
        | Time    | Plan                | Actual              |
        |  8:00am | email #admin        | meeting #mtg        |
        |  8:15am | [break]             | coding #dev         |
        |  8:30am | ~~off-plan~~        |                     |
    """
    time_slot: time
    plan: Optional[str] = None
    actual: Optional[str] = None
    plan_tags: list[Tag] = field(default_factory=list)
    actual_tags: list[Tag] = field(default_factory=list)
    filename: str = ""
    line_no: int = 0


def _parse_time_block_row(line: str, filename: str, line_no: int) -> Optional[TimeBlockEntry]:
    """
    Parse a time block table row.

    Format: | HH:MM am/pm | plan text | actual text |

    Args:
        line: Line of text to parse.
        filename: Source file name.
        line_no: Line number in source file.

    Returns:
        TimeBlockEntry if successfully parsed, None otherwise.
    """
    # Pattern: table row with time and two content columns
    # Example: |  8:00am | email #admin        | meeting #mtg        |
    pattern = re.compile(r'^\s*\|\s*(\d{1,2}:\d{2}\s*(?:am|pm))\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|', re.IGNORECASE)
    match = pattern.match(line)

    if not match:
        return None

    time_str = match.group(1).strip()
    plan_text = match.group(2).strip()
    actual_text = match.group(3).strip()

    # Parse time
    time_slot = _parse_time(time_str)
    if time_slot is None:
        return None

    # Extract tags from plan and actual columns
    plan_tags = parse_tags_from_text(plan_text) if plan_text else []
    actual_tags = parse_tags_from_text(actual_text) if actual_text else []

    return TimeBlockEntry(
        time_slot=time_slot,
        plan=plan_text if plan_text else None,
        actual=actual_text if actual_text else None,
        plan_tags=plan_tags,
        actual_tags=actual_tags,
        filename=filename,
        line_no=line_no
    )


def find_time_block_entries(filepath: str) -> list[TimeBlockEntry]:
    """
    Find all time block entries in a markdown file.

    Looks for entries under a '### Time Block' section in the file.

    Args:
        filepath: Path to the markdown file to search.

    Returns:
        A list of TimeBlockEntry objects found in the file.
    """
    entries: list[TimeBlockEntry] = []
    in_time_block_section = False
    in_table = False

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Check for time block section header
                if '### Time Block' in line:
                    in_time_block_section = True
                    continue

                # Check if we've left the time block section (new section header)
                if in_time_block_section and line.startswith('#'):
                    in_time_block_section = False
                    in_table = False
                    continue

                # Skip if not in time block section
                if not in_time_block_section:
                    continue

                # Check for table header or separator
                if '| Time' in line or '|---' in line or '| ---' in line:
                    in_table = True
                    continue

                # Skip if not in table yet
                if not in_table:
                    continue

                # Try to parse as time block row
                entry = _parse_time_block_row(line, filepath, line_num)
                if entry is not None:
                    entries.append(entry)

    except (IOError, UnicodeDecodeError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    return entries


def calculate_duration(start: time, end: time) -> timedelta:
    """
    Calculate duration between two times.

    Assumes times are on the same day. If end < start, assumes end is next day.

    Args:
        start: Start time.
        end: End time.

    Returns:
        Duration as timedelta.
    """
    # Convert times to datetime objects on the same day
    today = datetime.today().date()
    start_dt = datetime.combine(today, start)
    end_dt = datetime.combine(today, end)

    # If end is before start, assume it's the next day
    if end_dt < start_dt:
        end_dt = datetime.combine(today + timedelta(days=1), end)

    return end_dt - start_dt


def calculate_total_time_by_tag(entries: list[TimeLogEntry]) -> dict[str, timedelta]:
    """
    Calculate total time spent on each tag.

    Args:
        entries: List of TimeLogEntry objects with start and end times.

    Returns:
        Dictionary mapping tag text to total duration.
    """
    tag_durations: dict[str, timedelta] = defaultdict(timedelta)

    for entry in entries:
        # Skip entries without both start and end times
        if entry.start_time is None or entry.end_time is None:
            continue

        duration = calculate_duration(entry.start_time, entry.end_time)

        # Add duration to each tag in the entry
        for tag in entry.tags:
            tag_durations[tag.text] += duration

    return dict(tag_durations)


def calculate_work_vs_nonwork(entries: list[TimeLogEntry]) -> tuple[timedelta, timedelta]:
    """
    Calculate total work time vs non-work time.

    Work time includes: #mtg, #dev, #admin
    Non-work time includes: #pers, #break

    Args:
        entries: List of TimeLogEntry objects with start and end times.

    Returns:
        Tuple of (work_time, nonwork_time).
    """
    work_time = timedelta()
    nonwork_time = timedelta()

    # Define work tags and non-work tags
    work_tags = {'#mtg', '#dev', '#admin', '#meeting', '#code', '#coding', '#administrative'}
    nonwork_tags = {'#pers', '#break', '#personal'}

    for entry in entries:
        # Skip entries without both start and end times
        if entry.start_time is None or entry.end_time is None:
            continue

        duration = calculate_duration(entry.start_time, entry.end_time)

        # Categorize based on tags
        has_work_tag = any(tag.text.lower() in work_tags for tag in entry.tags)
        has_nonwork_tag = any(tag.text.lower() in nonwork_tags for tag in entry.tags)

        if has_work_tag:
            work_time += duration
        elif has_nonwork_tag:
            nonwork_time += duration
        # If no categorizing tags, don't count it

    return work_time, nonwork_time


def format_duration(duration: timedelta) -> str:
    """
    Format a duration as a human-readable string.

    Args:
        duration: Duration to format.

    Returns:
        String like "2h 30m" or "45m".
    """
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def is_off_plan(actual_text: Optional[str]) -> bool:
    """
    Check if an actual entry is marked as off-plan.

    Off-plan entries are marked with strikethrough: ~~text~~

    Args:
        actual_text: The actual column text.

    Returns:
        True if marked as off-plan, False otherwise.
    """
    if actual_text is None:
        return False

    # Check for strikethrough pattern: ~~text~~
    return '~~' in actual_text


def compare_plan_vs_actual(time_blocks: list[TimeBlockEntry]) -> tuple[int, int, int]:
    """
    Compare plan vs actual in time blocks.

    Categorizes time blocks as:
    - On-plan: actual matches plan (non-empty actual with same content)
    - Off-plan: actual is marked with ~~strikethrough~~ or differs from plan
    - Untracked: no actual entry

    Args:
        time_blocks: List of TimeBlockEntry objects.

    Returns:
        Tuple of (on_plan_count, off_plan_count, untracked_count).
    """
    on_plan = 0
    off_plan = 0
    untracked = 0

    for block in time_blocks:
        # Skip blocks with no plan
        if block.plan is None or not block.plan.strip():
            continue

        # No actual entry means untracked
        if block.actual is None or not block.actual.strip():
            untracked += 1
            continue

        # Check if marked as off-plan
        if is_off_plan(block.actual):
            off_plan += 1
            continue

        # Compare plan vs actual (ignoring tags for comparison)
        plan_clean = block.plan.strip()
        actual_clean = block.actual.strip()

        # Remove tags from both for comparison
        import re
        plan_no_tags = re.sub(r'#[\w-]+', '', plan_clean).strip()
        actual_no_tags = re.sub(r'#[\w-]+', '', actual_clean).strip()

        # If the main activity matches (ignoring case and extra whitespace), it's on-plan
        if plan_no_tags.lower() == actual_no_tags.lower():
            on_plan += 1
        else:
            off_plan += 1

    return on_plan, off_plan, untracked


def calculate_plan_adherence(time_blocks: list[TimeBlockEntry]) -> dict[str, float]:
    """
    Calculate plan adherence statistics.

    Args:
        time_blocks: List of TimeBlockEntry objects.

    Returns:
        Dictionary with keys:
        - 'on_plan_percent': Percentage of time spent on-plan
        - 'off_plan_percent': Percentage of time spent off-plan
        - 'untracked_percent': Percentage of time untracked
        - 'on_plan_count': Number of on-plan blocks
        - 'off_plan_count': Number of off-plan blocks
        - 'untracked_count': Number of untracked blocks
        - 'total_blocks': Total number of blocks with plans
    """
    on_plan, off_plan, untracked = compare_plan_vs_actual(time_blocks)
    total = on_plan + off_plan + untracked

    if total == 0:
        return {
            'on_plan_percent': 0.0,
            'off_plan_percent': 0.0,
            'untracked_percent': 0.0,
            'on_plan_count': 0,
            'off_plan_count': 0,
            'untracked_count': 0,
            'total_blocks': 0,
        }

    return {
        'on_plan_percent': (on_plan / total) * 100,
        'off_plan_percent': (off_plan / total) * 100,
        'untracked_percent': (untracked / total) * 100,
        'on_plan_count': on_plan,
        'off_plan_count': off_plan,
        'untracked_count': untracked,
        'total_blocks': total,
    }
