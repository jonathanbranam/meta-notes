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

import os
import sys

from tasks import Task, find_tasks_in_file
from notes import get_wiki_link, find_all_markdown_files


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
        print(f"## {wiki_link}\n")

        for task in tasks:
            print(task.text)

    # Print summary
    total_tasks: int = sum(len(tasks) for _, tasks in files_with_tasks)
    print(f"\n\nSummary: Found {total_tasks} tasks in {len(files_with_tasks)} files")


if __name__ == '__main__':
    main()
