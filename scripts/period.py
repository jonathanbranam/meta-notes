"""
Period parsing for --date options.

A period is a day, an inclusive range of days, a month, a quarter, or a
year, and resolves to an inclusive (START, END) pair of dates.
"""

import calendar
import re
from datetime import date

FORMS = ("YYYY-MM-DD, YYYY-MM-DD..YYYY-MM-DD, YYYY-MM, YYYY-Qn (n = 1-4), "
         "or YYYY")

_DAY = re.compile(r'^(\d{4})-(\d{2})-(\d{2})$')
_RANGE = re.compile(r'^(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})$')
_MONTH = re.compile(r'^(\d{4})-(\d{2})$')
_QUARTER = re.compile(r'^(\d{4})-Q([1-4])$')
_YEAR = re.compile(r'^(\d{4})$')


def _error(text: str) -> ValueError:
    return ValueError(f"Invalid date: {text}. Use {FORMS}.")


def _day(text: str, whole: str) -> date:
    match = _DAY.match(text)
    if not match:
        raise _error(whole)
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        raise _error(whole) from None


def parse_period(text: str | None, today: date | None = None) -> tuple[date, date]:
    """
    Resolve a --date value to an inclusive period.

    Args:
        text: The --date value, or None for today.
        today: Reference date for None (default: today).

    Returns:
        Tuple of (start, end) dates, both inclusive.

    Raises:
        ValueError: If text is not an accepted form, names a date that
            doesn't exist, or is a range whose start is after its end.
    """
    if text is None:
        day = today or date.today()
        return day, day

    if _DAY.match(text):
        day = _day(text, text)
        return day, day

    match = _RANGE.match(text)
    if match:
        start = _day(match.group(1), text)
        end = _day(match.group(2), text)
        if start > end:
            raise ValueError(f"Invalid date: {text}. The start of a range must not "
                             f"be after its end. Use {FORMS}.")
        return start, end

    match = _MONTH.match(text)
    if match:
        year, month = int(match.group(1)), int(match.group(2))
        if not 1 <= month <= 12:
            raise _error(text)
        return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])

    match = _QUARTER.match(text)
    if match:
        year, quarter = int(match.group(1)), int(match.group(2))
        first = 3 * quarter - 2
        last = first + 2
        return date(year, first, 1), date(year, last, calendar.monthrange(year, last)[1])

    match = _YEAR.match(text)
    if match:
        year = int(match.group(1))
        if year < 1:
            raise _error(text)
        return date(year, 1, 1), date(year, 12, 31)

    raise _error(text)
