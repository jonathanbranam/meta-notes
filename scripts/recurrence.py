"""
Recurrence rules for tasks, in Obsidian Tasks syntax.

A rule is the text after the repeat marker: `every [N] day|week|month|year[s]`
with an optional trailing `when done`, `every weekday`, or
`every [N] week[s] on <day>[, <day>...]` (day names, comma separated, with
`and` allowed before the last one).
"""

import calendar
import re
from dataclasses import dataclass
from datetime import date, timedelta

_RULE = re.compile(
    r'^every\s+(?:(\d+)\s+)?(day|week|month|year)s?(\s+when\s+done)?$',
    re.IGNORECASE)
_WEEKDAY = re.compile(r'^every\s+weekday(\s+when\s+done)?$', re.IGNORECASE)
_WEEK_ON = re.compile(
    r'^every\s+(?:(\d+)\s+)?weeks?\s+on\s+(.+?)(\s+when\s+done)?$',
    re.IGNORECASE)
_DAY_SEPARATOR = re.compile(r'\s*,\s*(?:and\s+)?|\s+and\s+', re.IGNORECASE)
_DAY_NAMES = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
              'saturday', 'sunday']


@dataclass(frozen=True)
class Rule:
    """
    A parsed rule. unit is day, week, month, year or weekday. A week rule
    with days holds the weekdays it recurs on (0 is Monday, as date.weekday).
    """
    unit: str
    interval: int = 1
    when_done: bool = False
    days: tuple[int, ...] = ()


def _parse_days(text: str) -> tuple[int, ...] | None:
    """The sorted weekday numbers named in text, or None if it isn't a list."""
    days = set()
    for name in _DAY_SEPARATOR.split(text):
        if name.lower() not in _DAY_NAMES:
            return None
        days.add(_DAY_NAMES.index(name.lower()))
    return tuple(sorted(days))


def parse_rule(text: str) -> Rule | None:
    """Parse rule text, or return None when it is not a supported rule."""
    text = text.strip()
    match = _WEEKDAY.match(text)
    if match:
        return Rule('weekday', 1, bool(match.group(1)))
    match = _WEEK_ON.match(text)
    if match:
        interval = int(match.group(1)) if match.group(1) else 1
        days = _parse_days(match.group(2))
        if interval < 1 or not days:
            return None
        return Rule('week', interval, bool(match.group(3)), days)
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


def _next_on_days(rule: Rule, base: date) -> date:
    """
    The next listed weekday after base. Weeks run Monday to Sunday: the
    listed days later in base's week come first, else the first listed day
    of the week `interval` weeks on.
    """
    monday = base - timedelta(days=base.weekday())
    later = [day for day in rule.days if day > base.weekday()]
    if later:
        return monday + timedelta(days=later[0])
    return monday + timedelta(weeks=rule.interval, days=rule.days[0])


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
        if rule.days:
            return _next_on_days(rule, base)
        return base + timedelta(weeks=rule.interval)
    if rule.unit == 'month':
        return _add_months(base, rule.interval)
    if rule.unit == 'year':
        return _add_months(base, 12 * rule.interval)
    if rule.unit == 'weekday':
        step = {4: 3, 5: 2}.get(base.weekday(), 1)
        return base + timedelta(days=step)
    raise ValueError(f"Unknown recurrence unit: {rule.unit}")
