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

import argparse
import os
import sys
from datetime import date, timedelta

from tasks import Task, TaskStatus, find_tasks_in_file, filter_tasks_by_status
from notes import get_wiki_link, find_all_markdown_files, calculate_week_end


def filter_incomplete_tasks(tasks: list[Task]) -> list[Task]:
    """
    Filter a list of tasks to only include incomplete tasks.

    Args:
        tasks: List of Task objects to filter.

    Returns:
        List containing only tasks with INCOMPLETE status.
    """
    return filter_tasks_by_status(tasks, [TaskStatus.INCOMPLETE])


def filter_tasks_by_folder(tasks: list[Task], folder: str, root_dir: str) -> list[Task]:
    """
    Filter tasks to only include those from files in a specific folder.

    Args:
        tasks: List of Task objects to filter.
        folder: Folder path (includes subfolders by default).
        root_dir: Root directory being searched.

    Returns:
        List containing only tasks from files in the specified folder.
    """
    # Normalize folder path (remove trailing slash)
    folder_normalized = folder.rstrip('/')

    # Convert to absolute path for comparison
    if not os.path.isabs(folder_normalized):
        folder_abs = os.path.abspath(os.path.join(root_dir, folder_normalized))
    else:
        folder_abs = os.path.abspath(folder_normalized)

    filtered_tasks = []
    for task in tasks:
        # Get absolute path of task filename
        task_abs = os.path.abspath(task.filename)

        # Check if task file is in the specified folder (or subfolder)
        if task_abs.startswith(folder_abs + os.sep) or os.path.dirname(task_abs) == folder_abs:
            filtered_tasks.append(task)

    return filtered_tasks


def filter_tasks_by_due_date(tasks: list[Task], due_on: date | None = None,
                             due_by: date | None = None,
                             due_between: tuple[date, date] | None = None) -> list[Task]:
    """
    Filter tasks by due date criteria.

    Args:
        tasks: List of Task objects to filter.
        due_on: If provided, only include tasks due on this exact date.
        due_by: If provided, only include tasks due on or before this date.
        due_between: If provided, only include tasks due between these dates (inclusive).

    Returns:
        List containing only tasks matching the date criteria.
    """
    filtered_tasks = []

    for task in tasks:
        if task.due_date is None:
            continue

        if due_on is not None:
            if task.due_date == due_on:
                filtered_tasks.append(task)
        elif due_by is not None:
            if task.due_date <= due_by:
                filtered_tasks.append(task)
        elif due_between is not None:
            start_date, end_date = due_between
            if start_date <= task.due_date <= end_date:
                filtered_tasks.append(task)
        else:
            # No date filtering
            filtered_tasks.append(task)

    return filtered_tasks


def filter_tasks_by_status_arg(tasks: list[Task], status_arg: str) -> list[Task]:
    """
    Filter tasks by status argument.

    Args:
        tasks: List of Task objects to filter.
        status_arg: Status string ('incomplete', 'completed', 'all', etc.).

    Returns:
        List containing only tasks matching the status.
    """
    if status_arg == 'all':
        return tasks
    elif status_arg == 'incomplete':
        return filter_tasks_by_status(tasks, [TaskStatus.INCOMPLETE])
    elif status_arg == 'completed':
        return filter_tasks_by_status(tasks, [TaskStatus.COMPLETED])
    elif status_arg == 'rescheduled':
        return filter_tasks_by_status(tasks, [TaskStatus.RESCHEDULED])
    elif status_arg == 'canceled':
        return filter_tasks_by_status(tasks, [TaskStatus.CANCELED])
    else:
        return tasks


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
    Format tasks from a single file as output lines (standard format).

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


def format_file_tasks_condensed(filepath: str, tasks: list[Task], root_dir: str) -> list[str]:
    """
    Format tasks from a single file in condensed format.

    Condensed format shows the source note as a list item with tasks indented below:
    - [[path/to/note]]
      - [ ] task 1
      - [ ] task 2

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
    lines.append(f"- {wiki_link}")

    for task in tasks:
        # Add one level of indentation (2 spaces) to each task line
        indented_task = "  " + task.text
        lines.append(indented_task)

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
    root_dir: str,
    condensed: bool = False
) -> list[str]:
    """
    Format a single section of the report.

    Args:
        category: Category name (for identification).
        header: Markdown header for the section.
        file_tasks: List of (filepath, tasks) tuples for this section.
        root_dir: Root directory for generating wiki links.
        condensed: If True, use condensed format.

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
    formatter = format_file_tasks_condensed if condensed else format_file_tasks
    for filepath, tasks in file_tasks:
        file_lines = formatter(filepath, tasks, root_dir)
        lines.extend(file_lines)
        if not condensed:
            lines.append("")  # Empty line between files (standard format only)

    return lines


