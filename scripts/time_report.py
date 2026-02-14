#!/usr/bin/env python3
"""
Generate time tracking report from a daily note file.

Reads time log and time block entries from a daily note and generates
a comprehensive report with:
- Total time by tag
- Work vs non-work breakdown
- Plan adherence statistics
"""

import argparse
import sys
from pathlib import Path

from time_tracking import (
    find_time_log_entries,
    find_time_block_entries,
    calculate_total_time_by_tag,
    calculate_work_vs_nonwork,
    calculate_plan_adherence,
    format_duration,
)


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
            report_lines.append(f"- Untracked: {stats['untracked_count']} blocks ({stats['untracked_percent']:.1f}%)")
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
