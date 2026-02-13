"""
Notes and wiki link management module.

Handles markdown file discovery and wiki link generation.
"""

import os
from datetime import date, timedelta


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


def calculate_week_start(today: date) -> date:
    """
    Calculate the start of the current week (Monday).

    Week runs Monday through Sunday. If today is Monday, returns today.
    Otherwise, returns the date of the previous Monday.

    Args:
        today: The reference date.

    Returns:
        The date of the current or previous Monday.
    """
    # weekday() returns 0 for Monday, 6 for Sunday
    days_since_monday = today.weekday()

    return today - timedelta(days=days_since_monday)


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
