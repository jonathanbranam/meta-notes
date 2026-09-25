"""
Unit tests for scripts/tags.py
"""

import sys
from pathlib import Path

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

import tags


# Tests for canonical_tag function

def test_canonical_tag_plain_name():
    assert tags.canonical_tag('design') == 'design'


def test_canonical_tag_strips_hash():
    assert tags.canonical_tag('#design') == 'design'


def test_canonical_tag_alias():
    assert tags.canonical_tag('#mtg') == 'meeting'
    assert tags.canonical_tag('mtg') == 'meeting'
    assert tags.canonical_tag('pers') == 'personal'
    assert tags.canonical_tag('#per') == 'personal'


def test_canonical_tag_alias_ignores_case():
    assert tags.canonical_tag('#MTG') == 'meeting'


def test_canonical_tag_keeps_case():
    assert tags.canonical_tag('#Admin') == 'Admin'


# Tests for parse_tags function

def test_parse_tags_several_tags():
    assert tags.parse_tags('- [ ] #aftr #design follow up 📅 2026-07-08') == ['aftr', 'design']


def test_parse_tags_before_and_after_text():
    assert tags.parse_tags('#first some text #second more') == ['first', 'second']


def test_parse_tags_hyphen_and_underscore():
    assert tags.parse_tags('#off-task and #snake_case') == ['off-task', 'snake_case']


def test_parse_tags_alias():
    assert tags.parse_tags('- [ ] #mtg prep 📅 2026-10-01') == ['meeting']


def test_parse_tags_duplicates_removed_ignoring_case():
    assert tags.parse_tags('#Admin #admin #ADMIN') == ['Admin']


def test_parse_tags_alias_duplicate_of_canonical():
    assert tags.parse_tags('#meeting #mtg') == ['meeting']


def test_parse_tags_none():
    assert tags.parse_tags('- [ ] no tags here') == []
