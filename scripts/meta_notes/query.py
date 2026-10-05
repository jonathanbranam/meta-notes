"""
Task query: the find_tasks.py report, plus structured results for --json.
"""

import os
from datetime import date, timedelta

import find_tasks
from notes import find_all_markdown_files
from period import agenda_horizon, parse_period
from tasks import Node, Task, task_warnings


def node_ref(node: Node, rel: str) -> dict:
    """A checkbox line as a JSON-ready reference: file, line, text, status."""
    return {"file": rel, "line": node.line_no, "text": node.text,
            "status": node.status.value}


def task_to_dict(task: Task, root_dir: str, section: str) -> dict:
    """Convert a Task to a JSON-ready dict with a root-relative file path."""
    rel = os.path.relpath(task.filename, root_dir)
    return {
        "file": rel,
        "line": task.line_no,
        "text": task.text,
        "status": task.status.value,
        "start": task.start_date.isoformat() if task.start_date else None,
        "due": task.due_date.isoformat() if task.due_date else None,
        "time": task.due_time.strftime("%H:%M") if task.due_time else None,
        "recurrence": task.recurrence,
        "recurs_from_completion": task.recurs_from_completion,
        "completed": task.completed_date.isoformat() if task.completed_date else None,
        "tags": task.tags,
        "section": section,
        "notes": list(task.notes),
        "parent": node_ref(task.parent, rel) if task.parent else None,
        "subtasks": [node_ref(child, rel) for child in task.subtasks],
    }


def run(root_dir: str, period: str | None = None, modes: list[str] | None = None,
        later: bool = False, tags: list[str] | None = None,
        group_by: str | None = None, folder: str | None = None,
        status: str = "incomplete", condensed: bool = False,
        today: date | None = None,
        at: str | None = None) -> tuple[list[str], list[dict], list[str]]:
    """
    Run a task query with find_tasks.py semantics.

    Args:
        root_dir: Notes root to search.
        period, modes, later, tags, group_by, folder, status: find_tasks.py
            options (see find_tasks.run_query).
        condensed: Use the condensed text format.
        today: Reference date for the default period (default: today).
        at: --at value, 'now' or HH:MM, for a single day in period.

    Returns:
        Tuple of (text lines identical to find_tasks.py, task dicts in
        report order with each task once, warnings about the selected
        tasks' times).

    Raises:
        ValueError: If period or at is invalid.
    """
    lines, selected = find_tasks.run_query(root_dir, period, modes, later, tags,
                                           group_by, folder, status, condensed, today, at)
    warnings = [w for _, task in selected for w in task_warnings(task)]
    return (lines, [task_to_dict(task, root_dir, section) for section, task in selected],
            warnings)


def agenda(root_dir: str, through: str | None = None, undated: bool = False,
           later: bool = False, tags: list[str] | None = None,
           folder: str | None = None, status: str = "incomplete",
           condensed: bool = False, today: date | None = None
           ) -> tuple[list[str], list[dict], list[str]]:
    """
    The task picture for the coming days: Overdue, Today, one section per
    following day through the horizon, and optionally Undated.

    Args:
        through: Last day (any --date form; its end day), default
            period.agenda_horizon.
        undated: Add an Undated section.
        later, tags, folder, status, condensed: as for run.
        today: Reference date (default: today).

    Returns:
        Tuple of (text lines, sections, warnings). Each section is
        {"section", "heading", "date", "tasks"}, in order, empty ones
        included; the text omits empty sections. A task is in one section,
        by due date. Started (🛫) tasks with no due date are under Today; a
        started task due after the horizon is left out.

    Raises:
        ValueError: If through is invalid or before today.
    """
    today = today or date.today()
    end = parse_period(through, today)[1] if through else agenda_horizon(today)
    if end < today:
        raise ValueError(f"--through {through} is before today")

    names = [("overdue", "Overdue", None), ("today", "Today", today)]
    day = today
    while day < end:
        day += timedelta(days=1)
        names.append((day.isoformat(), day.strftime("%Y-%m-%d %a"), day))
    if undated:
        names.append(("undated", "Undated", None))
    buckets: dict[str, list] = {name: [] for name, _, _ in names}

    files = find_all_markdown_files(root_dir)
    for task in find_tasks.collect_tasks(files, root_dir, folder, status, tags):
        if not later and find_tasks.is_later(task):
            continue
        due = task.effective_due
        if due is not None:
            if due > end:
                continue
            key = "overdue" if due < today else due.isoformat() if due > today else "today"
        elif task.start_date is not None:
            if task.start_date > today:
                continue
            key = "today"
        elif task.undated:
            key = "undated"
        else:
            continue
        if key in buckets:
            buckets[key].append(task)

    lines: list[str] = []
    sections: list[dict] = []
    warnings: list[str] = []
    for name, heading, when in names:
        tasks = sorted(buckets[name], key=lambda t: (t.filename, t.line_no))
        sections.append({"section": name, "heading": heading,
                         "date": when.isoformat() if when else None,
                         "tasks": [task_to_dict(t, root_dir, name) for t in tasks]})
        warnings.extend(w for t in tasks for w in task_warnings(t))
        if tasks:
            find_tasks._add_heading(lines, f"# {heading}")
            lines.extend(find_tasks.format_files(tasks, root_dir, condensed))
    total = sum(len(s["tasks"]) for s in sections)
    if not total:
        return ["No tasks found matching the criteria."], sections, warnings
    if not condensed:
        files_n = len({t["file"] for s in sections for t in s["tasks"]})
        lines.append("")
        lines.append(f"Summary: Found {total} {'task' if total == 1 else 'tasks'} "
                     f"in {files_n} {'file' if files_n == 1 else 'files'}")
    return lines, sections, warnings
