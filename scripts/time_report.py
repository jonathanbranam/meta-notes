#!/usr/bin/env python3
"""
Generate a time tracking report from daily notes.

For one day, reads the day's time log and time block entries and reports:
- The day's log, with gaps and overlaps between entries
- The day's total time, including unlogged (missing) time
- Total time by tag
- Work vs non-work breakdown
- Plan adherence statistics
- A summary of the Monday-Sunday week

For a longer period, reports the period summary: total time, highlighted
tags, time per tag, and a summary of each day.

Reports are built as JSON-ready dicts (build_*) and rendered as text from
those dicts (format_*), so the text and JSON can't disagree.
"""

import argparse
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from period import parse_period
from time_tracking import (
    TimeLogEntry,
    find_time_log_entries,
    find_time_block_entries,
    calculate_work_vs_nonwork,
    calculate_plan_adherence,
    format_duration,
    format_duration_long,
    duration_minutes,
    day_log_items,
    day_totals,
    tag_totals,
    highlighted_totals,
)


def _parse_date_from_filepath(filepath: str) -> date | None:
    """
    Parse the date from a daily note filepath.

    Daily note filenames follow the pattern: YYYY-MM-DD Ddd.md
    """
    match = re.search(r'(\d{4}-\d{2}-\d{2})\s+\w{3}\.md$', filepath)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y-%m-%d').date()
        except ValueError:
            return None
    return None


def _find_notes_root(filepath: str) -> str | None:
    """
    Find the notes root directory from a daily note filepath.

    Looks for the 'plan' directory component and returns its parent.
    """
    parts = Path(filepath).parts
    for i, part in enumerate(parts):
        if part == 'plan' and i + 1 < len(parts) and parts[i + 1] == 'daily':
            return str(Path(*parts[:i]))
    return None


def _daily_note_path(notes_root: str, d: date) -> str:
    """
    Construct the expected filepath for a daily note.

    Pattern: plan/daily/YY-Q#/YYYY-MM-DD Ddd.md
    """
    quarter_num = (d.month - 1) // 3 + 1
    year_short = d.strftime('%y')
    day_abbr = d.strftime('%a')
    folder = f'{year_short}-Q{quarter_num}'
    filename = f'{d.strftime("%Y-%m-%d")} {day_abbr}.md'
    return str(Path(notes_root) / 'plan' / 'daily' / folder / filename)


def _load_days(notes_root: str, start: date,
               end: date) -> list[tuple[date, list[TimeLogEntry] | None]]:
    """
    Read the time log of every day from start to end.

    Args:
        notes_root: Notes root directory.
        start: First day, inclusive.
        end: Last day, inclusive.

    Returns:
        (date, entries) for each day in order, where entries is None when
        the day has no daily note.
    """
    days = []
    day = start
    while day <= end:
        path = _daily_note_path(notes_root, day)
        days.append((day, find_time_log_entries(path) if Path(path).exists() else None))
        day += timedelta(days=1)
    return days


def build_period_report(notes_root: str, start: date, end: date) -> dict:
    """
    Summarize the time logs from start to end.

    Args:
        notes_root: Notes root directory.
        start: First day, inclusive.
        end: Last day, inclusive.

    Returns:
        Dict with 'start', 'end', 'work_minutes', 'total_minutes',
        'highlighted' ([{label, minutes}]), 'by_tag' ({tag: minutes},
        alphabetical), and 'days' ([{date, weekday, logged, work_minutes,
        earliest, latest, span_minutes}]).
    """
    all_entries: list[TimeLogEntry] = []
    days = []
    work = total = 0
    for day, entries in _load_days(notes_root, start, end):
        # Entries without any time (such as the template's HH:MM
        # placeholders) don't make a day logged
        logged = any(e.start_time or e.end_time for e in entries or [])
        item = {'date': day.isoformat(), 'weekday': day.strftime('%a'),
                'logged': logged}
        if logged:
            totals = day_totals(entries)
            work += totals['work_minutes']
            total += totals['total_minutes']
            item.update(work_minutes=totals['work_minutes'],
                        earliest=totals['earliest'], latest=totals['latest'],
                        span_minutes=totals['span_minutes'])
            all_entries.extend(entries)
        else:
            item.update(work_minutes=0, earliest=None, latest=None, span_minutes=None)
        days.append(item)

    by_tag = tag_totals(all_entries)
    return {
        'start': start.isoformat(),
        'end': end.isoformat(),
        'work_minutes': work,
        'total_minutes': total,
        'highlighted': [{'label': label, 'minutes': duration_minutes(d)}
                        for label, d in highlighted_totals(all_entries)],
        'by_tag': {tag: duration_minutes(by_tag[tag])
                   for tag in sorted(by_tag, key=str.lower)},
        'days': days,
    }


