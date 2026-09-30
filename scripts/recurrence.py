"""
Recurrence rules for tasks, in Obsidian Tasks syntax.

A rule is the text after the repeat marker: `every [N] day|week|month|year[s]`
with an optional trailing `when done`, or `every weekday`.
"""

import calendar
import re
from dataclasses import dataclass
from datetime import date, timedelta

_RULE = re.compile(
    r'^every\s+(?:(\d+)\s+)?(day|week|month|year)s?(\s+when\s+done)?$',
    re.IGNORECASE)
_WEEKDAY = re.compile(r'^every\s+weekday(\s+when\s+done)?$', re.IGNORECASE)


@dataclass(frozen=True)
class Rule:
    """A parsed rule. unit is day, week, month, year or weekday."""
    unit: str
    interval: int = 1
    when_done: bool = False


def parse_rule(text: str) -> Rule | None:
    """Parse rule text, or return None when it is not a supported rule."""
    text = text.strip()
    match = _WEEKDAY.match(text)
    if match:
        return Rule('weekday', 1, bool(match.group(1)))
    match = _RULE.match(text)
    if not match:
        return None
    interval = int(match.group(1)) if match.group(1) else 1
    if interval < 1:
        return None
    return Rule(match.group(2).lower(), interval, bool(match.group(3)))


def _add_months(base: date, months: int) -> date:
    index = base.year * 12 + base.month - 1 + months
    year, month = divmod(index, 12)
    month += 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def next_date(rule: Rule, base: date) -> date:
    """
    The next occurrence after base.

    base is the due date, or the completion date for a when-done rule; the
    caller picks it. The result is not moved past today, so a late
    completion can give a date that is already overdue.
    """
    if rule.unit == 'day':
        return base + timedelta(days=rule.interval)
    if rule.unit == 'week':
        return base + timedelta(weeks=rule.interval)
    if rule.unit == 'month':
        return _add_months(base, rule.interval)
    if rule.unit == 'year':
        return _add_months(base, 12 * rule.interval)
    if rule.unit == 'weekday':
        step = {4: 3, 5: 2}.get(base.weekday(), 1)
        return base + timedelta(days=step)
    raise ValueError(f"Unknown recurrence unit: {rule.unit}")
