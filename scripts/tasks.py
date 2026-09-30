"""
Task management module for markdown files.

Handles task parsing, status tracking, and date extraction from markdown tasks.
"""

from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum
from typing import Optional
import re
import sys

from recurrence import parse_rule
from tags import parse_tags
from time_tracking import _parse_bare_time_24h, _parse_time

# The time-of-day marker, written `⏰ HH:MM`
TIME_EMOJI = '⏰'

# Emojis that mark a due date. Used bare (no date after it), one marks an
# undated task.
DUE_EMOJIS = ('📅', '📆', '🗓')

# Status characters that task updates write, and their meanings. Any other
# character reads as incomplete (see char_to_status).
STATUS_CHARS = {
    ' ': 'open',
    'x': 'done',
    'X': 'done',
    '>': 'rescheduled (carried forward to another note)',
    '-': 'canceled',
    '.': 'partial (open)',
    'o': 'partial (open)',
    'O': 'partial (open)',
}

# A due emoji (optionally with an emoji variation selector), a date, and an
# optional 24-hour time after the date
_DUE_DATE_PATTERN = re.compile(
    '(?:' + '|'.join(DUE_EMOJIS) + r')\ufe0f?\s*(\d{4}-\d{2}-\d{2})'
    r'(?:[ \t]+(\d{1,2}:\d{2})(?![\d:]))?')

# ⏰ (optionally with an emoji variation selector) and what follows it: a
# time such as 15:00, 3:15pm, or 3:15 pm, or other text that isn't a time
_TIME_MARKER_PATTERN = re.compile(
    TIME_EMOJI + r'\ufe0f?[ \t]*(\d{1,2}:\d{2}(?:[ \t]*[AaPp][Mm])?|\S*)')

# 🔁 (optionally with an emoji variation selector) and the rule text after
# it, which runs to the next date or time marker, the first #tag, or the
# end of the line
_RECURRENCE_MARKER_PATTERN = re.compile(
    '🔁\\ufe0f?[ \\t]*(.*?)(?=[ \\t]+(?:📅|📆|🗓|🛫|✅|⏰|#)|[ \\t]*$)')

# A checkbox line: optional indentation, a bullet (-, *, +), whitespace, and
# a single status character in square brackets
CHECKBOX_PATTERN = re.compile(r'^\s*[-*+]\s+\[(.)\]')


class TaskStatus(Enum):
    """Enum representing the status of a task."""
    INCOMPLETE = "incomplete"
    COMPLETED = "completed"
    RESCHEDULED = "rescheduled"
    CANCELED = "canceled"


@dataclass
class Task:
    """Represents a task found in a markdown file.

    Dates can be specified in the task text using emojis:
    - 🛫 YYYY-MM-DD for start_date
    - 📅, 📆, or 🗓 YYYY-MM-DD for due_date
    - ✅ YYYY-MM-DD for completed_date

    The due time is the ⏰ time (24-hour like 15:00 or 12-hour like 3:15pm)
    or the time after the due date (📅 2026-10-01 15:00). When both are
    present, ⏰ wins. invalid_time is True when a ⏰ marker isn't a time.

    recurrence is the rule text after 🔁 as written (like "every 3 months"),
    and recurs_from_completion is True for a "when done" rule. A rule that
    isn't supported sets invalid_recurrence instead. A valid rule on a line
    with no due or start date (and not "when done") is not recurring.

    A due emoji with no valid date after it makes the task undated. Tags
    are the canonical names (without #) of every #tag on the line.
    """
    text: str
    status: TaskStatus
    filename: str
    line_no: int
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    undated: bool = False
    tags: list[str] = field(default_factory=list)
    due_time: Optional[time] = None
    invalid_time: bool = False
    recurrence: Optional[str] = None
    recurs_from_completion: bool = False
    invalid_recurrence: bool = False

    @property
    def effective_due(self) -> Optional[date]:
        """The ✅ date of a completed task that has one, otherwise the due date."""
        if self.status == TaskStatus.COMPLETED and self.completed_date:
            return self.completed_date
        return self.due_date


def _extract_date(text: str, emoji: str) -> Optional[date]:
    """
    Extract a date from task text following a specific emoji.

    Args:
        text: The task text to search.
        emoji: The emoji character indicating the date type.

    Returns:
        A date object if found, None otherwise.
    """
    # Pattern: emoji followed by optional whitespace and a date in YYYY-MM-DD format
    pattern = re.compile(rf'{re.escape(emoji)}\s*(\d{{4}}-\d{{2}}-\d{{2}})')
    match = pattern.search(text)
    if match:
        date_str = match.group(1)
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            # Invalid date format
            return None
    return None


def _parse_task_dates(text: str) -> tuple[Optional[date], Optional[date], Optional[date]]:
    """
    Parse all dates from task text.

    Args:
        text: The task text to parse.

    Returns:
        A tuple of (start_date, due_date, completed_date).
    """
    start_date = _extract_date(text, '🛫')
    due_date = None
    for match in _DUE_DATE_PATTERN.finditer(text):
        try:
            due_date = date.fromisoformat(match.group(1))
            break
        except ValueError:
            continue
    completed_date = _extract_date(text, '✅')
    return start_date, due_date, completed_date


