"""
Ceremony status: which ceremony markers are checked for a day and its week.

A marker is a checkbox line whose text, without a trailing ✅ date, is the
marker name (ignoring case and surrounding whitespace). It is done when its
status is x or X. Notes are found where `meta-notes note daily|weekly`
writes them. Nothing is written.
"""

import re
from dataclasses import dataclass
from datetime import date

import tasks
from meta_notes import note, template

# (name, note kind, marker text), in report order
CEREMONIES = (
    ("daily-plan", "daily", "plan complete"),
    ("daily-shutdown", "daily", "shutdown complete"),
    ("weekly-review", "weekly", "review complete"),
    ("weekly-plan", "weekly", "plan complete"),
)

# A trailing completion date, with an optional emoji variation selector
_COMPLETED = re.compile(r"\s*✅️?\s*(\d{4}-\d{2}-\d{2})\s*$")


@dataclass
class Marker:
    """A marker's state in one note."""
    present: bool = False
    done: bool = False
    completed: date | None = None


def _completed_date(text: str) -> date | None:
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def find_marker(lines: list[str], name: str) -> Marker:
    """
    Find a marker in a note's lines.

    Args:
        lines: The note's lines.
        name: Marker text, such as 'shutdown complete'.

    Returns:
        Whether any line is the marker, whether any such line is done, and
        the latest ✅ date among the done lines.
    """
    marker = Marker()
    for line in lines:
        match = tasks.CHECKBOX_PATTERN.match(line)
        if not match:
            continue
        text = line[match.end():]
        completed = _COMPLETED.search(text)
        if completed:
            text = text[:completed.start()]
        if text.strip().lower() != name:
            continue
        marker.present = True
        if tasks.char_to_status(match.group(1)) != tasks.TaskStatus.COMPLETED:
            continue
        marker.done = True
        day = _completed_date(completed.group(1)) if completed else None
        if day and (marker.completed is None or day > marker.completed):
            marker.completed = day
    return marker


def _read_lines(path: str) -> list[str] | None:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return None


def status(day: date) -> dict:
    """
    Ceremony status for a day and the Monday-to-Sunday week containing it.

    Args:
        day: The day. Paths are relative to the current directory, which
            the CLI sets to the notes root.

    Returns:
        Dict with `date`, `week_start`, and `ceremonies`, a list of dicts
        with `name`, `note`, `note_exists`, `marker_present`, `done`, and
        `completed` (YYYY-MM-DD or None).
    """
    notes = {kind: note.periodic_note(kind, day)[0] for kind in ("daily", "weekly")}
    contents = {kind: _read_lines(path) for kind, path in notes.items()}
    ceremonies = []
    for name, kind, text in CEREMONIES:
        lines = contents[kind]
        marker = find_marker(lines, text) if lines is not None else Marker()
        ceremonies.append({
            "name": name,
            "note": notes[kind],
            "note_exists": lines is not None,
            "marker_present": marker.present,
            "done": marker.done,
            "completed": marker.completed.isoformat() if marker.completed else None,
        })
    return {"date": day.isoformat(),
            "week_start": template.week_start(day).isoformat(),
            "ceremonies": ceremonies}


def format_status(data: dict) -> list[str]:
    """Text lines for a status result, one per ceremony."""
    width = max(len(c["name"]) for c in data["ceremonies"]) + 1
    lines = []
    for c in data["ceremonies"]:
        line = f"{c['name'] + ':':<{width}} {'done' if c['done'] else 'not done'}"
        if c["completed"]:
            line += f" {c['completed']}"
        if not c["note_exists"]:
            line += " (no note)"
        elif not c["marker_present"]:
            line += " (no marker)"
        lines.append(line)
    return lines


def run(day: date) -> tuple[list[str], dict]:
    """Ceremony status as (text lines, JSON data)."""
    data = status(day)
    return format_status(data), data
