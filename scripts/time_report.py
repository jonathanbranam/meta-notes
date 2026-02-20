#!/usr/bin/env python3
"""
Generate time tracking report from a daily note file.

Reads time log and time block entries from a daily note and generates
a comprehensive report with:
- Total time by tag
- Work vs non-work breakdown
- Plan adherence statistics
- Weekly day-by-day summary
"""

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path

from time_tracking import (
    find_time_log_entries,
    find_time_block_entries,
    calculate_total_time_by_tag,
    calculate_work_vs_nonwork,
    calculate_plan_adherence,
    format_duration,
    analyze_work_day,
    format_week_summary,
)


def _parse_date_from_filepath(filepath: str) -> date | None:
    """
    Parse the date from a daily note filepath.

    Daily note filenames follow the pattern: YYYY-MM-DD Ddd.md
    """
    match = re.search(r'(\d{4}-\d{2}-\d{2})\s+\w{3}\.md$', filepath)
    if match:
        from datetime import datetime
        return datetime.strptime(match.group(1), '%Y-%m-%d').date()
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


def _get_week_analyses(filepath: str) -> list[tuple[date, dict | None]] | None:
    """
    Collect Mon-Fri work day analyses for the week containing filepath.

    Returns None if the date cannot be parsed from the filepath.
    """
    d = _parse_date_from_filepath(filepath)
    if d is None:
        return None

    notes_root = _find_notes_root(filepath)
    if notes_root is None:
        return None

    monday = d - timedelta(days=d.weekday())
    result = []
    for i in range(5):
        day = monday + timedelta(days=i)
        day_path = _daily_note_path(notes_root, day)
        if Path(day_path).exists():
            entries = find_time_log_entries(day_path)
            analysis = analyze_work_day(entries)
        else:
            analysis = None
        result.append((day, analysis))

    return result


def generate_report(filepath: str) -> str:
    """
    Generate a time tracking report from a daily note file.

    Args:
        filepath: Path to the daily note markdown file.

    Returns:
        Formatted report as a string.
    """
    # Parse time log entries and time blocks
    log_entries = find_time_log_entries(filepath)
    time_blocks = find_time_block_entries(filepath)

    # Build report sections
    report_lines = []
    report_lines.append("# Time Tracking Report")
    report_lines.append("")
    report_lines.append(f"File: {Path(filepath).name}")
    report_lines.append("")

    # Time Log Summary
    report_lines.append("## Time Log Summary")
    report_lines.append("")

    if not log_entries:
        report_lines.append("No time log entries found.")
        report_lines.append("")
    else:
        # Total time by tag
        tag_times = calculate_total_time_by_tag(log_entries)

        if tag_times:
            report_lines.append("### Time by Tag")
            report_lines.append("")

            # Sort by duration (descending)
            sorted_tags = sorted(tag_times.items(), key=lambda x: x[1], reverse=True)

            for tag, duration in sorted_tags:
                formatted_time = format_duration(duration)
                report_lines.append(f"- {tag}: {formatted_time}")

            report_lines.append("")

        # Work vs non-work breakdown
        work_time, nonwork_time = calculate_work_vs_nonwork(log_entries)
        total_logged = work_time + nonwork_time

        if total_logged.total_seconds() > 0:
            report_lines.append("### Work vs Non-Work")
            report_lines.append("")
            report_lines.append(f"- Work time: {format_duration(work_time)}")
            report_lines.append(f"- Non-work time: {format_duration(nonwork_time)}")
            report_lines.append(f"- Total logged: {format_duration(total_logged)}")

            work_percent = (work_time.total_seconds() / total_logged.total_seconds()) * 100
            report_lines.append(f"- Work percentage: {work_percent:.1f}%")
            report_lines.append("")

    # Plan Adherence Summary
    report_lines.append("## Plan Adherence")
    report_lines.append("")

    if not time_blocks:
        report_lines.append("No time block entries found.")
        report_lines.append("")
    else:
        stats = calculate_plan_adherence(time_blocks)

        if stats['total_blocks'] == 0:
            report_lines.append("No time blocks with plans found.")
            report_lines.append("")
        else:
            report_lines.append(f"### Summary ({stats['total_blocks']} blocks)")
            report_lines.append("")
            report_lines.append(f"- On-plan: {stats['on_plan_count']} blocks ({stats['on_plan_percent']:.1f}%)")
            report_lines.append(f"- Off-plan: {stats['off_plan_count']} blocks ({stats['off_plan_percent']:.1f}%)")
            report_lines.append(f"- Unplanned: {stats['unplanned_count']} blocks ({stats['unplanned_percent']:.1f}%)")
            report_lines.append("")

    # Week Summary
    week_analyses = _get_week_analyses(filepath)
    if week_analyses is not None:
        report_lines.append("## Week Summary")
        report_lines.append("")
        report_lines.append(format_week_summary(week_analyses))
        report_lines.append("")

    return "\n".join(report_lines)


def main():
    """Main entry point for the time report script."""
    parser = argparse.ArgumentParser(
        description="Generate time tracking report from a daily note."
    )
    parser.add_argument(
        "file",
        help="Path to the daily note markdown file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)"
    )

    args = parser.parse_args()

    # Check if file exists
    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Generate report
    report = generate_report(args.file)

    # Output report
    if args.output:
        Path(args.output).write_text(report)
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
