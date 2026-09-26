"""
Conventions: the shared syntax and editing rules, printed as markdown.

The prose lives in conventions.md beside this module. Parts defined in code
are marked `<!-- generated: NAME -->` there and filled from tasks.py and
tags.py, so the printed text always matches the installed CLI.
"""

import re
import textwrap
from pathlib import Path

import tasks
from tags import TAG_ALIASES

CONVENTIONS_FILE = Path(__file__).with_name("conventions.md")

MARKER_PATTERN = re.compile(r"<!-- generated: ([\w-]+) -->")


def _statuses() -> str:
    # Characters with the same meaning share one entry: `x`/`X` done
    groups: dict[str, list[str]] = {}
    for char, meaning in tasks.STATUS_CHARS.items():
        groups.setdefault(meaning, []).append(f"`{char}`")
    items = [f"{'/'.join(chars)} {meaning}" for meaning, chars in groups.items()]
    return textwrap.fill("Status characters: " + ", ".join(items)
                         + ". Any other character reads as open.", 74,
                         break_on_hyphens=False)


def _tag_aliases() -> str:
    items = [f"`{alias}` for `{target}`" for alias, target in TAG_ALIASES.items()]
    return textwrap.fill("Aliases, read as their target in task queries, task "
                         "updates, and time logs: " + ", ".join(items) + ".", 74,
                         break_on_hyphens=False)


GENERATORS = {
    "statuses": _statuses,
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
