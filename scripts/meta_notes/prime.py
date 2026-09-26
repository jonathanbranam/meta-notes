"""
Prime: a guide to the notes root for an agent, printed as markdown.

The prose lives in prime.md beside this module. Parts defined in code are
marked `<!-- generated: NAME -->` there and filled in, as in conventions.py: today's plan note paths from note.py, the time report's
tag groups, the shipped skills, and the conventions themselves.
"""

import textwrap
from datetime import date
from pathlib import Path

from time_tracking import TAG_GROUPS
from meta_notes import conventions, init, note

PRIME_FILE = Path(__file__).with_name("prime.md")

NO_ROOT = ("> No notes root found here (a directory containing `.meta-notes`). "
           "Paths below are relative to a notes root; `meta-notes init` "
           "creates one.\n\n")

PLAN_KINDS = {
    "daily": "Daily",
    "weekly": "Weekly",
    "quarterly": "Quarterly",
    "yearly": "Yearly",
}


def _today_paths(today: date) -> str:
    lines = []
    for kind, label in PLAN_KINDS.items():
        path, _, _ = note.periodic_note(kind, today)
        lines.append(f"- {label}: `{path}`")
    return "\n".join(lines)


def _tag_groups(today: date) -> str:
    tags = [f"`{tag}`" for group in TAG_GROUPS.values() for tag in sorted(group)]
    return textwrap.fill("Common tags, which `meta-notes time` reports as "
                         "groups: " + ", ".join(tags) + ".", 74,
                         break_on_hyphens=False)


def _skills(today: date) -> str:
    names = ", ".join(f"`{name}`" for name in init.shipped_skills())
    return textwrap.fill("Skills in `.claude/skills/` run the planning "
                         f"ceremonies and answer calendar questions: {names}.",
                         74, break_on_hyphens=False)


GENERATORS = {
    "today-paths": _today_paths,
    "tag-groups": _tag_groups,
    "skills": _skills,
    "conventions": lambda today: conventions.run().removesuffix("\n"),
}


def render(text: str, today: date) -> str:
    """
    Replace each generated marker in text with its generated block.

    Raises:
        KeyError: If a marker names no generator.
    """
    return conventions.MARKER_PATTERN.sub(
        lambda m: GENERATORS[m.group(1)](today), text)


def run(root: str | None, today: date | None = None) -> str:
    """
    The guide as markdown.

    Args:
        root: The notes root, or None when there isn't one.
        today: Today's date (default: date.today()).
    """
    text = render(PRIME_FILE.read_text(encoding="utf-8"), today or date.today())
    return text if root else NO_ROOT + text
