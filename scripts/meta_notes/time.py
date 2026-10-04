"""
Time report: the time_report.py report, plus structured results for --json.
"""

import os
from datetime import date

import time_report
from meta_notes import config
from meta_notes.root import SENTINEL


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
            note, or the root's mode is invalid.
    """
    # A root given by --root may have no sentinel yet: that is work mode
    has_sentinel = os.path.exists(os.path.join(root_dir, SENTINEL))
    mode = config.mode(root_dir) if has_sentinel else 'work'
    data = time_report.build_report(root_dir, date_text, today, mode)
    return time_report.format_report(data), data
