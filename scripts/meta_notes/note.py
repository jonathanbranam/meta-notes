"""
Create notes from templates: daily, weekly, quarterly, yearly, and by path.

Replaces the path and template-date logic of OpenDaily, OpenWeekPlan,
OpenQuarterPlan, OpenYearPlan, ExtractDateForTemplate, and Open in
autoload/meta_notes/notes.vim. Paths are relative to the current directory,
which the CLI sets to the notes root. An existing note is never written.
"""

import os
import re
from dataclasses import dataclass, field
from datetime import date

from meta_notes import template

PERIODIC_KINDS = ("daily", "weekly", "quarterly", "yearly")

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

# Ported from ExtractDateForTemplate; Vim's \w is [0-9A-Za-z_]
DAILY_PATH_RE = re.compile(
    r"plan/daily/\d{2}-Q\d/(\d{4}-\d{2}-\d{2})\s+[0-9A-Za-z_]{3}\.md$")
WEEKLY_PATH_RE = re.compile(
    r"plan/week/\d{2}-Q\d/(\d{4}-\d{2}-\d{2})(\s+[0-9A-Za-z_]{3})?\.md$")
QUARTERLY_PATH_RE = re.compile(r"plan/quarter/(\d{4})-(Q\d)\.md$")
YEARLY_PATH_RE = re.compile(r"plan/year/(\d{4})\.md$")

QUARTER_START_MONTHS = {"Q1": 1, "Q2": 4, "Q3": 7}


class NoteError(Exception):
    """A note couldn't be created; the message is shown to the user."""


@dataclass
class NoteResult:
    """Outcome of creating or rendering a note."""
    path: str
    exists: bool
    created: bool = False
    template: str | None = None
    content: str | None = None
    warnings: list[str] = field(default_factory=list)


def parse_date(value: str) -> date:
    """Parse a YYYY-MM-DD date, raising NoteError if it isn't one."""
    try:
        if DATE_RE.fullmatch(value):
            return date.fromisoformat(value)
    except ValueError:
        pass
    raise NoteError(f"Invalid date: {value} (expected YYYY-MM-DD)")


def _quarter_start(d: date) -> date:
    return date(d.year, (d.month - 1) // 3 * 3 + 1, 1)


def periodic_note(kind: str, d: date) -> tuple[str, date, str]:
    """
    Where a periodic note goes and how it is rendered.

    Args:
        kind: 'daily', 'weekly', 'quarterly', or 'yearly'.
        d: Any date in the note's period.

    Returns:
        (path, template date, fallback header).
    """
    if kind == "daily":
        day = f"{d.isoformat()} {template.day_abbr(d)}"
        return (f"plan/daily/{d:%y}-{template.quarter(d)}/{day}.md", d,
                f"# Daily Note - {day}")
    if kind == "weekly":
        monday = template.week_start(d)
        return (f"plan/week/{monday:%y}-{template.quarter(monday)}/"
                f"{monday.isoformat()}.md", monday,
                f"# Week Plan - {monday.isoformat()}")
    if kind == "quarterly":
        q = template.quarter(d)
        return (f"plan/quarter/{d.year}-{q}.md", _quarter_start(d),
                f"# Quarterly Plan - {d.year} {q}")
    if kind == "yearly":
        return (f"plan/year/{d.year}.md", date(d.year, 1, 1),
                f"# Year Plan - {d.year}")
    raise ValueError(f"Unknown note kind: {kind}")


def date_for_path(path: str, today: date) -> date:
    """
    The template date for a note at a path: from the name of a plan note,
    the same as its periodic kind, and today otherwise.
    """
    m = DAILY_PATH_RE.search(path) or WEEKLY_PATH_RE.search(path)
    if m:
        return parse_date(m.group(1))
    m = QUARTERLY_PATH_RE.search(path)
    if m:
        return date(int(m.group(1)), QUARTER_START_MONTHS.get(m.group(2), 10), 1)
    m = YEARLY_PATH_RE.search(path)
    if m:
        return date(int(m.group(1)), 1, 1)
    return today


def note_path(path: str) -> str:
    """
    Normalize a root-relative note path and append `.md` when missing.

    Raises:
        NoteError: If the path is empty or outside the notes root.
    """
    normalized = os.path.normpath(path) if path else ""
    if normalized in ("", "."):
        raise NoteError(f"Invalid note path: {path!r}")
    if (os.path.isabs(normalized) or normalized == ".."
            or normalized.startswith("../")):
        raise NoteError(f"Path is outside the notes root: {path}")
    return normalized if normalized.endswith(".md") else normalized + ".md"


def _write_new(path: str, content: str) -> bool:
    """Write a file that must not exist yet. Returns False if it does."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    try:
        with open(path, "x", encoding="utf-8", newline="") as f:
            f.write(content)
    except FileExistsError:
        return False
    return True


def create(kind: str, value: str | None = None, template_name: str | None = None,
           render_only: bool = False, today: date | None = None) -> NoteResult:
    """
    Create a note from its template, unless it already exists.

    Args:
        kind: 'daily', 'weekly', 'quarterly', 'yearly', or 'new'.
        value: For a periodic kind, a YYYY-MM-DD date in the period (default:
            today). For 'new', the note's path relative to the notes root.
        template_name: For 'new', use resource/template/<name>.md instead of
            template discovery.
        render_only: Render the note without writing anything.
        today: Today's date (default: date.today()).

    Returns:
        NoteResult. content is set when the note didn't exist.

    Raises:
        NoteError: For an invalid date or path, or a missing named template.
    """
    today = today or date.today()
    if kind == "new":
        path = note_path(value or "")
        note_date = date_for_path(path, today)
        header = f"# {path[:-3]}"
    else:
        path, note_date, header = periodic_note(
            kind, parse_date(value) if value else today)

    if template_name is not None:
        template_path = f"{template.TEMPLATE_FOLDER}/{template_name}.md"
        if not os.path.isfile(template_path):
            raise NoteError(f"Template not found: {template_path}")
    else:
        template_path = None

    if os.path.lexists(path):
        return NoteResult(path, exists=True)

    if template_path is None:
        template_path = template.find_template(path)

    result = NoteResult(path, exists=False, template=template_path)
    if template_path is None:
        lines = [header, ""]
        has_vim_blocks = False
    else:
        context = template.build_context(note_date, path, today)
        rendered = template.render(template_path, context)
        lines = rendered.lines
        has_vim_blocks = rendered.has_vim_blocks
        result.warnings.extend(rendered.warnings)
    result.content = "\n".join(lines) + "\n"

    if render_only:
        return result

    if not _write_new(path, result.content):
        # Created by someone else since the check; leave it alone
        return NoteResult(path, exists=True)
    result.created = True
    if has_vim_blocks:
        result.warnings.append(
            f"{path}: {{{{% vim %}}}} blocks are left as text outside Vim")
    return result
