"""
Unit tests for scripts/meta_notes/conventions.py
"""

import sys
from pathlib import Path

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

import tasks
from meta_notes import conventions
from tags import TAG_ALIASES


# Tests for run function

def test_run_replaces_every_marker():
    source = conventions.CONVENTIONS_FILE.read_text(encoding='utf-8')
    markers = conventions.MARKER_PATTERN.findall(source)

    text = conventions.run()

    assert sorted(markers) == sorted(conventions.GENERATORS)
    assert '<!-- generated' not in text


def test_run_lists_every_tag_alias():
    text = conventions.run()

    for alias, target in TAG_ALIASES.items():
        assert f"| `{alias}` | `{target}` |" in text
    assert "| `#waiting` | `#wait` |" in text


def test_run_lists_due_emoji_with_one_to_write():
    text = conventions.run()

    assert "- `📅`: the one to write" in text
    assert "- `📆`: also read as a due date" in text
    assert "- `🗓`: also read as a due date" in text


def test_run_lists_every_status_character():
    text = conventions.run()

    for char, meaning in tasks.STATUS_CHARS.items():
        assert f"| `- [{char}]` | {meaning} |" in text


def test_run_includes_task_update_rule():
    text = conventions.run()

    assert "meta-notes task update <file>:<line> --expect <text>" in text


def test_run_covers_required_topics():
    text = conventions.run()

    for phrase in ('🛫', '✅', '80 columns', '#next', '#later', '#wait',
                   '#review', '#deadline', 'Home.md', '`status`', '`tag`',
                   '`archived`', "--status '>'", 'shutdown complete',
                   'review complete', 'plan complete', '--status x',
                   'meta-notes move', 'rename', 'archive'):
        assert phrase in text, phrase


def test_run_lines_fit_in_80_columns():
    for line in conventions.run().splitlines():
        if not line.startswith('|'):
            assert len(line) <= 80, line


# Tests for render function

def test_render_leaves_other_text_alone():
    assert conventions.render("plain\n") == "plain\n"
