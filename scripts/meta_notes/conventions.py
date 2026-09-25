"""
Conventions: the shared syntax and editing rules, printed as markdown.

The prose lives in conventions.md beside this module. Parts defined in code
are marked `<!-- generated: NAME -->` there and filled from tasks.py and
tags.py, so the printed text always matches the installed CLI.
"""

import re
from pathlib import Path

import tasks
from tags import TAG_ALIASES

CONVENTIONS_FILE = Path(__file__).with_name("conventions.md")

MARKER_PATTERN = re.compile(r"<!-- generated: ([\w-]+) -->")


def _statuses() -> str:
    rows = ["| Line | Status |", "|---|---|"]
    rows += [f"| `- [{char}]` | {meaning} |"
             for char, meaning in tasks.STATUS_CHARS.items()]
    return "\n".join(rows)


def _due_emoji() -> str:
    first, *others = tasks.DUE_EMOJIS
    items = [f"- `{first}`: the one to write"]
    items += [f"- `{emoji}`: also read as a due date" for emoji in others]
    return "\n".join(items)


def _tag_aliases() -> str:
    rows = ["| Alias | Reads as |", "|---|---|"]
    rows += [f"| `{alias}` | `{target}` |"
             for alias, target in TAG_ALIASES.items()]
    return "\n".join(rows)


GENERATORS = {
    "statuses": _statuses,
    "due-emoji": _due_emoji,
    "tag-aliases": _tag_aliases,
}


def render(text: str) -> str:
    """
    Replace each generated marker in text with its generated block.

    Raises:
        KeyError: If a marker names no generator.
    """
    return MARKER_PATTERN.sub(lambda m: GENERATORS[m.group(1)](), text)


def run() -> str:
    """The conventions as markdown."""
    return render(CONVENTIONS_FILE.read_text(encoding="utf-8"))
