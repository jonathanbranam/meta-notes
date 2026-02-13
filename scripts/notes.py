"""
Notes and wiki link management module.

Handles markdown file discovery and wiki link generation.
"""

import os


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
