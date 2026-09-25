"""
Unit tests for scripts/period.py
"""

import sys
from datetime import date
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from period import parse_period


# Tests for parse_period function: accepted forms

def test_parse_period_single_day():
    assert parse_period('2026-11-15') == (date(2026, 11, 15), date(2026, 11, 15))


def test_parse_period_range():
    assert parse_period('2026-11-02..2026-11-08') == (date(2026, 11, 2), date(2026, 11, 8))


def test_parse_period_range_same_day():
    assert parse_period('2026-11-02..2026-11-02') == (date(2026, 11, 2), date(2026, 11, 2))


def test_parse_period_month_february():
    assert parse_period('2026-02') == (date(2026, 2, 1), date(2026, 2, 28))


def test_parse_period_month_february_leap_year():
    assert parse_period('2028-02') == (date(2028, 2, 1), date(2028, 2, 29))


def test_parse_period_month_december():
    assert parse_period('2026-12') == (date(2026, 12, 1), date(2026, 12, 31))


def test_parse_period_quarter_q1():
    assert parse_period('2026-Q1') == (date(2026, 1, 1), date(2026, 3, 31))


def test_parse_period_quarter_q4():
    assert parse_period('2026-Q4') == (date(2026, 10, 1), date(2026, 12, 31))


def test_parse_period_year():
    assert parse_period('2026') == (date(2026, 1, 1), date(2026, 12, 31))


def test_parse_period_default_is_today():
    today = date(2026, 9, 25)
    assert parse_period(None, today) == (today, today)


def test_parse_period_default_without_today():
    assert parse_period(None) == (date.today(), date.today())


# Tests for parse_period function: invalid periods

@pytest.mark.parametrize('text', [
    'next-month',
    '2026-W45',
    '2026-02-30',
    '2026-11-08..2026-11-02',
    '2026-13',
    '2026-Q5',
    '2026-q4',
    '26-11-15',
    '2026-11-15..',
    '',
])
def test_parse_period_invalid(text):
    with pytest.raises(ValueError) as exc:
        parse_period(text)
    message = str(exc.value)
    assert f"Invalid date: {text}." in message
    assert 'YYYY-MM-DD..YYYY-MM-DD' in message
    assert 'YYYY-Qn' in message


def test_parse_period_reversed_range_explains():
    with pytest.raises(ValueError, match='start of a range'):
        parse_period('2026-11-08..2026-11-02')
