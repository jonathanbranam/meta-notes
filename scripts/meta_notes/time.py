"""
Time report: the time_report.py report, plus structured results for --json.
"""

from datetime import date

import time_report


def run(root_dir: str, date_text: str | None = None,
        today: date | None = None) -> tuple[list[str], dict]:
    """
    Build the time report for a --date value.

    Args:
        root_dir: Notes root.
        date_text: A date-period value, or None for today.
        today: Reference date for the default (default: today).

    Returns:
        Tuple of (text lines identical to time_report.py --date, report
        data: the day report for a single day, else the period report).

    Raises:
        ValueError: If date_text is invalid, or a single day has no daily
            note.
    """
    data = time_report.build_report(root_dir, date_text, today)
    return time_report.format_report(data), data
