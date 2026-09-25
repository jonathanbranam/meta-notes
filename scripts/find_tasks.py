#!/usr/bin/env python3
"""
Find and list tasks from markdown files.

Searches recursively through all markdown files and lists the selected
tasks grouped by file, each file as a wiki link.

A checkbox line (-, *, or + followed by [status]) is a task only when it
has a due emoji (📅, 📆, or 🗓, with or without a date) or a start date
(🛫 YYYY-MM-DD). A bare due emoji marks an undated task. A completed
task's ✅ date stands in for its due date.

Status:
- [ ], [.], [o], [O], [/], or any other character = incomplete
- [x] or [X] = completed
- [>] = rescheduled
- [-] = canceled

Modes select tasks relative to the --date period START..END (default:
today). Each task is listed once, in the first matching selected mode:
- overdue: due before START
- due: due within START..END
- scheduled: due or start date within START..END
- ready: due or start date on or before END (the default mode)
- future: dated, but neither date on or before END
- undated: bare due emoji and no start date
--all selects ready, future, and undated. Tasks tagged #later are left out
unless --later is given.
"""

import argparse
import os
import sys
from datetime import date
from typing import Callable

from tasks import Task, TaskStatus, find_tasks_in_file, filter_tasks_by_status
from notes import get_wiki_link, find_all_markdown_files
from period import FORMS, parse_period
from tags import canonical_tag

# Sections in report order. A task is listed in the first selected one that
# matches it.
SECTIONS = ('overdue', 'due', 'scheduled', 'ready', 'future', 'undated')

# Modes that --all selects
ALL_MODES = ('ready', 'future', 'undated')

NOT_TAGGED = 'Not tagged'


def _on_or_before(day: date | None, end: date) -> bool:
    return day is not None and day <= end


def _within(day: date | None, start: date, end: date) -> bool:
    return day is not None and start <= day <= end


def _is_ready(task: Task, start: date, end: date) -> bool:
    return _on_or_before(task.effective_due, end) or _on_or_before(task.start_date, end)


PREDICATES: dict[str, Callable[[Task, date, date], bool]] = {
    'overdue': lambda t, start, end: t.effective_due is not None and t.effective_due < start,
    'due': lambda t, start, end: _within(t.effective_due, start, end),
    'scheduled': lambda t, start, end: (_within(t.effective_due, start, end)
                                        or _within(t.start_date, start, end)),
    'ready': _is_ready,
    'future': lambda t, start, end: ((t.effective_due is not None or t.start_date is not None)
                                     and not _is_ready(t, start, end)),
    'undated': lambda t, start, end: t.undated and t.start_date is None,
}


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


def filter_tasks_by_tags(tasks: list[Task], tags: list[str]) -> list[Task]:
    """
    Filter tasks to those with any of the given tags.

    Args:
        tasks: List of Task objects to filter.
        tags: Tag names, with or without #. Aliases apply and case is ignored.

    Returns:
        List containing only tasks with at least one of the tags.
    """
    wanted = {canonical_tag(tag).lower() for tag in tags}
    return [task for task in tasks
            if any(tag.lower() in wanted for tag in task.tags)]


def collect_tasks(markdown_files: list[str], root_dir: str, folder: str | None = None,
                  status: str = 'incomplete', tags: list[str] | None = None) -> list[Task]:
    """
    Collect tasks from markdown files, filtered by status, folder, and tags.

    Args:
        markdown_files: Files to read.
        root_dir: Root directory being searched (for --folder).
        folder: Only include tasks from this folder (and subfolders).
        status: Status argument ('incomplete', 'completed', 'all', ...).
        tags: Only include tasks with any of these tags.

    Returns:
        Matching tasks in file order.
    """
    all_tasks: list[Task] = []
    for filepath in markdown_files:
        all_tasks.extend(find_tasks_in_file(filepath))

    filtered_tasks = filter_tasks_by_status_arg(all_tasks, status)
    if folder:
        filtered_tasks = filter_tasks_by_folder(filtered_tasks, folder, root_dir)
    if tags:
        filtered_tasks = filter_tasks_by_tags(filtered_tasks, tags)
    return filtered_tasks


def resolve_modes(modes: list[str] | tuple[str, ...] | None) -> list[str]:
    """
    Expand --all and apply the default mode.

    Args:
        modes: Selected mode names, possibly including 'all'.

    Returns:
        Distinct mode names in section order. 'ready' when none is selected.
    """
    selected = set(modes or ())
    if 'all' in selected:
        selected.discard('all')
        selected.update(ALL_MODES)
    if not selected:
        selected = {'ready'}
    return [section for section in SECTIONS if section in selected]


def is_later(task: Task) -> bool:
    """Whether a task is tagged #later (any case)."""
    return any(tag.lower() == 'later' for tag in task.tags)


