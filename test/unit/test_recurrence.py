"""
Unit tests for scripts/recurrence.py
"""

import sys
from datetime import date
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from recurrence import Rule, next_date, parse_rule


# Tests for parse_rule

@pytest.mark.parametrize('text, expected', [
    ('every 3 months', Rule('month', 3, False)),
    ('every 2 weeks', Rule('week', 2, False)),
    ('every 10 days', Rule('day', 10, False)),
    ('every 2 years', Rule('year', 2, False)),
    ('every day', Rule('day', 1, False)),
    ('every week', Rule('week', 1, False)),
    ('every month', Rule('month', 1, False)),
    ('every year', Rule('year', 1, False)),
    ('every 1 month', Rule('month', 1, False)),
    ('every weekday', Rule('weekday', 1, False)),
])
def test_recurrence_parse_rule_forms(text, expected):
    assert parse_rule(text) == expected


def test_recurrence_parse_rule_when_done():
    assert parse_rule('every month when done') == Rule('month', 1, True)
    assert parse_rule('every 2 weeks when done') == Rule('week', 2, True)
    assert parse_rule('every weekday when done') == Rule('weekday', 1, True)


def test_recurrence_parse_rule_case_and_whitespace():
    assert parse_rule('  Every 3 Months  When Done ') == Rule('month', 3, True)


@pytest.mark.parametrize('text', [
    '', 'every', 'every 0 days', 'every other week', 'every Monday',
    'every month on the 1st', 'every January', 'daily', 'every 3',
    'every 3 fortnights', 'every -1 days', 'every 2 weekdays',
    'every month when', 'every month done',
])
def test_recurrence_parse_rule_unsupported(text):
    assert parse_rule(text) is None


# Tests for next_date

def test_recurrence_next_date_days_and_weeks():
    assert next_date(Rule('day', 1), date(2026, 9, 30)) == date(2026, 10, 1)
    assert next_date(Rule('day', 10), date(2026, 12, 25)) == date(2027, 1, 4)
    assert next_date(Rule('week', 2), date(2026, 9, 30)) == date(2026, 10, 14)


def test_recurrence_next_date_months():
    assert next_date(Rule('month', 3), date(2026, 7, 1)) == date(2026, 10, 1)
    assert next_date(Rule('month', 1), date(2026, 12, 15)) == date(2027, 1, 15)
    assert next_date(Rule('month', 13), date(2026, 1, 5)) == date(2027, 2, 5)


def test_recurrence_next_date_month_end_clamps():
    assert next_date(Rule('month', 1), date(2026, 1, 31)) == date(2026, 2, 28)
    assert next_date(Rule('month', 1), date(2028, 1, 31)) == date(2028, 2, 29)
    assert next_date(Rule('month', 1), date(2026, 3, 31)) == date(2026, 4, 30)
    assert next_date(Rule('month', 3), date(2026, 11, 30)) == date(2027, 2, 28)


def test_recurrence_next_date_years():
    assert next_date(Rule('year', 1), date(2026, 6, 15)) == date(2027, 6, 15)
    assert next_date(Rule('year', 2), date(2026, 6, 15)) == date(2028, 6, 15)


def test_recurrence_next_date_leap_day_clamps():
    assert next_date(Rule('year', 1), date(2028, 2, 29)) == date(2029, 2, 28)
    assert next_date(Rule('year', 4), date(2028, 2, 29)) == date(2032, 2, 29)


def test_recurrence_next_date_weekday_skips_weekend():
    # 2026-09-28 is a Monday
    assert next_date(Rule('weekday'), date(2026, 9, 28)) == date(2026, 9, 29)
    assert next_date(Rule('weekday'), date(2026, 10, 1)) == date(2026, 10, 2)
    assert next_date(Rule('weekday'), date(2026, 10, 2)) == date(2026, 10, 5)
    assert next_date(Rule('weekday'), date(2026, 10, 3)) == date(2026, 10, 5)
    assert next_date(Rule('weekday'), date(2026, 10, 4)) == date(2026, 10, 5)


def test_recurrence_next_date_late_completion_steps_from_base():
    # Due 2026-07-01, done 2026-10-05: the caller passes the due date, and the
    # result is already overdue, as in Obsidian.
    rule = parse_rule('every 3 months')
    assert next_date(rule, date(2026, 7, 1)) == date(2026, 10, 1)


def test_recurrence_next_date_when_done_steps_from_completion():
    # The caller passes the completion date for a when-done rule.
    rule = parse_rule('every 3 months when done')
    assert rule.when_done
    assert next_date(rule, date(2026, 10, 5)) == date(2027, 1, 5)


def test_recurrence_next_date_unknown_unit():
    with pytest.raises(ValueError):
        next_date(Rule('fortnight'), date(2026, 9, 30))
