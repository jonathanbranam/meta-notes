"""
Prime: a guide to the notes root for an agent, printed as markdown.

The prose lives in prime.md beside this module. Parts defined in code or in
the notes root are marked `<!-- generated: NAME -->` there and filled in, as
in conventions.py: today's plan note paths from note.py, the daily and weekly
sections from the root's templates (or the shipped ones), the time report's
tag groups, the shipped skills, and the conventions themselves.
"""

import re
from datetime import date
from pathlib import Path

from time_tracking import TAG_GROUPS
from meta_notes import conventions, init, note

PRIME_FILE = Path(__file__).with_name("prime.md")

NO_ROOT = ("> No notes root found here (a directory containing `.meta-notes`). "
           "Paths below are relative to a notes root; `meta-notes init` "
           "creates one.\n\n")

PLAN_PATTERNS = {
    "daily": ("Daily", "plan/daily/YY-QN/YYYY-MM-DD Ddd.md"),
    "weekly": ("Weekly", "plan/week/YY-QN/YYYY-MM-DD.md"),
    "quarterly": ("Quarterly", "plan/quarter/YYYY-QN.md"),
    "yearly": ("Yearly", "plan/year/YYYY.md"),
}

HEADING_PATTERN = re.compile(r"(#{2,6})\s+(.+?)\s*$")


def _today_paths(root: Path | None, today: date) -> str:
    rows = []
    for kind, (label, pattern) in PLAN_PATTERNS.items():
        path, _, _ = note.periodic_note(kind, today)
        rows.append(f"| {label} | `{pattern}` | `{path}` |")
    return "\n".join(rows)


def _template_text(root: Path | None, name: str) -> str:
    """A template's text: the root's copy when readable, else the shipped one."""
    if root is not None:
        try:
            return (root / init.TEMPLATE_FOLDER / name).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            pass
    return (init.TEMPLATES_DIR / name).read_text(encoding="utf-8")


def template_sections(text: str) -> list[tuple[int, str]]:
    """
    The `##` and deeper headings of a template, skipping its front matter.

    Returns:
        (level, title) pairs, level 2 for `##`.
    """
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((i for i, line in enumerate(lines[1:], 1)
                    if line.strip() == "---"), 0)
        lines = lines[end + 1:]
    sections = []
    for line in lines:
        m = HEADING_PATTERN.match(line)
        if m:
            sections.append((len(m.group(1)), m.group(2)))
    return sections


def _sections(root: Path | None, name: str) -> str:
    sections = template_sections(_template_text(root, name))
    if not sections:
        return "- (none)"
    top = min(level for level, _ in sections)
    return "\n".join(f"{'  ' * (level - top)}- {title}"
                     for level, title in sections)


def _tag_groups(root: Path | None, today: date) -> str:
    return "\n".join(f"- {group}: " + ", ".join(f"`{t}`" for t in sorted(tags))
                     for group, tags in TAG_GROUPS.items())


def _skills(root: Path | None, today: date) -> str:
    names = init.shipped_skills()
    return "\n".join(f"- `{name}`" for name in names) or "- (none)"


GENERATORS = {
    "today-paths": _today_paths,
    "daily-sections": lambda root, today: _sections(root, "daily.md"),
    "weekly-sections": lambda root, today: _sections(root, "weekly.md"),
    "tag-groups": _tag_groups,
    "skills": _skills,
    "conventions": lambda root, today: conventions.run().removesuffix("\n"),
}


def render(text: str, root: Path | None, today: date) -> str:
    """
    Replace each generated marker in text with its generated block.

    Raises:
        KeyError: If a marker names no generator.
    """
    return conventions.MARKER_PATTERN.sub(
        lambda m: GENERATORS[m.group(1)](root, today), text)


def run(root: str | None, today: date | None = None) -> str:
    """
    The guide as markdown.

    Args:
        root: The notes root, or None when there isn't one.
        today: Today's date (default: date.today()).
    """
    root_path = Path(root) if root else None
    text = render(PRIME_FILE.read_text(encoding="utf-8"), root_path,
                  today or date.today())
    return text if root_path else NO_ROOT + text
