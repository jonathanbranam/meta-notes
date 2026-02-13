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


def generate_report(root_dir: str) -> list[str]:
    """
    Generate a complete report of incomplete tasks in all markdown files.

    Args:
        root_dir: Directory to search for markdown files.

    Returns:
        List of output lines for the complete report.
    """
    lines: list[str] = []

    # Find all markdown files
    markdown_files = find_all_markdown_files(root_dir)

    if not markdown_files:
        return ["No markdown files found."]

    # Process each file and collect incomplete tasks
    files_with_incomplete_tasks: list[tuple[str, list[Task]]] = []

    for filepath in markdown_files:
        all_tasks = find_tasks_in_file(filepath)
        incomplete_tasks = filter_incomplete_tasks(all_tasks)

        if incomplete_tasks:
            files_with_incomplete_tasks.append((filepath, incomplete_tasks))

    # Generate output
    if not files_with_incomplete_tasks:
        return ["No incomplete tasks found in any markdown files."]

    # Format each file's tasks
    for filepath, tasks in files_with_incomplete_tasks:
        file_lines = format_file_tasks(filepath, tasks, root_dir)
        lines.extend(file_lines)
        lines.append("")  # Empty line between files

    # Add summary
    total_tasks = sum(len(tasks) for _, tasks in files_with_incomplete_tasks)
    lines.append("")
    lines.append(f"Summary: Found {total_tasks} incomplete tasks in {len(files_with_incomplete_tasks)} files")

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

    # Generate and print report
    report_lines = generate_report(root_dir)
    output = "\n".join(report_lines)
    print(output)


if __name__ == '__main__':
    main()
