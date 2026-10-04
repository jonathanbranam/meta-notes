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
from meta_notes import hours

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


# Text added to the conventions for a mode where it differs from the other.
# Work, the default, adds none, so its conventions are unchanged. The skills
# take a root to be personal when this section is there.
MODE_TEXT: dict[str, str] = {
    "personal": """\
## Personal mode

This notes root is in **personal** mode. The skills follow the personal day:

- No PR, Slack or email steps. The next day is tomorrow, weekends included.
- There is no daily shutdown, and no `shutdown complete` marker in a daily
  note. `daily-plan` runs on its own.
- The weekly review and weekly plan happen on Sunday and cover the seven
  days Monday to Sunday. The review has no manager summary.
- Free time is the personal day (07:00 to 21:00); there are no 1-1s.
- In the Time Block, `work:` marks the exception; time is personal by
  default, so `pers:` isn't needed.""",
}

GENERATORS = {
    "workdays": hours.conventions_text,
    "statuses": lambda mode: _statuses(),
    "tag-aliases": lambda mode: _tag_aliases(),
}


def render(text: str, mode: str = "work") -> str:
    """
    Replace each generated marker in text with its generated block.

    Raises:
        KeyError: If a marker names no generator.
    """
    return MARKER_PATTERN.sub(lambda m: GENERATORS[m.group(1)](mode), text)


def run(mode: str = "work") -> str:
    """The conventions as markdown, with the mode's text appended if any."""
    text = render(CONVENTIONS_FILE.read_text(encoding="utf-8"), mode)
    extra = MODE_TEXT.get(mode)
    return text + "\n" + extra.strip("\n") + "\n" if extra else text