def parse_time_marker(text: str) -> tuple[Optional[time], bool]:
    """
    Read the ⏰ time of task text.

    Args:
        text: The task text.

    Returns:
        A tuple of (the time, or None; True when a ⏰ marker is there but
        isn't a valid time). The first ⏰ is used.
    """
    match = _TIME_MARKER_PATTERN.search(text)
    if not match:
        return None, False
    value = match.group(1)
    parsed = _parse_bare_time_24h(value) or _parse_time(value)
    return parsed, parsed is None


def parse_due_time(text: str) -> tuple[Optional[time], bool]:
    """
    Read a task's time of day: ⏰ first, else the time after the due date.

    Returns:
        A tuple of (the time, or None; True when a ⏰ marker isn't a time).
    """
    marked, invalid = parse_time_marker(text)
    if marked is not None:
        return marked, False
    for match in _DUE_DATE_PATTERN.finditer(text):
        try:
            date.fromisoformat(match.group(1))
        except ValueError:
            continue
        if match.group(2):
            return _parse_bare_time_24h(match.group(2)), invalid
        break
    return None, invalid


def parse_recurrence(text: str, due_date: Optional[date],
                     start_date: Optional[date]) -> tuple[Optional[str], bool, bool]:
    """
    Read a task's 🔁 rule.

    Returns:
        A tuple of (the rule text as written, or None; True for a "when
        done" rule; True when a 🔁 marker is there but its rule isn't
        supported). The first 🔁 is used.
    """
    match = _RECURRENCE_MARKER_PATTERN.search(text)
    if not match:
        return None, False, False
    rule_text = match.group(1).strip()
    rule = parse_rule(rule_text)
    if rule is None:
        return None, False, True
    if not rule.when_done and due_date is None and start_date is None:
        return None, False, False
    return rule_text, rule.when_done, False


def task_warnings(task: Task) -> list[str]:
    """Warnings for a task's ⏰ time and 🔁 rule."""
    where = f"{task.filename}:{task.line_no}"
    warnings = []
    if task.invalid_time:
        warnings.append(f"{where}: ⏰ is not a time (use HH:MM)")
    elif task.due_time is not None and task.due_date is None:
        warnings.append(f"{where}: time without a due date is ignored")
    if task.invalid_recurrence:
        warnings.append(f"{where}: 🔁 is not a supported rule (like "
                        "'every 3 months' or 'every weekday')")
    return warnings


def _has_due_emoji(text: str) -> bool:
    """Whether text contains any due emoji, with or without a date."""
    return any(emoji in text for emoji in DUE_EMOJIS)


def is_task(text: str) -> bool:
    """
    Whether a checkbox line counts as a task.

    A checkbox line is a task only when it contains a due emoji (with or
    without a date) or a start date (🛫 YYYY-MM-DD). Other checkbox lines
    are checklist items.

    Args:
        text: The line's text.

    Returns:
        True if the line has a due emoji or a valid start date.
    """
    return _has_due_emoji(text) or _extract_date(text, '🛫') is not None


def char_to_status(status_char: str) -> TaskStatus:
    """
    Convert a status character to a TaskStatus enum.

    Args:
        status_char: Single character status indicator.

    Returns:
        Corresponding TaskStatus enum value.
    """
    status_upper = status_char.upper()
    if status_upper == 'X':
        return TaskStatus.COMPLETED
    elif status_char == '>':
        return TaskStatus.RESCHEDULED
    elif status_char == '-':
        return TaskStatus.CANCELED
    else:
        # Any other character (including space, ., o, O, /, etc.) is incomplete
        return TaskStatus.INCOMPLETE


def find_tasks_in_file(filepath: str) -> list[Task]:
    """
    Find all task lines in a markdown file.

    Checkbox lines that aren't tasks (see is_task) are skipped.

    Args:
        filepath: Path to the markdown file to search.

    Returns:
        A list of Task objects found in the file.
    """
    tasks: list[Task] = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                match = CHECKBOX_PATTERN.match(line)
                if not match:
                    continue
                text = line.rstrip()
                if not is_task(text):
                    continue
                start_date, due_date, completed_date = _parse_task_dates(text)
                has_due_emoji = _has_due_emoji(text)
                due_time, invalid_time = parse_due_time(text)
                recurrence, from_completion, invalid_rule = parse_recurrence(
                    text, due_date, start_date)
                tasks.append(Task(
                    text=text,
                    status=char_to_status(match.group(1)),
                    filename=filepath,
                    line_no=line_num,
                    start_date=start_date,
                    due_date=due_date,
                    completed_date=completed_date,
                    undated=has_due_emoji and due_date is None,
                    tags=parse_tags(text),
                    due_time=due_time,
                    invalid_time=invalid_time,
                    recurrence=recurrence,
                    recurs_from_completion=from_completion,
                    invalid_recurrence=invalid_rule,
                ))
    except (IOError, UnicodeDecodeError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    return tasks


def categorize_status(status: str) -> str:
    """
    Categorize task status for display.

    Args:
        status: Single character status indicator.

    Returns:
        String representation of the status category.
    """
    return char_to_status(status).value


def filter_tasks_by_status(tasks: list[Task], statuses: list[TaskStatus]) -> list[Task]:
    """
    Filter tasks to only include those with specified statuses.

    Args:
        tasks: List of Task objects to filter.
        statuses: List of TaskStatus values to include.

    Returns:
        List containing only tasks with status in the statuses list.
    """
    return [task for task in tasks if task.status in statuses]
