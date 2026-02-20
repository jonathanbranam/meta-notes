"""
Time tracking module for markdown files.

Handles time log parsing, time block parsing, and time calculations.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Optional
from collections import defaultdict
import re
import sys


class EntryType(Enum):
    """Enum representing the type of time log entry."""
    ARRIVED = "arrived"
    ACTIVITY = "activity"


# Tag groups: tags that share meaning and should be reported together.
TAG_GROUPS: dict[str, set[str]] = {
    'Meeting': {'#mtg', '#meeting'},
    'Personal': {'#per', '#personal', '#off-task'},
    'Break': {'#break'},
}

# Reverse lookup: normalized tag text → group name
TAG_TO_GROUP: dict[str, str] = {
    tag: group
    for group, tags in TAG_GROUPS.items()
    for tag in tags
}


@dataclass
class Tag:
    """Represents a tag extracted from text.

    Examples:
        Tag('#mtg')
        Tag('#project-alpha')
    """
    text: str

    def __post_init__(self):
        """Ensure tag text starts with #."""
        if not self.text.startswith('#'):
            self.text = '#' + self.text


@dataclass
class TimeLogEntry:
    """Represents a time log entry found in a markdown file.

    Time log entries use multi-line format:
    - activity name #tag-1 #tag-2
      * start: 2026-02-14 Sat 08:00
      * end:   2026-02-14 Sat 09:00
      * optional notes #additional-tag

    Examples:
        - email review #admin #communication
          * start: 2026-02-14 Sat 08:00
          * end:   2026-02-14 Sat 08:30
        - #mtg with #sapna about #ai-dev
          * start: 2026-02-14 Sat 09:00
          * end:   2026-02-14 Sat 09:16
    """
    entry_type: EntryType
    text: str
    filename: str
    line_no: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    activity: Optional[str] = None
    tags: list[Tag] = field(default_factory=list)
    notes: Optional[str] = None


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


def _parse_datetime(datetime_str: str) -> Optional[datetime]:
    """
    Parse a datetime string in format: YYYY-MM-DD DDD HH:MM

    Args:
        datetime_str: Datetime string to parse (e.g., '2026-02-14 Sat 08:00').

    Returns:
        A datetime object if successfully parsed, None otherwise.
    """
    datetime_str = datetime_str.strip()

    # Pattern: YYYY-MM-DD DDD HH:MM (DDD is day abbreviation like Mon, Tue, etc.)
    pattern = re.compile(r'^(\d{4})-(\d{2})-(\d{2})\s+\w{3}\s+(\d{2}):(\d{2})$')
    match = pattern.match(datetime_str)

    if not match:
        return None

    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))
    hour = int(match.group(4))
    minute = int(match.group(5))

    try:
        return datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    except ValueError:
        return None


def get_tag_group(tag_text: str) -> Optional[str]:
    """
    Return the group name for a tag, or None if not in any group.

    Args:
        tag_text: Tag text (with or without # prefix).

    Returns:
        Group name string, or None.
    """
    normalized = tag_text.lower()
    if not normalized.startswith('#'):
        normalized = '#' + normalized
    return TAG_TO_GROUP.get(normalized)


def parse_tags_from_text(text: str) -> list[Tag]:
    """
    Extract all tags from text.

    Tags start with # followed by word characters (letters, numbers, hyphens).

    Args:
        text: Text to search for tags.

    Returns:
        List of Tag objects found.
    """
    pattern = re.compile(r'#[\w-]+')
    return [Tag(match) for match in pattern.findall(text)]


def calculate_time_by_group(entries: list[TimeLogEntry]) -> dict[str, timedelta]:
    """
    Calculate total time spent per tag group.

    For each entry, all tags are checked for group membership. If an entry
    has multiple tags belonging to the same group, that group is only counted
    once for that entry.

    Args:
        entries: List of TimeLogEntry objects with start and end times.

    Returns:
        Dictionary mapping group name to total duration.
    """
    group_durations: dict[str, timedelta] = defaultdict(timedelta)

    for entry in entries:
        if entry.start_time is None or entry.end_time is None:
            continue

        duration = calculate_duration(entry.start_time, entry.end_time)

        seen_groups: set[str] = set()
        for tag in entry.tags:
            group = get_tag_group(tag.text)
            if group and group not in seen_groups:
                group_durations[group] += duration
                seen_groups.add(group)

    return dict(group_durations)