def select(tasks: list[Task], modes: list[str] | tuple[str, ...] | None,
           start: date, end: date, later: bool = False) -> list[tuple[str, Task]]:
    """
    Select tasks by mode for the period START..END.

    Args:
        tasks: Tasks to select from (already filtered by status, folder, tags).
        modes: Selected mode names ('all' expands; none means 'ready').
        start: First day of the period.
        end: Last day of the period.
        later: Include tasks tagged #later.

    Returns:
        (section, task) pairs, in the order of tasks. Each task appears at
        most once, in the first matching mode in section order.
    """
    sections = resolve_modes(modes)
    selected: list[tuple[str, Task]] = []
    for task in tasks:
        if not later and is_later(task):
            continue
        for section in sections:
            if PREDICATES[section](task, start, end):
                selected.append((section, task))
                break
    return selected


def sort_selection(selected: list[tuple[str, Task]]) -> list[tuple[str, Task]]:
    """Order selected tasks by section, then file path, then line."""
    return sorted(selected, key=lambda pair: (SECTIONS.index(pair[0]),
                                              pair[1].filename, pair[1].line_no))


def group_tasks_by_file(tasks: list[Task]) -> dict[str, list[Task]]:
    """Group tasks by filename, preserving task order within each file."""
    tasks_by_file: dict[str, list[Task]] = {}
    for task in tasks:
        tasks_by_file.setdefault(task.filename, []).append(task)
    return tasks_by_file


def group_tasks_by_tag(tasks: list[Task]) -> list[tuple[str, list[Task]]]:
    """
    Group tasks by tag, ignoring case.

    Args:
        tasks: Tasks to group.

    Returns:
        (heading, tasks) pairs, tags sorted ignoring case with 'Not tagged'
        last. A tag's heading is the first spelling seen. A task with several
        tags is in each of their groups.
    """
    groups: dict[str, tuple[str, list[Task]]] = {}
    untagged: list[Task] = []
    for task in tasks:
        if not task.tags:
            untagged.append(task)
        for tag in task.tags:
            groups.setdefault(tag.lower(), (tag, []))[1].append(task)
    result = [groups[key] for key in sorted(groups)]
    if untagged:
        result.append((NOT_TAGGED, untagged))
    return result


def format_file_tasks(filepath: str, tasks: list[Task], root_dir: str,
                      level: int = 2) -> list[str]:
    """
    Format tasks from a single file as output lines (standard format).

    Args:
        filepath: Path to the file containing tasks.
        tasks: List of Task objects from the file.
        root_dir: Root directory for generating wiki links.
        level: Heading level of the file heading.

    Returns:
        List of formatted output lines (empty if no tasks).
    """
    if not tasks:
        return []

    lines: list[str] = []
    wiki_link = get_wiki_link(filepath, root_dir)
    lines.append(f"{'#' * level} {wiki_link}")
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


def format_files(tasks: list[Task], root_dir: str, condensed: bool,
                 level: int = 2) -> list[str]:
    """Format tasks grouped by file, files sorted by path."""
    lines: list[str] = []
    tasks_by_file = group_tasks_by_file(tasks)
    for filepath in sorted(tasks_by_file):
        if condensed:
            lines.extend(format_file_tasks_condensed(filepath, tasks_by_file[filepath], root_dir))
        else:
            lines.extend(format_file_tasks(filepath, tasks_by_file[filepath], root_dir, level))
            lines.append("")  # Empty line between files (standard format only)
    return lines


def _add_heading(lines: list[str], heading: str) -> None:
    """Append a heading and a blank line, after a blank line if needed."""
    if lines and lines[-1] != "":
        lines.append("")
    lines.append(heading)
    lines.append("")


def build_report(selected: list[tuple[str, Task]], sections: list[str], root_dir: str,
                 group_by: str | None = None, condensed: bool = False) -> list[str]:
    """
    Build the report lines for selected tasks.

    Args:
        selected: (section, task) pairs from select, in sort_selection order.
        sections: The resolved modes. With more than one, each non-empty
            section gets a '# <Section>' heading.
        root_dir: Root directory for generating wiki links.
        group_by: 'tag' to list tasks under a heading per tag.
        condensed: If True, use condensed format.

    Returns:
        List of output lines.
    """
    if not selected:
        return ["No tasks found matching the criteria."]

    lines: list[str] = []
    for section in sections:
        tasks = [task for name, task in selected if name == section]
        if not tasks:
            continue
        if len(sections) > 1:
            _add_heading(lines, f"# {section.capitalize()}")
        if group_by == 'tag':
            for heading, tag_tasks in group_tasks_by_tag(tasks):
                _add_heading(lines, f"## {heading}")
                lines.extend(format_files(tag_tasks, root_dir, condensed, level=3))
        else:
            lines.extend(format_files(tasks, root_dir, condensed))

    # Add summary (not in condensed format)
    if not condensed:
        total_tasks = len(selected)
        total_files = len({task.filename for _, task in selected})
        task_word = "task" if total_tasks == 1 else "tasks"
        file_word = "file" if total_files == 1 else "files"
        lines.append("")
        lines.append(f"Summary: Found {total_tasks} {task_word} in {total_files} {file_word}")

    return lines


