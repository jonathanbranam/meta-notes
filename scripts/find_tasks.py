#!/usr/bin/env python3
"""
Find and list tasks from markdown files.

Searches recursively through all markdown files and outputs:
- File name as a wiki link
- All tasks defined within that file

Task format: bullet (-, *, +) followed by [status]
- [ ] = uncompleted
- [x] or [X] = completed
- [>] = rescheduled
- [-] = canceled
"""

import os
import re
import sys


def find_tasks_in_file(filepath):
    """
    Find all task lines in a markdown file.

    Returns a list of tuples: (line_number, line_content, status)
    """
    tasks = []
    # Pattern: line starts with optional whitespace, bullet (-, *, +),
    # then space(s), then square brackets with a single character
    task_pattern = re.compile(r'^\s*[-*+]\s+\[(.)\]')

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                match = task_pattern.match(line)
                if match:
                    status = match.group(1)
                    tasks.append((line_num, line.rstrip(), status))
    except (IOError, UnicodeDecodeError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    return tasks


def get_wiki_link(filepath, root_dir):
    """
    Convert a file path to a wiki link format.

    Removes the root directory and .md extension.
    """
    # Get relative path from root
    rel_path = os.path.relpath(filepath, root_dir)
    # Remove .md extension if present
    if rel_path.endswith('.md'):
        rel_path = rel_path[:-3]
    return f"[[{rel_path}]]"


def find_all_markdown_files(root_dir):
    """
    Recursively find all markdown files in the given directory.
    """
    markdown_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]

        for filename in filenames:
            if filename.endswith('.md'):
                markdown_files.append(os.path.join(dirpath, filename))

    return sorted(markdown_files)


def categorize_status(status):
    """
    Categorize task status for display.
    """
    status_upper = status.upper()
    if status_upper == 'X':
        return 'completed'
    elif status == '>':
        return 'rescheduled'
    elif status == '-':
        return 'canceled'
    elif status == ' ':
        return 'pending'
    else:
        return 'other'


def main():
    """
    Main entry point for the script.
    """
    # Get the root directory from command line or use current directory
    root_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    if not os.path.isdir(root_dir):
        print(f"Error: {root_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Find all markdown files
    markdown_files = find_all_markdown_files(root_dir)

    if not markdown_files:
        print("No markdown files found.", file=sys.stderr)
        sys.exit(0)

    # Process each file and collect tasks
    files_with_tasks = []

    for filepath in markdown_files:
        tasks = find_tasks_in_file(filepath)
        if tasks:
            files_with_tasks.append((filepath, tasks))

    # Output results
    if not files_with_tasks:
        print("No tasks found in any markdown files.")
        return

    for filepath, tasks in files_with_tasks:
        wiki_link = get_wiki_link(filepath, root_dir)
        print(f"\n{wiki_link}")
        print("=" * len(wiki_link))

        for line_num, line_content, status in tasks:
            print(f"  {line_content}")

    # Print summary
    total_tasks = sum(len(tasks) for _, tasks in files_with_tasks)
    print(f"\n\nSummary: Found {total_tasks} tasks in {len(files_with_tasks)} files")


if __name__ == '__main__':
    main()