def _parse_time_log_lines(lines: list[str], filepath: str) -> list[TimeLogEntry]:
    """
    Parse time log entries from a list of lines.

    Looks for entries under a '### Log' section.
    New format uses multi-line entries:
    - activity name #tag-1 #tag-2
      * start: 2026-02-14 Sat 08:00
      * end:   2026-02-14 Sat 09:00
      * optional notes

    Args:
        lines: Lines of text to parse.
        filepath: Source file path (used for TimeLogEntry metadata).

    Returns:
        A list of TimeLogEntry objects found in the lines.
    """
    entries: list[TimeLogEntry] = []
    in_log_section = False
    current_entry_data: Optional[dict] = None

    for line_num, line in enumerate(lines, 1):
        # Check for log section header
        if line.strip() == '### Log':
            in_log_section = True
            continue

        # Check if we've left the log section (new section header)
        if in_log_section and line.startswith('#'):
            in_log_section = False
            # Save any pending entry
            if current_entry_data:
                entry = _create_time_log_entry(current_entry_data, filepath)
                if entry:
                    entries.append(entry)
                current_entry_data = None
            continue

        # Skip if not in log section
        if not in_log_section:
            continue

        # Check for activity line (starts with -)
        if line.strip().startswith('-') and not line.strip().startswith('  '):
            # Save previous entry if exists
            if current_entry_data:
                entry = _create_time_log_entry(current_entry_data, filepath)
                if entry:
                    entries.append(entry)

            # Start new entry
            activity_line = line.strip()[1:].strip()  # Remove leading '-'
            tags = parse_tags_from_text(activity_line)

            # Remove tags from activity text
            activity = re.sub(r'#[\w-]+', '', activity_line).strip()

            current_entry_data = {
                'activity': activity,
                'tags': tags,
                'start_time': None,
                'end_time': None,
                'notes': None,
                'line_no': line_num,
                'text': line.rstrip()
            }

        # Check for start/end/notes lines (indented with *)
        elif current_entry_data and line.strip().startswith('*'):
            detail_line = line.strip()[1:].strip()  # Remove leading '*'

            # Parse start time
            if detail_line.startswith('start:'):
                time_str = detail_line[6:].strip()
                current_entry_data['start_time'] = _parse_datetime(time_str)

            # Parse end time
            elif detail_line.startswith('end:'):
                time_str = detail_line[4:].strip()
                current_entry_data['end_time'] = _parse_datetime(time_str)

            # Everything else is notes
            else:
                if current_entry_data['notes'] is None:
                    current_entry_data['notes'] = detail_line
                else:
                    current_entry_data['notes'] += ' ' + detail_line

    # Save final entry if exists
    if current_entry_data:
        entry = _create_time_log_entry(current_entry_data, filepath)
        if entry:
            entries.append(entry)

    return entries


