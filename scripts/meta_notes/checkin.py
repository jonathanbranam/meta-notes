"""
Stay-on-task check-ins: read and fill the daily note's Time Block.

The Time Block is the table under `### Time Block`. Its rows start with a
12-hour time; the Plan and Actual cells are found by the header names.
`wait` sleeps until a check-in is due, so a calling agent wakes when it
exits. Only `fill_actual` writes.
"""

import re
import time as _time
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from meta_notes import note

DEFAULT_INTERVAL = 30
DEFAULT_END = "17:30"
# How often wait re-reads the clock, so a sleeping machine wakes to a due
# check-in within this many seconds
TICK_SECONDS = 30

_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_ROW_TIME = re.compile(r"^(\d{1,2}):(\d{2})\s*([ap])m$", re.IGNORECASE)
_CLOCK = re.compile(r"^(\d{1,2}):(\d{2})$")


@dataclass
class Row:
    """A Time Block row: its line index and cells."""
    index: int
    time: time
    label: str
    plan: str
    actual: str


def parse_time(text: str) -> time:
    """
    Parse `HH:MM` (24-hour) or `9:15am` (12-hour).

    Raises:
        ValueError: If the text is neither, or names an invalid time.
    """
    text = text.strip()
    match = _ROW_TIME.match(text)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if not 1 <= hour <= 12:
            raise ValueError(f"invalid time: {text!r}")
        hour = hour % 12 + (12 if match.group(3).lower() == "p" else 0)
        return time(hour, minute)
    match = _CLOCK.match(text)
    if match:
        try:
            return time(int(match.group(1)), int(match.group(2)))
        except ValueError:
            pass
    raise ValueError(f"invalid time: {text!r}; use HH:MM or 9:15am")


_SEPARATOR = re.compile(r"^[\s:|-]+$")


@dataclass
class Layout:
    """The Time Block table's header: cell names and the Plan/Actual cells."""
    names: list[str]
    plan: int
    actual: int

    def column(self, name: str) -> int:
        """The `split("|")` index of the "plan" or "actual" cell."""
        return self.plan if name == "plan" else self.actual


def _block_lines(lines: list[str]) -> list[tuple[int, str]]:
    """The table lines under `### Time Block`, with their indexes."""
    found = []
    in_block = False
    for index, line in enumerate(lines):
        heading = _HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            if heading.group(2).lower() == "time block" and level == 3:
                in_block = True
                continue
            if in_block and level <= 3:
                break
        if in_block and line.lstrip().startswith("|"):
            found.append((index, line))
    return found


def layout(lines: list[str]) -> Layout:
    """
    The Time Block's columns, found by the table's header names.

    Raises:
        ValueError: If the table has no header with both Plan and Actual;
            the message names the headers it found.
    """
    found = []
    for _, line in _block_lines(lines):
        if _SEPARATOR.match(line):
            continue
        cells = line.strip().strip("|").split("|")
        try:
            parse_time(cells[0])
            continue
        except ValueError:
            pass
        names = [c.strip() for c in cells]
        lower = [n.lower() for n in names]
        if "plan" in lower and "actual" in lower:
            # +1: split("|") has an empty first cell before the leading |
            return Layout(names, lower.index("plan") + 1,
                          lower.index("actual") + 1)
        found = names
    raise ValueError("the Time Block table needs Plan and Actual headers; "
                     f"found: {', '.join(found) or 'none'}")


def time_block_rows(lines: list[str]) -> list[Row]:
    """
    The Time Block's rows, in order; [] when there is no Time Block.

    Raises:
        ValueError: If there are rows but the header lacks Plan or Actual.
    """
    parsed = []
    for index, line in _block_lines(lines):
        cells = line.split("|")
        if len(cells) < 3:
            continue
        try:
            at = parse_time(cells[1])
        except ValueError:
            continue
        parsed.append((index, at, cells))
    if not parsed:
        return []
    cols = layout(lines)

    def cell(cells, col):
        return cells[col].strip() if col < len(cells) - 1 else ""

    return [Row(index, at, cells[1].strip(), cell(cells, cols.plan),
                cell(cells, cols.actual))
            for index, at, cells in parsed]


def _read_lines(path: str) -> list[str] | None:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return None


