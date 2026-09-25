"""
Task query: the find_tasks.py report, plus structured results for --json.
"""

import os
from datetime import date

import find_tasks
from tasks import Task

# Section order of the categorized report
CATEGORIES = ("past_or_current", "future", "no_date")


def task_to_dict(task: Task, root_dir: str, category: str | None = None) -> dict:
    """Convert a Task to a JSON-ready dict with a root-relative file path."""
    data = {
        "file": os.path.relpath(task.filename, root_dir),
        "line": task.line_no,
        "text": task.text,
        "status": task.status.value,
        "start": task.start_date.isoformat() if task.start_date else None,
        "due": task.due_date.isoformat() if task.due_date else None,
        "completed": task.completed_date.isoformat() if task.completed_date else None,
    }
    if category is not None:
        data["category"] = category
    return data


def run(root_dir: str, folder: str | None = None, due_on: str | None = None,
        due_by: str | None = None, due_between: list[str] | None = None,
        status: str = "incomplete", condensed: bool = False,
        today: date | None = None) -> tuple[list[str], list[dict]]:
    """
    Run a task query with find_tasks.py semantics.

    Args:
        root_dir: Notes root to search.
        folder, due_on, due_by, due_between, status: find_tasks.py filters,
            with dates as YYYY-MM-DD strings.
        condensed: Use the condensed text format.
        today: Reference date for the categorized report (default: today).

    Returns:
        Tuple of (text lines identical to find_tasks.py, task dicts in the
        same order).

    Raises:
        ValueError: If a date argument is invalid.
    """
    today = today or date.today()
    on, by, between = find_tasks.parse_date_filters(due_on, due_by, due_between)

    if find_tasks.is_filtered(folder, on, by, between, status):
        lines = find_tasks.generate_filtered_report(
            root_dir, folder, on, by, between, status, condensed)
        tasks = find_tasks.collect_filtered_tasks(
            root_dir, folder, on, by, between, status)
        by_file = find_tasks.group_tasks_by_file(tasks)
        results = [task_to_dict(t, root_dir)
                   for filepath in sorted(by_file)
                   for t in by_file[filepath]]
        return lines, results

    lines = find_tasks.generate_report(root_dir, today, condensed)
    categorized = find_tasks.collect_categorized_tasks(root_dir, today)
    results = [task_to_dict(t, root_dir, category)
               for category in CATEGORIES
               for _filepath, file_tasks in categorized[category]
               for t in file_tasks]
    return lines, results