def find_time_log_entries(filepath: str) -> list[TimeLogEntry]:
    """
    Find all time log entries in a markdown file.

    Args:
        filepath: Path to the markdown file to search.

    Returns:
        A list of TimeLogEntry objects found in the file.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return _parse_time_log_lines(lines, filepath)
    except (IOError, UnicodeDecodeError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
        return []


def _create_time_log_entry(entry_data: dict, filepath: str) -> Optional[TimeLogEntry]:
    """
    Create a TimeLogEntry from parsed entry data.

    Args:
        entry_data: Dictionary with parsed entry data.
        filepath: Source file path.

    Returns:
        TimeLogEntry if data is valid, None otherwise.
    """
    if not entry_data.get('activity'):
        return None

    # Extract additional tags from notes if present
    tags = entry_data.get('tags', [])
    if entry_data.get('notes'):
        notes_tags = parse_tags_from_text(entry_data['notes'])
        tags.extend(notes_tags)

    return TimeLogEntry(
        entry_type=EntryType.ACTIVITY,
        text=entry_data.get('text', ''),
        filename=filepath,
        line_no=entry_data.get('line_no', 0),
        start_time=entry_data.get('start_time'),
        end_time=entry_data.get('end_time'),
        activity=entry_data.get('activity'),
        tags=tags,
        notes=entry_data.get('notes')
    )


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
        |  8:30am | ~off-plan~          |                     |
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


def calculate_duration(start: datetime | time, end: datetime | time) -> timedelta:
    """
    Calculate duration between two times or datetimes.

    For time objects: Assumes times are on the same day. If end < start, assumes end is next day.
    For datetime objects: Direct subtraction.

    Args:
        start: Start time or datetime.
        end: End time or datetime.

    Returns:
        Duration as timedelta.
    """
    # If already datetime objects, just subtract
    if isinstance(start, datetime) and isinstance(end, datetime):
        return end - start

    # Convert time objects to datetime objects on the same day
    if isinstance(start, time) and isinstance(end, time):
        today = datetime.today().date()
        start_dt = datetime.combine(today, start)
        end_dt = datetime.combine(today, end)

        # If end is before start, assume it's the next day
        if end_dt < start_dt:
            end_dt = datetime.combine(today + timedelta(days=1), end)

        return end_dt - start_dt

    # Mixed types - convert to datetime
    today = datetime.today().date()
    if isinstance(start, time):
        start = datetime.combine(today, start)
    if isinstance(end, time):
        end = datetime.combine(today, end)

    return end - start


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


# Tags that mark the start/end boundary of the personal/work transition.
# Entries tagged with these are stripped from the beginning and end of the day.
PERSONAL_BOUNDARY_TAGS: frozenset[str] = frozenset({'#per', '#personal'})

# Tags whose time does not count toward "hours worked".
NON_WORK_TAGS: frozenset[str] = frozenset({'#per', '#personal', '#off-task', '#break'})

_DAY_ABBREVS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def _has_any_tag(entry: TimeLogEntry, tag_set: frozenset) -> bool:
    """Return True if the entry has any tag from the given set."""
    return any(tag.text.lower() in tag_set for tag in entry.tags)


def format_duration_long(duration: timedelta) -> str:
    """
    Format a duration in long form: "7 hr 46 min" or "30 min".

    Args:
        duration: Duration to format.

    Returns:
        String like "7 hr 46 min" or "30 min".
    """
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if hours > 0:
        return f"{hours} hr {minutes} min"
    return f"{minutes} min"


def analyze_work_day(entries: list[TimeLogEntry]) -> Optional[dict]:
    """
    Compute work day statistics from a day's time log entries.

    The work window starts at the first entry not tagged with a personal
    boundary tag (#per, #personal) and ends at the last such entry.
    Entries tagged #off-task or #break are included in the window but
    do not count toward hours worked.

    Args:
        entries: Time log entries for a single day.

    Returns:
        Dict with keys 'start', 'end', 'total_time', 'hours_worked',
        or None if there are no timed entries outside personal time.
    """
    timed = [e for e in entries if e.start_time is not None and e.end_time is not None]
    if not timed:
        return None

    timed.sort(key=lambda e: e.start_time)

    # Strip personal entries from the beginning
    start_idx = 0
    while start_idx < len(timed) and _has_any_tag(timed[start_idx], PERSONAL_BOUNDARY_TAGS):
        start_idx += 1

    # Strip personal entries from the end
    end_idx = len(timed) - 1
    while end_idx >= start_idx and _has_any_tag(timed[end_idx], PERSONAL_BOUNDARY_TAGS):
        end_idx -= 1

    if start_idx > end_idx:
        return None

    work_window = timed[start_idx:end_idx + 1]
    work_start = work_window[0].start_time
    work_end = work_window[-1].end_time
    total_time = calculate_duration(work_start, work_end)

    hours_worked = timedelta()
    for entry in work_window:
        if not _has_any_tag(entry, NON_WORK_TAGS):
            hours_worked += calculate_duration(entry.start_time, entry.end_time)

    return {
        'start': work_start,
        'end': work_end,
        'total_time': total_time,
        'hours_worked': hours_worked,
    }


def format_week_summary(days: list[tuple[date, Optional[dict]]]) -> str:
    """
    Format a Mon-Fri week summary as a markdown indented list.

    Args:
        days: List of (date, analysis_or_None) for each day of the week.

    Returns:
        Formatted markdown string.
    """
    lines = []
    total_worked = timedelta()

    for d, analysis in days:
        day_abbrev = _DAY_ABBREVS[d.weekday()]
        lines.append(f"- {d.strftime('%Y-%m-%d')} {day_abbrev}")

        if analysis is None:
            lines.append("  * (no data)")
        else:
            start_str = analysis['start'].strftime('%H:%M')
            end_str = analysis['end'].strftime('%H:%M')
            lines.append(f"  * time tracked:   {start_str} - {end_str}")
            lines.append(f"  * hours worked:   {format_duration_long(analysis['hours_worked'])}")
            lines.append(f"  * total time:     {format_duration_long(analysis['total_time'])}")
            total_worked += analysis['hours_worked']

    lines.append("")
    lines.append(f"Weekly total worked: {format_duration_long(total_worked)}")

    return "\n".join(lines)


def is_off_plan(block: 'TimeBlockEntry') -> bool:
    """
    Check if a time block entry is off-plan.

    A block is off-plan if:
    - The plan text is wrapped in single tildes: ~plan text~
    - The actual text contains the #off-plan tag

    Args:
        block: The TimeBlockEntry to check.

    Returns:
        True if the block is off-plan, False otherwise.
    """
    if block is None:
        return False

    plan = block.plan or ""
    plan_stripped = plan.strip()
    if plan_stripped.startswith('~') and plan_stripped.endswith('~') and len(plan_stripped) > 1:
        return True

    actual = block.actual or ""
    if '#off-plan' in actual:
        return True

    return False


def compare_plan_vs_actual(time_blocks: list[TimeBlockEntry]) -> tuple[int, int, int]:
    """
    Compare plan vs actual in time blocks.

    Categorizes time blocks as:
    - On-plan: has a plan not marked off-plan, and actual does not contain #off-plan
    - Off-plan: plan is wrapped in ~tildes~, or actual contains #off-plan
    - Unplanned: no plan entry

    Args:
        time_blocks: List of TimeBlockEntry objects.

    Returns:
        Tuple of (on_plan_count, off_plan_count, unplanned_count).
    """
    on_plan = 0
    off_plan = 0
    unplanned = 0

    for block in time_blocks:
        if not block.plan or not block.plan.strip():
            unplanned += 1
        elif is_off_plan(block):
            off_plan += 1
        else:
            on_plan += 1

    return on_plan, off_plan, unplanned


def calculate_plan_adherence(time_blocks: list[TimeBlockEntry]) -> dict[str, float]:
    """
    Calculate plan adherence statistics.

    Args:
        time_blocks: List of TimeBlockEntry objects.

    Returns:
        Dictionary with keys:
        - 'on_plan_percent': Percentage of time spent on-plan
        - 'off_plan_percent': Percentage of time spent off-plan
        - 'unplanned_percent': Percentage of time unplanned (no plan entry)
        - 'on_plan_count': Number of on-plan blocks
        - 'off_plan_count': Number of off-plan blocks
        - 'unplanned_count': Number of unplanned blocks
        - 'total_blocks': Total number of blocks
    """
    on_plan, off_plan, unplanned = compare_plan_vs_actual(time_blocks)
    total = on_plan + off_plan + unplanned

    if total == 0:
        return {
            'on_plan_percent': 0.0,
            'off_plan_percent': 0.0,
            'unplanned_percent': 0.0,
            'on_plan_count': 0,
            'off_plan_count': 0,
            'unplanned_count': 0,
            'total_blocks': 0,
        }

    return {
        'on_plan_percent': (on_plan / total) * 100,
        'off_plan_percent': (off_plan / total) * 100,
        'unplanned_percent': (unplanned / total) * 100,
        'on_plan_count': on_plan,
        'off_plan_count': off_plan,
        'unplanned_count': unplanned,
        'total_blocks': total,
    }
