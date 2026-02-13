#!/usr/bin/env python3
"""
Find and list incomplete tasks from markdown files.

Searches recursively through all markdown files and outputs:
- File name as a wiki link
- All incomplete tasks defined within that file

Task format: bullet (-, *, +) followed by [status]
- [ ], [.], [o], [O], [/], or any other character = incomplete (reported)
- [x] or [X] = completed (not reported)
- [>] = rescheduled (not reported)
- [-] = canceled (not reported)
"""

import os
import sys
from datetime import date, timedelta

from tasks import Task, TaskStatus, find_tasks_in_file, filter_tasks_by_status
from notes import get_wiki_link, find_all_markdown_files


def filter_incomplete_tasks(tasks: list[Task]) -> list[Task]:
    """
    Filter a list of tasks to only include incomplete tasks.

    Args:
        tasks: List of Task objects to filter.

    Returns:
        List containing only tasks with INCOMPLETE status.
    """
    return filter_tasks_by_status(tasks, [TaskStatus.INCOMPLETE])


def calculate_week_end(today: date) -> date:
    """
    Calculate the end of the current week (Sunday).

    Week runs Monday through Sunday. If today is Sunday, returns today.
    Otherwise, returns the date of the following Sunday.

    Args:
        today: The reference date.

    Returns:
        The date of the current or next Sunday.
    """
    # weekday() returns 0 for Monday, 6 for Sunday
    days_until_sunday = 6 - today.weekday()

    if days_until_sunday < 0:
        # This shouldn't happen since 6 - weekday() is always >= 0
        days_until_sunday = 0

    return today + timedelta(days=days_until_sunday)


def get_task_relevant_date(task: Task) -> date | None:
    """
    Get the most relevant date from a task (due_date takes precedence over start_date).

    Args:
        task: Task object to extract date from.

    Returns:
        The due_date if present, otherwise start_date, or None if neither exists.
    """
    return task.due_date or task.start_date


def categorize_task_by_date(task: Task, today: date, week_end: date) -> str:
    """
    Categorize a task based on its due/start date.

    Args:
        task: Task object to categorize.
        today: Today's date.
        week_end: Date representing the end of this week.

    Returns:
        'past_or_current' for tasks due in the past or this week,
        'future' for tasks due beyond this week,
        'no_date' for tasks without due or start dates.
    """
    relevant_date = get_task_relevant_date(task)

    if relevant_date is None:
        return 'no_date'
    elif relevant_date <= week_end:
        return 'past_or_current'
    else:
        return 'future'


def format_file_tasks(filepath: str, tasks: list[Task], root_dir: str) -> list[str]:
    """
    Format tasks from a single file as output lines.

    Args:
        filepath: Path to the file containing tasks.
        tasks: List of Task objects from the file.
        root_dir: Root directory for generating wiki links.

    Returns:
        List of formatted output lines (empty if no tasks).
    """
    if not tasks:
        return []

    lines: list[str] = []
    wiki_link = get_wiki_link(filepath, root_dir)
    lines.append(f"## {wiki_link}")
    lines.append("")

    for task in tasks:
        lines.append(task.text)

    return lines


def collect_categorized_tasks(root_dir: str, today: date) -> dict[str, list[tuple[str, list[Task]]]]:
    """
    Collect and categorize all incomplete tasks from markdown files.

    Args:
        root_dir: Directory to search for markdown files.
        today: Reference date to use for categorization.

    Returns:
        Dictionary with categories as keys ('past_or_current', 'future', 'no_date')
        and lists of (filepath, tasks) tuples as values.
    """
    # Calculate date boundaries (week ends on Sunday)
    week_end = calculate_week_end(today)

    # Find all markdown files
    markdown_files = find_all_markdown_files(root_dir)

    # Structure: {category: [(filepath, [tasks])]}
    categorized_files: dict[str, list[tuple[str, list[Task]]]] = {
        'past_or_current': [],
        'future': [],
        'no_date': []
    }

    for filepath in markdown_files:
        all_tasks = find_tasks_in_file(filepath)
        incomplete_tasks = filter_incomplete_tasks(all_tasks)

        if not incomplete_tasks:
            continue

        # Categorize tasks by date
        tasks_by_category: dict[str, list[Task]] = {
            'past_or_current': [],
            'future': [],
            'no_date': []
        }

        for task in incomplete_tasks:
            category = categorize_task_by_date(task, today, week_end)
            tasks_by_category[category].append(task)

        # Add to categorized files (only if tasks exist in that category)
        for category, tasks in tasks_by_category.items():
            if tasks:
                categorized_files[category].append((filepath, tasks))

    return categorized_files


def format_section(
    category: str,
    header: str,
    file_tasks: list[tuple[str, list[Task]]],
    root_dir: str
) -> list[str]:
    """
    Format a single section of the report.

    Args:
        category: Category name (for identification).
        header: Markdown header for the section.
        file_tasks: List of (filepath, tasks) tuples for this section.
        root_dir: Root directory for generating wiki links.

    Returns:
        List of formatted output lines for the section.
    """
    if not file_tasks:
        return []

    lines: list[str] = []

    # Add section header
    lines.append(header)
    lines.append("")

    # Format each file's tasks in this category
    for filepath, tasks in file_tasks:
        file_lines = format_file_tasks(filepath, tasks, root_dir)
        lines.extend(file_lines)
        lines.append("")  # Empty line between files

    return lines


def generate_report(root_dir: str, today: date) -> list[str]:
    """
    Generate a complete report of incomplete tasks in all markdown files.

    Tasks are organized into three sections:
    1. Past or current week (tasks due in past or within 7 days)
    2. Future tasks (tasks due more than 7 days out)
    3. Tasks without dates

    Args:
        root_dir: Directory to search for markdown files.
        today: Reference date to use for categorization.

    Returns:
        List of output lines for the complete report.
    """
    # Find all markdown files
    markdown_files = find_all_markdown_files(root_dir)

    if not markdown_files:
        return ["No markdown files found."]

    # Collect and categorize tasks
    categorized_files = collect_categorized_tasks(root_dir, today)

    # Check if we have any tasks at all
    total_tasks = sum(
        sum(len(tasks) for _, tasks in file_tasks)
        for file_tasks in categorized_files.values()
    )

    if total_tasks == 0:
        return ["No incomplete tasks found in any markdown files."]

    # Generate output for each section
    lines: list[str] = []

    sections = [
        ('past_or_current', '# Past & Current Week'),
        ('future', '# Future (>1 Week)'),
        ('no_date', '# No Date')
    ]

    for category, header in sections:
        section_lines = format_section(
            category,
            header,
            categorized_files[category],
            root_dir
        )
        lines.extend(section_lines)

    # Add summary
    total_files = sum(len(file_tasks) for file_tasks in categorized_files.values())
    task_word = "task" if total_tasks == 1 else "tasks"
    section_word = "file section" if total_files == 1 else "file sections"
    lines.append("")
    lines.append(f"Summary: Found {total_tasks} incomplete {task_word} in {total_files} {section_word}")

    return lines


def main() -> None:
    """
    Main entry point for the script.
    """
    # Get the root directory from command line or use current directory
    root_dir: str = sys.argv[1] if len(sys.argv) > 1 else '.'

    if not os.path.isdir(root_dir):
        print(f"Error: {root_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Get current date
    today = date.today()

    # Generate and print report
    report_lines = generate_report(root_dir, today)
    output = "\n".join(report_lines)
    print(output)


if __name__ == '__main__':
    main()
