"""
Time Block edits: write Plan and Actual cells of a note's Time Block.

Rows are found by time, cells are padded to their column's width, and a
non-empty cell is only overwritten when the caller expects its text, so a
stale read can't clobber an edit. Parsing is shared with `checkin`.
"""

from dataclasses import dataclass, field
from datetime import time

from meta_notes import checkin

COLUMNS = {"plan": 2, "actual": 3}


class TimeBlockError(ValueError):
    """An update that wrote nothing. `current` lists mismatched cells."""

    def __init__(self, message: str, current: list[dict] | None = None):
        super().__init__(message)
        self.current = current


@dataclass
class UpdateResult:
    """What an update wrote: the rows' labels, and which were created."""
    written: list[str] = field(default_factory=list)
    created: list[str] = field(default_factory=list)


def _clean(text: str) -> str:
    return " ".join(text.replace("|", "/").split())


def format_label(at: time, inner: int) -> str:
    """A row label like ` 7:00am`, right-aligned in `inner` characters."""
    hour = at.hour % 12 or 12
    label = f"{hour}:{at.minute:02d}{'pm' if at.hour >= 12 else 'am'}"
    return label.rjust(inner)


def _ragged(lines: list[str], rows: list[checkin.Row],
            columns: list[int]) -> str | None:
    """A message naming rows whose cell width differs, or None."""
    for col in columns:
        widths = {r.index: len(lines[r.index].split("|")[col]) for r in rows}
        if len(set(widths.values())) > 1:
            common = max(set(widths.values()),
                         key=list(widths.values()).count)
            odd = [f"{r.label} (line {r.index + 1}, width {widths[r.index]})"
                   for r in rows if widths[r.index] != common]
            name = "plan" if col == 2 else "actual"
            return (f"ragged Time Block: the {name} cells differ in width "
                    f"(most are {common}): {', '.join(odd)}")
    return None


def _created_row(lines: list[str], rows: list[checkin.Row],
                 at: time) -> tuple[int, str]:
    """The line index and text of a new blank row for `at`."""
    after = [r for r in rows if r.time > at]
    index = after[0].index if after else rows[-1].index + 1
    cells = lines[rows[0].index].split("|")
    blank = ["", f" {format_label(at, len(cells[1]) - 2)} "]
    blank += [" " * len(c) for c in cells[2:-1]] + [cells[-1]]
    return index, "|".join(blank)


def update(path: str, first: time, last: time, plan: str | None = None,
           actual: str | None = None, expect: str | None = None,
           create: bool = False) -> UpdateResult:
    """
    Write Plan and/or Actual cells of the Time Block rows first..last.

    Args:
        path: The note.
        first, last: The row times, inclusive.
        plan, actual: New cell text (None leaves the column alone); `|`
            becomes `/` and newlines spaces.
        expect: The text every target cell must currently hold (compared
            stripped). None means empty.
        create: Add the row at `first` when missing; only without a range.

    Raises:
        TimeBlockError: With nothing written, if there is no Time Block,
            a row is missing, the table is ragged, text is wider than its
            column, or a cell doesn't match `expect` (`current` then lists
            each, with `time`, `column` and `text`).
    """
    new = {name: _clean(text) for name, text in
           (("plan", plan), ("actual", actual)) if text is not None}
    if not new:
        raise TimeBlockError("give --plan or --actual")
    if last < first:
        raise TimeBlockError("--through is before --time")
    if create and last != first:
        raise TimeBlockError("--create can't be used with --through")
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        raise TimeBlockError(f"no such file: {path}")
    rows = checkin.time_block_rows(lines)
    if not rows:
        raise TimeBlockError(f"no Time Block in {path}")
    ragged = _ragged(lines, rows, [COLUMNS[n] for n in new])
    if ragged:
        raise TimeBlockError(ragged)

    created = []
    if create and not any(r.time == first for r in rows):
        index, line = _created_row(lines, rows, first)
        lines.insert(index, line)
        rows = checkin.time_block_rows(lines)
        created = [r.label for r in rows if r.time == first]
    for at in (first, last):
        if not any(r.time == at for r in rows):
            raise TimeBlockError(f"time slot not found: {at:%H:%M} in {path}")
    targets = [r for r in rows if first <= r.time <= last]

    wanted = (expect or "").strip()
    mismatches = []
    for row in targets:
        cells = lines[row.index].split("|")
        for name in new:
            current = cells[COLUMNS[name]].strip()
            if current != wanted:
                mismatches.append({"time": row.label, "column": name,
                                   "text": current})
    if mismatches:
        detail = "; ".join(f"{m['time']} {m['column']}: {m['text']!r}"
                           for m in mismatches)
        raise TimeBlockError(
            f"cells don't match --expect {wanted!r}: {detail}", mismatches)

    for row in targets:
        cells = lines[row.index].split("|")
        for name, text in new.items():
            width = len(cells[COLUMNS[name]])
            if len(text) + 2 > width:
                raise TimeBlockError(
                    f"text is too wide for the {name} column: {len(text)} "
                    f"characters, the column holds {width - 2}")
    for row in targets:
        cells = lines[row.index].split("|")
        for name, text in new.items():
            col = COLUMNS[name]
            cells[col] = checkin._cell(text, len(cells[col]))
        lines[row.index] = "|".join(cells)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return UpdateResult([r.label for r in targets], created)