def run_query(root_dir: str, period: str | None = None,
              modes: list[str] | tuple[str, ...] | None = None, later: bool = False,
              tags: list[str] | None = None, group_by: str | None = None,
              folder: str | None = None, status: str = 'incomplete',
              condensed: bool = False,
              today: date | None = None) -> tuple[list[str], list[tuple[str, Task]]]:
    """
    Run a task query.

    Args:
        root_dir: Directory to search for markdown files.
        period: --date value (default: today).
        modes: Selected mode names ('all' expands; none means 'ready').
        later: Include tasks tagged #later.
        tags: Only include tasks with any of these tags.
        group_by: 'tag' to group the report by tag.
        folder: Only include tasks from this folder (and subfolders).
        status: Status argument ('incomplete', 'completed', 'all', ...).
        condensed: If True, use condensed format.
        today: Reference date for the default period (default: today).

    Returns:
        Tuple of (report lines, selected (section, task) pairs in report
        order, each task once).

    Raises:
        ValueError: If period is invalid.
    """
    start, end = parse_period(period, today)

    markdown_files = find_all_markdown_files(root_dir)
    if not markdown_files:
        return ["No markdown files found."], []

    sections = resolve_modes(modes)
    tasks = collect_tasks(markdown_files, root_dir, folder, status, tags)
    selected = sort_selection(select(tasks, sections, start, end, later))
    return build_report(selected, sections, root_dir, group_by, condensed), selected


def add_query_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the task query options (shared with `meta-notes tasks`)."""
    parser.add_argument(
        '--date',
        metavar='PERIOD',
        help=f'Day or period to select for (default: today): {FORMS}'
    )

    modes = parser.add_argument_group('modes (combine; default: --ready)')
    for mode, help_text in (
        ('scheduled', 'Due or start date within the period'),
        ('due', 'Due date within the period'),
        ('overdue', 'Due date before the period'),
        ('ready', 'Due or start date on or before the end of the period'),
        ('future', 'Dated, but not ready'),
        ('undated', 'Bare due emoji and no start date'),
        ('all', 'Ready, future, and undated tasks'),
    ):
        modes.add_argument(f'--{mode}', dest='modes', action='append_const',
                           const=mode, help=help_text)

    parser.add_argument(
        '--later',
        action='store_true',
        help='Include tasks tagged #later'
    )

    parser.add_argument(
        '--tag',
        action='append',
        dest='tags',
        metavar='TAG',
        help='Only tasks with this tag (repeatable; any tag matches)'
    )

    parser.add_argument(
        '--group-by',
        choices=['tag'],
        help='List tasks under a heading per tag'
    )

    parser.add_argument(
        '--folder',
        help='Filter tasks from specific folder (includes subfolders)'
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


def main() -> None:
    """
    Main entry point for the script.
    """
    parser = argparse.ArgumentParser(
        description='Find and list tasks from markdown files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                # Tasks ready today
  %(prog)s --due --date 2026-02-14        # Tasks due on a date
  %(prog)s --overdue                      # Tasks due before today
  %(prog)s --ready --date 2026-02-15      # Tasks ready by Sunday
  %(prog)s --scheduled --date 2026-11     # Tasks scheduled in November
  %(prog)s --due --date 2026-02-01..2026-02-28  # Tasks due in a range
  %(prog)s --all --folder project         # Every task in project/
  %(prog)s --all --later                  # Every task, including #later
  %(prog)s --status completed --due --date 2026-Q3  # Completed in Q3
  %(prog)s --tag admin --group-by tag     # Tasks tagged #admin
  %(prog)s --condensed                    # Condensed format output

Replacements for removed options:
  --due-on D            --due --date D
  --due-by D            --overdue --date D+1
  --due-between A B     --due --date A..B
        """
    )

    parser.add_argument(
        'root_dir',
        nargs='?',
        default='.',
        help='Root directory to search (default: current directory)'
    )

    add_query_arguments(parser)

    args = parser.parse_args()

    # Validate root directory
    if not os.path.isdir(args.root_dir):
        print(f"Error: {args.root_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    try:
        lines, _selected = run_query(
            args.root_dir, args.date, args.modes, args.later, args.tags,
            args.group_by, args.folder, args.status,
            args.condensed or args.format == 'condensed')
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print("\n".join(lines))


if __name__ == '__main__':
    main()
