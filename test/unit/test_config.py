"""
Unit tests for scripts/meta_notes/config.py

Tests reading .meta-notes as TOML config.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
repo_dir = Path(__file__).parent.parent.parent
scripts_dir = repo_dir / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import config, init


# Tests for load function

def test_config_load_existing_sentinel(tmp_path):
    """The sentinel init writes is valid, empty config."""
    (tmp_path / '.meta-notes').write_text(init.SENTINEL_CONTENT)

    assert config.load(str(tmp_path)) == {}


def test_config_load_calendar_table(tmp_path):
    """A [calendar] table is read with its values."""
    (tmp_path / '.meta-notes').write_text(
        init.SENTINEL_CONTENT + '\n[calendar]\nemail = "me@example.com"\n'
        'stale_days = 7\ncalendars = ["me@example.com"]\n')

    assert config.load(str(tmp_path)) == {'calendar': {
        'email': 'me@example.com', 'stale_days': 7,
        'calendars': ['me@example.com']}}


def test_config_load_unknown_key(tmp_path):
    """Unknown keys are read without error; callers ignore them."""
    (tmp_path / '.meta-notes').write_text(
        '[calendar]\ncolour = "blue"\nemail = "me@example.com"\n')

    calendar = config.table(config.load(str(tmp_path)), 'calendar')

    assert calendar['email'] == 'me@example.com'


def test_config_load_invalid_toml(tmp_path):
    """A parse error names .meta-notes and the line."""
    (tmp_path / '.meta-notes').write_text('# comment\n[calendar\n')

    with pytest.raises(ValueError) as exc:
        config.load(str(tmp_path))

    assert '.meta-notes' in str(exc.value)
    assert 'line 2' in str(exc.value)


# Tests for table function

def test_config_table_missing(tmp_path):
    """A missing table is empty."""
    assert config.table({}, 'calendar') == {}


def test_config_table_not_a_table(tmp_path):
    """A key that isn't a table is treated as missing."""
    assert config.table({'calendar': 'yes'}, 'calendar') == {}
