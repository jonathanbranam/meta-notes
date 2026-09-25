"""
Task query: the find_tasks.py report, plus structured results for --json.
"""

import os
from datetime import date

import find_tasks
from tasks import Task


def task_to_dict(task: Task, root_dir: str, section: str) -> dict:
    """Convert a Task to a JSON-ready dict with a root-relative file path."""
    return {
        "file": os.path.relpath(task.filename, root_dir),
        "line": task.line_no,
        "text": task.text,
        "status": task.status.value,
        "start": task.start_date.isoformat() if task.start_date else None,
        "due": task.due_date.isoformat() if task.due_date else None,
        "completed": task.completed_date.isoformat() if task.completed_date else None,
        "tags": task.tags,
        "section": section,
    }


def run(root_dir: str, period: str | None = None, modes: list[str] | None = None,
        later: bool = False, tags: list[str] | None = None,
        group_by: str | None = None, folder: str | None = None,
        status: str = "incomplete", condensed: bool = False,
        today: date | None = None) -> tuple[list[str], list[dict]]:
    """
    Run a task query with find_tasks.py semantics.

    Args:
        root_dir: Notes root to search.
        period, modes, later, tags, group_by, folder, status: find_tasks.py
            options (see find_tasks.run_query).
        condensed: Use the condensed text format.
        today: Reference date for the default period (default: today).

    Returns:
        Tuple of (text lines identical to find_tasks.py, task dicts in
        report order, each task once).

    Raises:
        ValueError: If period is invalid.
    """
    lines, selected = find_tasks.run_query(root_dir, period, modes, later, tags,
                                           group_by, folder, status, condensed, today)
    return lines, [task_to_dict(task, root_dir, section) for section, task in selected]