def build_day_report(notes_root: str | None, day: date | None, path: str) -> dict:
    """
    Build the report for one daily note.

    Args:
        notes_root: Notes root directory, for the week summary; None to
            leave the week out.
        day: The note's date; None to leave the week out.
        path: Path to the daily note.

    Returns:
        Dict with 'start' and 'end' (the day), 'kind' ('day'), 'file',
        'entries' (see day_log_items), 'totals' (see day_totals), 'by_tag'
        ({tag: minutes}, most time first), 'work_vs_nonwork',
        'plan_adherence' (None without time blocks), and 'week' (see
        build_period_report, or None).
    """
    entries = find_time_log_entries(path)
    blocks = find_time_block_entries(path)

    by_tag = tag_totals(entries)
    work, nonwork = calculate_work_vs_nonwork(entries)
    logged = work + nonwork

    week = None
    if notes_root is not None and day is not None:
        monday = day - timedelta(days=day.weekday())
        week = build_period_report(notes_root, monday, monday + timedelta(days=6))

    return {
        'start': day.isoformat() if day else None,
        'end': day.isoformat() if day else None,
        'kind': 'day',
        'file': os.path.relpath(path, notes_root) if notes_root is not None else path,
        'entries': day_log_items(entries),
        'totals': day_totals(entries),
        'by_tag': {tag: duration_minutes(d) for tag, d in
                   sorted(by_tag.items(), key=lambda x: x[1], reverse=True)},
        'work_vs_nonwork': {
            'work_minutes': duration_minutes(work),
            'nonwork_minutes': duration_minutes(nonwork),
            'total_minutes': duration_minutes(logged),
            'work_percent': (work / logged * 100) if logged else None,
        },
        'plan_adherence': calculate_plan_adherence(blocks) if blocks else None,
        'week': week,
    }


def _minutes(minutes: int) -> str:
    return format_duration_long(timedelta(minutes=minutes))


def _field(bullet: str, label: str, value: str) -> str:
    """A '- label:    value' line with the values aligned."""
    return f"{bullet} {(label + ':').ljust(17)} {value}"


def _format_entry(item: dict) -> list[str]:
    if item['kind'] == 'gap':
        title = f"*GAP of {item['minutes']} min*"
    elif item['kind'] == 'overlap':
        title = f"*Overlap of {item['minutes']} min*"
    else:
        title = item['text']

    lines = [f"- {title}",
             f"  * start: {item['start'] or '*MISSING START TIME*'}",
             f"  * end:   {item['end'] or '*MISSING END TIME*'}"]
    if item['kind'] == 'entry':
        if item['minutes'] is not None:
            lines.append(f"  * time:  {_minutes(item['minutes'])}")
        if item['tags']:
            lines.append(f"  * tags:  {' '.join(item['tags'])}")
    return lines


def format_period_summary(data: dict) -> list[str]:
    """
    Render a period summary (see build_period_report) as text lines.
    """
    lines = [f"## Summary for {data['start']} to {data['end']}", "",
             "### Total Time", "",
             _field('-', 'work duration', _minutes(data['work_minutes'])),
             _field('-', 'total duration', _minutes(data['total_minutes']))]
    for item in data['highlighted']:
        lines.append(_field('-', item['label'], _minutes(item['minutes'])))
    lines.append("")

    lines += ["### Time per tag", ""]
    if data['by_tag']:
        lines += [_field('-', tag, _minutes(m)) for tag, m in data['by_tag'].items()]
    else:
        lines.append("No tagged time.")
    lines.append("")

    lines += ["### Day Summaries", ""]
    for day in data['days']:
        lines.append(f"- {day['date']} {day['weekday']}")
        if not day['logged']:
            lines.append("  * (no log)")
            continue
        lines += [
            _field('  *', 'work duration', _minutes(day['work_minutes'])),
            _field('  *', 'earliest time', day['earliest']),
            _field('  *', 'latest time', day['latest']),
            _field('  *', 'total time', _minutes(day['span_minutes'])),
        ]
    return lines


def format_period_report(data: dict) -> list[str]:
    """
    Render a period report (see build_period_report) as text lines.
    """
    return ["# Time Tracking Report", ""] + format_period_summary(data)


