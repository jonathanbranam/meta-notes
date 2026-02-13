"""
Task management module for markdown files.

Handles task parsing, status tracking, and date extraction from markdown tasks.
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional
import re
import sys


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
    - 🗓 or 📆 YYYY-MM-DD for due_date
    - ✅ YYYY-MM-DD for completed_date
    """
    text: str
    status: TaskStatus
    filename: str
    line_no: int
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    completed_date: Optional[date] = None


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
    # Try both calendar emojis for due_date
    due_date = _extract_date(text, '🗓') or _extract_date(text, '📆')
    completed_date = _extract_date(text, '✅')
    return start_date, due_date, completed_date


def _char_to_status(status_char: str) -> TaskStatus:
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

    Args:
        filepath: Path to the markdown file to search.

    Returns:
        A list of Task objects found in the file.
    """
    tasks: list[Task] = []
    # Pattern: line starts with optional whitespace, bullet (-, *, +),
    # then space(s), then square brackets with a single character
    task_pattern = re.compile(r'^\s*[-*+]\s+\[(.)\]')

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                match = task_pattern.match(line)
                if match:
                    status_char = match.group(1)
                    status = _char_to_status(status_char)
                    text = line.rstrip()
                    start_date, due_date, completed_date = _parse_task_dates(text)
                    task = Task(
                        text=text,
                        status=status,
                        filename=filepath,
                        line_no=line_num,
                        start_date=start_date,
                        due_date=due_date,
                        completed_date=completed_date
                    )
                    tasks.append(task)
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
    return _char_to_status(status).value