def generate_report(root_dir: str, today: date, condensed: bool = False) -> list[str]:
    """
    Generate a complete report of incomplete tasks in all markdown files.

    Tasks are organized into three sections:
    1. Past or current week (tasks due in past or within 7 days)
    2. Future tasks (tasks due more than 7 days out)
    3. Tasks without dates

    Args:
        root_dir: Directory to search for markdown files.
        today: Reference date to use for categorization.
        condensed: If True, use condensed format.

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
            root_dir,
            condensed
        )
        lines.extend(section_lines)

    # Add summary (not in condensed format)
    if not condensed:
        total_files = sum(len(file_tasks) for file_tasks in categorized_files.values())
        task_word = "task" if total_tasks == 1 else "tasks"
        section_word = "file section" if total_files == 1 else "file sections"
        lines.append("")
        lines.append(f"Summary: Found {total_tasks} incomplete {task_word} in {total_files} {section_word}")

    return lines


def parse_date_arg(date_str: str) -> date:
    """
    Parse a date string in YYYY-MM-DD format.

    Args:
        date_str: Date string to parse.

    Returns:
        Parsed date object.

    Raises:
        ValueError: If date string is invalid.
    """
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")


def parse_date_filters(due_on_arg: str | None, due_by_arg: str | None,
                       due_between_arg: list[str] | None
                       ) -> tuple[date | None, date | None, tuple[date, date] | None]:
    """
    Parse the date filter arguments.

    Args:
        due_on_arg: --due-on value, if given.
        due_by_arg: --due-by value, if given.
        due_between_arg: --due-between START END values, if given.

    Returns:
        Tuple of (due_on, due_by, due_between).

    Raises:
        ValueError: If a date is invalid or the range is reversed.
    """
    due_on = parse_date_arg(due_on_arg) if due_on_arg else None
    due_by = parse_date_arg(due_by_arg) if due_by_arg else None
    due_between = None
    if due_between_arg:
        start = parse_date_arg(due_between_arg[0])
        end = parse_date_arg(due_between_arg[1])
        if start > end:
            raise ValueError("Start date must be before or equal to end date")
        due_between = (start, end)
    return due_on, due_by, due_between


def is_filtered(folder: str | None, due_on: date | None, due_by: date | None,
                due_between: tuple[date, date] | None, status: str) -> bool:
    """Whether any filter is set (otherwise the categorized report is used)."""
    return bool(folder or due_on or due_by or due_between or status != 'incomplete')


def collect_filtered_tasks(root_dir: str, folder: str | None = None,
                           due_on: date | None = None, due_by: date | None = None,
                           due_between: tuple[date, date] | None = None,
                           status: str = 'incomplete') -> list[Task]:
    """
    Collect tasks from all markdown files matching the filters.

    Args:
        root_dir: Directory to search for markdown files.
        folder: Only include tasks from this folder (and subfolders).
        due_on: Only include tasks due on this date.
        due_by: Only include tasks due on or before this date.
        due_between: Only include tasks due in this inclusive range.
        status: Status argument ('incomplete', 'completed', 'all', ...).

    Returns:
        Matching tasks in file order.
    """
    all_tasks = []
    for filepath in find_all_markdown_files(root_dir):
        all_tasks.extend(find_tasks_in_file(filepath))

    filtered_tasks = filter_tasks_by_status_arg(all_tasks, status)

    if folder:
        filtered_tasks = filter_tasks_by_folder(filtered_tasks, folder, root_dir)

    if due_on or due_by or due_between:
        filtered_tasks = filter_tasks_by_due_date(filtered_tasks, due_on, due_by, due_between)

    return filtered_tasks


def group_tasks_by_file(tasks: list[Task]) -> dict[str, list[Task]]:
    """Group tasks by filename, preserving task order within each file."""
    tasks_by_file: dict[str, list[Task]] = {}
    for task in tasks:
        tasks_by_file.setdefault(task.filename, []).append(task)
    return tasks_by_file


def generate_filtered_report(root_dir: str, folder: str | None = None,
                             due_on: date | None = None, due_by: date | None = None,
                             due_between: tuple[date, date] | None = None,
                             status: str = 'incomplete',
                             condensed: bool = False) -> list[str]:
    """
    Generate the filtered report: matching tasks grouped by file.

    Args:
        root_dir: Directory to search for markdown files.
        folder, due_on, due_by, due_between, status: Filters, as for
            collect_filtered_tasks.
        condensed: If True, use condensed format.

    Returns:
        List of output lines.
    """
    if not find_all_markdown_files(root_dir):
        return ["No markdown files found."]

    filtered_tasks = collect_filtered_tasks(root_dir, folder, due_on, due_by,
                                            due_between, status)
    tasks_by_file = group_tasks_by_file(filtered_tasks)

    if not tasks_by_file:
        return ["No tasks found matching the criteria."]

    lines: list[str] = []
    formatter = format_file_tasks_condensed if condensed else format_file_tasks
    for filepath in sorted(tasks_by_file.keys()):
        lines.extend(formatter(filepath, tasks_by_file[filepath], root_dir))
        if not condensed:
            lines.append("")  # Empty line between files (standard format only)

    # Add summary (not in condensed format)
    if not condensed:
        total_tasks = len(filtered_tasks)
        total_files = len(tasks_by_file)
        task_word = "task" if total_tasks == 1 else "tasks"
        file_word = "file" if total_files == 1 else "files"
        lines.append("")
        lines.append(f"Summary: Found {total_tasks} {task_word} in {total_files} {file_word}")

    return lines


def main() -> None:
    """
    Main entry point for the script.
    """
    parser = argparse.ArgumentParser(
        description='Find and list tasks from markdown files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # All incomplete tasks in current directory
  %(prog)s --folder project          # Tasks from project/ folder
  %(prog)s --due-on 2026-02-14       # Tasks due on specific date
  %(prog)s --due-by 2026-02-20       # Tasks due by date
  %(prog)s --status all              # All tasks regardless of status
  %(prog)s --due-between 2026-02-01 2026-02-28  # Tasks due in date range
  %(prog)s --condensed               # Condensed format output
  %(prog)s --format=condensed        # Same as --condensed
        """
    )

    parser.add_argument(
        'root_dir',
        nargs='?',
        default='.',
        help='Root directory to search (default: current directory)'
    )

    parser.add_argument(
        '--folder',
        help='Filter tasks from specific folder (includes subfolders)'
    )

    parser.add_argument(
        '--due-on',
        metavar='DATE',
        help='Show tasks due on specific date (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--due-by',
        metavar='DATE',
        help='Show tasks due on or before date (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--due-between',
        nargs=2,
        metavar=('START', 'END'),
        help='Show tasks due between dates (YYYY-MM-DD YYYY-MM-DD)'
    )

    parser.add_argument(
        '--status',
        choices=['incomplete', 'completed', 'rescheduled', 'canceled', 'all'],
        default='incomplete',
        help='Filter by task status (default: incomplete)'
    )

    parser.add_argument(
        '--format',
        choices=['standard', 'condensed'],
        default='standard',
        help='Output format (default: standard)'
    )

    parser.add_argument(
        '--condensed',
        action='store_true',
        help='Use condensed output format (synonym for --format=condensed)'
    )

    args = parser.parse_args()

    # Determine output format (--condensed flag overrides --format)
    use_condensed = args.condensed or args.format == 'condensed'

    # Validate root directory
    if not os.path.isdir(args.root_dir):
        print(f"Error: {args.root_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Parse date arguments
    try:
        due_on, due_by, due_between = parse_date_filters(
            args.due_on, args.due_by, args.due_between)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Get current date
    today = date.today()

    if is_filtered(args.folder, due_on, due_by, due_between, args.status):
        lines = generate_filtered_report(args.root_dir, args.folder, due_on, due_by,
                                         due_between, args.status, use_condensed)
    else:
        # Use categorized report (for backward compatibility with templates)
        lines = generate_report(args.root_dir, today, use_condensed)

    print("\n".join(lines))


if __name__ == '__main__':
    main()
