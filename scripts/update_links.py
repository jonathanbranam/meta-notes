#!/usr/bin/env python3
"""
Update wiki-style links across all markdown files.

When a file or folder is moved or renamed, this script updates all
wiki-style [[links]] that reference the old path to use the new path.
"""

import argparse
import os
import re
import sys
from pathlib import Path


def find_markdown_files(root_dir: str) -> list[Path]:
    """
    Find all markdown files in the repository.

    Args:
        root_dir: Root directory to search

    Returns:
        List of Path objects for all .md files
    """
    root_path = Path(root_dir)
    markdown_files = []

    for path in root_path.rglob("*.md"):
        # Skip hidden directories and files
        if any(part.startswith(".") for part in path.parts):
            continue
        markdown_files.append(path)

    return sorted(markdown_files)


def update_links_in_file(
    filepath: Path, old_path: str, new_path: str, dry_run: bool = False
) -> tuple[bool, int]:
    """
    Update wiki-style links in a single file.

    Args:
        filepath: Path to the markdown file
        old_path: Old path to find (without .md extension)
        new_path: New path to replace with (without .md extension)
        dry_run: If True, don't write changes

    Returns:
        Tuple of (changed, count) where changed is True if file was modified
        and count is the number of replacements made
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return False, 0

    # Pattern to match [[old_path]] or [[old_path/...]]
    # We need to match both exact matches and paths that start with old_path/
    # Use word boundary or path separator to avoid partial matches
    escaped_old = re.escape(old_path)

    # Match [[old_path]] or [[old_path/anything]]
    pattern = r"\[\[" + escaped_old + r"(/[^\]]*)?]]"

    def replace_link(match):
        """Replace matched link with new path."""
        suffix = match.group(1) or ""  # The /anything part, if present
        return f"[[{new_path}{suffix}]]"

    new_content, count = re.subn(pattern, replace_link, content)

    if count == 0:
        return False, 0

    if not dry_run:
        try:
            filepath.write_text(new_content, encoding="utf-8")
        except Exception as e:
            print(f"Error writing {filepath}: {e}", file=sys.stderr)
            return False, 0

    return True, count


def update_all_links(
    root_dir: str, old_path: str, new_path: str, dry_run: bool = False
) -> dict:
    """
    Update wiki-style links across all markdown files.

    Args:
        root_dir: Root directory to search
        old_path: Old path to find (without .md extension)
        new_path: New path to replace with (without .md extension)
        dry_run: If True, show what would be changed without writing

    Returns:
        Dictionary with statistics about the update
    """
    # Normalize paths (remove leading/trailing slashes)
    old_path = old_path.strip("/")
    new_path = new_path.strip("/")

    markdown_files = find_markdown_files(root_dir)

    stats = {
        "files_scanned": len(markdown_files),
        "files_modified": 0,
        "total_replacements": 0,
        "modified_files": [],
    }

    for filepath in markdown_files:
        changed, count = update_links_in_file(filepath, old_path, new_path, dry_run)

        if changed:
            stats["files_modified"] += 1
            stats["total_replacements"] += count
            stats["modified_files"].append((str(filepath), count))

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Update wiki-style links when files are moved or renamed"
    )
    parser.add_argument("old_path", help="Old path (without .md extension)")
    parser.add_argument("new_path", help="New path (without .md extension)")
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory to search (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without writing files",
    )

    args = parser.parse_args()

    # Run the update
    stats = update_all_links(args.root, args.old_path, args.new_path, args.dry_run)

    # Print results
    if args.dry_run:
        print("DRY RUN - No files were modified")
        print()

    print(f"Scanned {stats['files_scanned']} markdown files")
    print(f"Modified {stats['files_modified']} files")
    print(f"Made {stats['total_replacements']} replacements")

    if stats["modified_files"]:
        print("\nModified files:")
        for filepath, count in stats["modified_files"]:
            print(f"  {filepath}: {count} replacement(s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
