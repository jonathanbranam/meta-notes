#!/usr/bin/env python3
"""
Find and list tasks from markdown files.

Searches recursively through all markdown files and outputs:
- File name as a wiki link
- All tasks defined within that file

Task format: bullet (-, *, +) followed by [status]
- [ ], [.], [o], [O], [/] = pending/uncompleted
- [x] or [X] = completed
- [>] = rescheduled
- [-] = canceled
"""

from dataclasses import dataclass
from enum import Enum
import os
import re
import sys


class TaskStatus(Enum):
    """Enum representing the status of a task."""
    PENDING = "pending"
    COMPLETED = "completed"
    RESCHEDULED = "rescheduled"
    CANCELED = "canceled"
    OTHER = "other"


@dataclass
class Task:
    """Represents a task found in a markdown file."""
    text: str
    status: TaskStatus
    filename: str
    line_no: int


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
                    task = Task(
                        text=line.rstrip(),
                        status=status,
                        filename=filepath,
                        line_no=line_num
                    )
                    tasks.append(task)
    except (IOError, UnicodeDecodeError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    return tasks


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
    elif status_char in (' ', '.', 'o', 'O', '/'):
        return TaskStatus.PENDING
    else:
        return TaskStatus.OTHER


def get_wiki_link(filepath: str, root_dir: str) -> str:
    """
    Convert a file path to a wiki link format.

    Args:
        filepath: Path to the file.
        root_dir: Root directory to make path relative to.

    Returns:
        Wiki link in the format [[path/to/file]].
    """
    # Get relative path from root
    rel_path = os.path.relpath(filepath, root_dir)
    # Remove .md extension if present
    if rel_path.endswith('.md'):
        rel_path = rel_path[:-3]
    return f"[[{rel_path}]]"


def find_all_markdown_files(root_dir: str) -> list[str]:
    """
    Recursively find all markdown files in the given directory.

    Args:
        root_dir: Directory to search for markdown files.

    Returns:
        Sorted list of paths to markdown files.
    """
    markdown_files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]

        for filename in filenames:
            if filename.endswith('.md'):
                markdown_files.append(os.path.join(dirpath, filename))

    return sorted(markdown_files)


def categorize_status(status: str) -> str:
    """
    Categorize task status for display.

    Args:
        status: Single character status indicator.

    Returns:
        String representation of the status category.
    """
    return _char_to_status(status).value


def main() -> None:
    """
    Main entry point for the script.
    """
    # Get the root directory from command line or use current directory
    root_dir: str = sys.argv[1] if len(sys.argv) > 1 else '.'

    if not os.path.isdir(root_dir):
        print(f"Error: {root_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Find all markdown files
    markdown_files: list[str] = find_all_markdown_files(root_dir)

    if not markdown_files:
        print("No markdown files found.", file=sys.stderr)
        sys.exit(0)

    # Process each file and collect tasks
    files_with_tasks: list[tuple[str, list[Task]]] = []

    for filepath in markdown_files:
        tasks: list[Task] = find_tasks_in_file(filepath)
        if tasks:
            files_with_tasks.append((filepath, tasks))

    # Output results
    if not files_with_tasks:
        print("No tasks found in any markdown files.")
        return

    for filepath, tasks in files_with_tasks:
        wiki_link: str = get_wiki_link(filepath, root_dir)
        print(f"\n{wiki_link}")
        print("=" * len(wiki_link))

        for task in tasks:
            print(f"  {task.text}")

    # Print summary
    total_tasks: int = sum(len(tasks) for _, tasks in files_with_tasks)
    print(f"\n\nSummary: Found {total_tasks} tasks in {len(files_with_tasks)} files")


if __name__ == '__main__':
    main()