def report(rows: list[Row], at: time) -> tuple[Row | None, list[Row]]:
    """
    The current row at a time, and the rows still unfilled before it.

    Unfilled rows are those before the current one with an empty Actual,
    counted from the row after the last filled Actual, or from the first
    row with a Plan when none is filled.
    """
    current = None
    for i, row in enumerate(rows):
        if row.time <= at:
            current = i
    if current is None:
        return None, []
    filled = [i for i in range(current + 1) if rows[i].actual]
    if filled:
        start = filled[-1] + 1
    else:
        start = next((i for i, r in enumerate(rows) if r.plan), current)
    return rows[current], [r for r in rows[start:current] if not r.actual]


def status(day: date, at: time) -> dict:
    """
    The check-in report for a day's daily note at a time.

    Args:
        day: The day. Paths are relative to the current directory, which
            the CLI sets to the notes root.
        at: The time of day.

    Returns:
        Dict with `date`, `time`, `note`, `note_exists`, `current` (dict
        with `time`, `plan`, `actual`, or None) and `unfilled` (list of
        dicts with `time` and `plan`).
    """
    path = note.periodic_note("daily", day)[0]
    lines = _read_lines(path)
    current, unfilled = report(time_block_rows(lines or []), at)
    return {
        "date": day.isoformat(),
        "time": at.strftime("%H:%M"),
        "note": path,
        "note_exists": lines is not None,
        "current": ({"time": current.label, "plan": current.plan,
                     "actual": current.actual} if current else None),
        "unfilled": [{"time": r.label, "plan": r.plan} for r in unfilled],
    }


def format_status(data: dict) -> list[str]:
    """Text lines for a status result."""
    if not data["note_exists"]:
        return [f"{data['time']} no daily note ({data['note']})"]
    cur = data["current"]
    head = f"{data['time']} now: "
    if cur is None:
        head += "no Time Block row yet"
    else:
        head += f"{cur['time']} {cur['plan'] or '(no plan)'}"
        if cur["actual"]:
            head += f" -> {cur['actual']}"
    lines = [head]
    for row in data["unfilled"]:
        lines.append(f"unfilled: {row['time']} {row['plan'] or '(no plan)'}")
    return lines


def due_time(start: datetime, every: int, end: time) -> tuple[datetime, str]:
    """When the next check-in is due, and its reason ('due' or 'end')."""
    finish = datetime.combine(start.date(), end)
    due = start + timedelta(minutes=every)
    if finish <= due:
        return finish, "end"
    return due, "due"


def wait(start: datetime, every: int, end: time, now=datetime.now,
         sleep=_time.sleep) -> tuple[datetime, str]:
    """
    Sleep until the next check-in is due.

    Args:
        start: When the wait began.
        every: Minutes until a check-in is due.
        end: The end of the workday; a check-in is due then at the latest.
        now: Returns the current time; a parameter for tests.
        sleep: Sleeps for seconds; a parameter for tests.

    Returns:
        (the time it is due, 'due' or 'end'). Returns at once, with 'end',
        when start is at or after the end time.
    """
    due, reason = due_time(start, every, end)
    while True:
        remaining = (due - now()).total_seconds()
        if remaining <= 0:
            return due, reason
        sleep(min(TICK_SECONDS, remaining))


def _cell(text: str, width: int) -> str:
    padded = f" {text} "
    return padded.ljust(width)


def fill_actual(day: date, first: time, last: time, text: str,
                force: bool = False) -> dict:
    """
    Write text into the Actual cells of the rows from first through last.

    Args:
        day: The day of the daily note.
        first, last: The row times, inclusive.
        text: The Actual text; `|` becomes `/` and newlines spaces.
        force: Overwrite cells that aren't empty.

    Returns:
        Dict with `note`, `written` and `skipped` (lists of row labels).

    Raises:
        ValueError: If the note or a row is missing, or the text is empty.
            Nothing is written.
    """
    text = " ".join(text.replace("|", "/").split())
    if not text:
        raise ValueError("actual text is empty")
    if last < first:
        raise ValueError("--through is before the start time")
    path = note.periodic_note("daily", day)[0]
    lines = _read_lines(path)
    if lines is None:
        raise ValueError(f"no daily note: {path}")
    rows = time_block_rows(lines)
    col = layout(lines).actual if rows else 0
    if not any(r.time == first for r in rows):
        raise ValueError(f"no Time Block row at {first:%H:%M} in {path}")
    written, skipped = [], []
    for row in rows:
        if not first <= row.time <= last:
            continue
        if row.actual and not force:
            skipped.append(row.label)
            continue
        cells = lines[row.index].split("|")
        cells[col] = _cell(text, len(cells[col]))
        lines[row.index] = "|".join(cells)
        written.append(row.label)
    if written:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    return {"note": path, "written": written, "skipped": skipped}