def format_day_report(data: dict) -> list[str]:
    """
    Render a day report (see build_day_report) as text lines.
    """
    lines = ["# Time Tracking Report", "",
             f"File: {Path(data['file']).name}", "",
             "## Time Log", ""]

    entries = data['entries']
    if not entries:
        lines += ["No time log entries found.", ""]
    else:
        for item in entries:
            lines += _format_entry(item)
        lines.append("")

        totals = data['totals']
        lines += ["### Total Time", "",
                  _field('-', 'work duration', _minutes(totals['work_minutes'])),
                  _field('-', 'total duration', _minutes(totals['total_minutes']))]
        if totals['earliest'] is not None:
            lines += [_field('-', 'earliest time', totals['earliest']),
                      _field('-', 'latest time', totals['latest']),
                      _field('-', 'total time', _minutes(totals['span_minutes']))]
        if totals['missing_minutes'] is not None:
            lines.append(_field('-', '*missing time*', _minutes(totals['missing_minutes'])))
        lines.append("")

        lines += ["## Time Log Summary", ""]
        if data['by_tag']:
            lines += ["### Time by Tag", ""]
            for tag, minutes in data['by_tag'].items():
                lines.append(f"- #{tag}: {format_duration(timedelta(minutes=minutes))}")
            lines.append("")

        split = data['work_vs_nonwork']
        if split['total_minutes'] > 0:
            lines += ["### Work vs Non-Work", "",
                      f"- Work time: {format_duration(timedelta(minutes=split['work_minutes']))}",
                      f"- Non-work time: {format_duration(timedelta(minutes=split['nonwork_minutes']))}",
                      f"- Total logged: {format_duration(timedelta(minutes=split['total_minutes']))}",
                      f"- Work percentage: {split['work_percent']:.1f}%",
                      ""]

    lines += ["## Plan Adherence", ""]
    stats = data['plan_adherence']
    if stats is None:
        lines.append("No time block entries found.")
    elif stats['total_blocks'] == 0:
        lines.append("No time blocks with plans found.")
    else:
        lines += [f"### Summary ({stats['total_blocks']} blocks)", "",
                  f"- On-plan: {stats['on_plan_count']} blocks ({stats['on_plan_percent']:.1f}%)",
                  f"- Off-plan: {stats['off_plan_count']} blocks ({stats['off_plan_percent']:.1f}%)",
                  f"- Unplanned: {stats['unplanned_count']} blocks ({stats['unplanned_percent']:.1f}%)"]

    if data['week'] is not None:
        lines += [""] + format_period_summary(data['week'])
    return lines


def build_report(notes_root: str, date_text: str | None,
                 today: date | None = None) -> dict:
    """
    Build the report selected by a --date value.

    Args:
        notes_root: Notes root directory.
        date_text: A date-period value, or None for today.
        today: Reference date for None (default: today).

    Returns:
        The day report (see build_day_report) for a single day, otherwise
        the period report: build_period_report's dict with 'kind' 'period'.

    Raises:
        ValueError: If date_text is invalid, or a single day has no daily
            note.
    """
    start, end = parse_period(date_text, today)
    if start == end:
        path = _daily_note_path(notes_root, start)
        if not Path(path).exists():
            raise ValueError(f"Daily note not found: {path}")
        return build_day_report(notes_root, start, path)
    data = build_period_report(notes_root, start, end)
    return {'kind': 'period', **data}


def format_report(data: dict) -> list[str]:
    """Render a report from build_report as text lines."""
    if data['kind'] == 'day':
        return format_day_report(data)
    return format_period_report(data)


def generate_report(filepath: str) -> str:
    """
    Generate a time tracking report from a daily note file.

    Args:
        filepath: Path to the daily note markdown file.

    Returns:
        Formatted report as a string.
    """
    data = build_day_report(_find_notes_root(filepath),
                            _parse_date_from_filepath(filepath), filepath)
    return "\n".join(format_day_report(data))


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the time report script. Returns the exit code."""
    parser = argparse.ArgumentParser(
        description="Generate a time tracking report from daily notes."
    )
    parser.add_argument(
        "file", nargs="?",
        help="Path to a daily note (default: the note for --date)"
    )
    parser.add_argument(
        "--date", metavar="DATE",
        help="YYYY-MM-DD for a day report; YYYY-MM-DD..YYYY-MM-DD, YYYY-MM, "
             "YYYY-Qn, or YYYY for a period report (default: today). Daily "
             "notes are found under the current directory."
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)"
    )

    args = parser.parse_args(argv)

    if args.file and args.date:
        print("Error: Give a file or --date, not both.", file=sys.stderr)
        return 1

    if args.file:
        if not Path(args.file).exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            return 1
        report = generate_report(args.file)
    else:
        try:
            report = "\n".join(format_report(build_report(".", args.date)))
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    if args.output:
        Path(args.output).write_text(report)
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
