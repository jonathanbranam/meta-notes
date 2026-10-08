"""
Time Log edits: append and replace entries under a daily note's `### Log`.

An entry is a `- ` header line plus every indented line under it. Edits
are guarded: the caller states the text it expects to find, and nothing is
written when the file differs, so a stale read can't clobber a change the
human made in Vim. Timestamps are parsed by `time_tracking`.
"""

import re
from dataclasses import dataclass, field
from datetime import date, datetime, time

import time_tracking

_START = re.compile(r"^\s+[*-]\s*start:(.*)$")
_END = re.compile(r"^\s+[*-]\s*end:(.*)$")


def _strip_tilde(time_str: str) -> str:
	"""Remove leading tilde from time string for comparison and parsing."""
	return time_str.lstrip('~')


class TimeLogError(ValueError):
    """An edit that wrote nothing. `current` lists entries to compare."""

    def __init__(self, message: str, current: list[dict] | None = None):
        super().__init__(message)
        self.current = current


@dataclass
class Entry:
    """A log entry: its first line index and its lines."""
    index: int
    lines: list[str]
    start: datetime | None = None
    end: datetime | None = None
    start_has_tilde: bool = False
    end_has_tilde: bool = False

    @property
    def header(self) -> str:
        return self.lines[0]

    def as_dict(self) -> dict:
        return {"line": self.index + 1, "text": "\n".join(self.lines)}


@dataclass
class Result:
    """What an edit wrote: the file's line numbers and any warnings."""
    written: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _parse_stamp(text: str, file_date: date | None) -> tuple[datetime | None, bool]:
	"""Parse a timestamp, optionally prefixed with ~. Returns (datetime, has_tilde)."""
	text = text.strip()
	has_tilde = text.startswith('~')
	clean_text = _strip_tilde(text)
	dt = time_tracking._parse_entry_time(clean_text, file_date)
	return dt, has_tilde


def parse_entries(lines: list[str], first: int, file_date: date | None,
                  strict: bool = False) -> list[Entry]:
    """
    Group lines into entries; `first` is the index of the first line.

    Args:
        lines: The lines of the log section (or of a `--text` argument).
        first: The file index of `lines[0]`.
        file_date: The note's date, to resolve bare times.
        strict: Raise TimeLogError for a line outside any entry or a blank
            line, instead of skipping blank lines between entries.
    """
    entries: list[Entry] = []
    for offset, line in enumerate(lines):
        if line.startswith("- ") or line.rstrip() == "-":
            entries.append(Entry(first + offset, [line]))
        elif entries and line[:1] in (" ", "\t") and line.strip():
            entries[-1].lines.append(line)
        elif strict:
            raise TimeLogError(
                f"line {offset + 1} is not part of an entry (a header is "
                f"'- text', its lines are indented): {line!r}")
    for entry in entries:
        for line in entry.lines[1:]:
            if (m := _START.match(line)) and entry.start is None:
                entry.start, entry.start_has_tilde = _parse_stamp(m.group(1), file_date)
            elif (m := _END.match(line)) and entry.end is None:
                entry.end, entry.end_has_tilde = _parse_stamp(m.group(1), file_date)
    return entries


def _file_date(path: str) -> date | None:
    return time_tracking._extract_date_from_filepath(path)


def _read(path: str) -> list[str]:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        raise TimeLogError(f"no such file: {path}")


def _write(path: str, lines: list[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _log_section(lines: list[str], path: str) -> tuple[int, int]:
    """The heading's index and the index just past the log section."""
    heading = next((i for i, line in enumerate(lines)
                    if line.strip() == "### Log"), None)
    if heading is None:
        raise TimeLogError(f"no '### Log' in {path}")
    end = next((i for i in range(heading + 1, len(lines))
                if lines[i].startswith("#")), len(lines))
    return heading, end


def _entry_end(entry: Entry) -> int:
    """The index just past an entry's last line."""
    return entry.index + len(entry.lines)


def _gap_warnings(entries: list[Entry]) -> list[str]:
    """Gap and overlap warnings between neighbouring entries."""
    out = []
    for prev, nxt in zip(entries, entries[1:]):
        if prev.end is None or nxt.start is None:
            continue
        minutes = time_tracking.duration_minutes(nxt.start - prev.end)
        name = nxt.header[2:].strip()
        if minutes > 0:
            out.append(f"*Gap of {minutes} min* before {name!r}")
        elif minutes < 0:
            out.append(f"*Overlap of {-minutes} min* before {name!r}")
    return out


def _check_new(entries: list[Entry], allow_open_last: bool) -> None:
    """Validate new entries; raise TimeLogError naming the first problem."""
    for i, entry in enumerate(entries):
        name = entry.header
        raw = {"start": None, "end": None}
        for line in entry.lines[1:]:
            for key, pattern in (("start", _START), ("end", _END)):
                if (m := pattern.match(line)) and raw[key] is None:
                    raw[key] = m.group(1).strip()
        if raw["start"] is None:
            raise TimeLogError(f"{name!r} has no 'start:' line")
        if entry.start is None:
            raise TimeLogError(
                f"{name!r} has an invalid start: {raw['start']!r}")
        if not raw["end"]:
            if i != len(entries) - 1 or not allow_open_last:
                raise TimeLogError(
                    f"{name!r} has no 'end:' line; only the log's last "
                    "entry may be open")
        elif entry.end is None:
            raise TimeLogError(
                f"{name!r} has an invalid end: {raw['end']!r}")
        elif entry.end < entry.start:
            raise TimeLogError(f"{name!r} ends before it starts")


def _stamp(at: time, has_tilde: bool = False) -> str:
	"""Format a time as HH:MM, optionally with a leading tilde."""
	formatted = f"{at:%H:%M}"
	return f"~{formatted}" if has_tilde else formatted


def append(path: str, text: str, start: time, end: time | None = None,
           notes: list[str] | None = None, prev: str | None = None,
           prev_start: time | None = None, prev_open: bool = False,
           close_prev: bool = False, first: bool = False,
           start_tilde: bool = False, end_tilde: bool = False,
           prev_start_tilde: bool = False) -> Result:
    """
    Add one entry at the end of the log.

    Args:
        path: The note.
        text: The new entry's header line, `- text #tags`.
        start, end: The new entry's times (`end` None leaves it open).
        notes: Extra `* note` lines, in order.
        prev: The last entry's header line, which must match exactly.
        prev_start: The last entry's start time, which must match.
        prev_open: Assert the last entry has no end (else it must have one).
        close_prev: Write the last entry's end as `start` (needs prev_open).
        first: Assert the log is empty; replaces the prev options.
        start_tilde, end_tilde, prev_start_tilde: Whether to write times with ~ prefix.

    Raises:
        TimeLogError: With nothing written, if the guard fails (`current`
            then lists the last entry), the log or arguments are invalid.
    """
    if not text.startswith("- ") or "\n" in text:
        raise TimeLogError("--text must be one line starting with '- '")
    notes = notes or []
    if any("\n" in n for n in notes):
        raise TimeLogError("a --note must be one line")
    if end is not None and end < start:
        raise TimeLogError("--end is before --start")
    if close_prev and not prev_open:
        raise TimeLogError("--close-prev needs --prev-open")
    lines = _read(path)
    heading, stop = _log_section(lines, path)
    file_date = _file_date(path)
    entries = parse_entries(lines[heading + 1:stop], heading + 1, file_date)
    last = entries[-1] if entries else None

    if first:
        if last is not None:
            raise TimeLogError("--first: the log already has entries",
                               [last.as_dict()])
        if prev or prev_start or prev_open or close_prev:
            raise TimeLogError("--first can't be used with the --prev "
                               "options")
    else:
        if prev is None or prev_start is None:
            raise TimeLogError("give --prev and --prev-start, or --first "
                               "for an empty log")
        if last is None:
            raise TimeLogError("the log has no entries; use --first")
        problems = []
        if last.header != prev:
            problems.append(f"last entry is {last.header!r}, not {prev!r}")
        if last.start is None or last.start.time() != prev_start:
            problems.append(f"last entry's start isn't {_stamp(prev_start)}")
        if prev_open and last.end is not None:
            problems.append("last entry already has an end")
        if not prev_open and last.end is None:
            problems.append("last entry has no end (use --prev-open)")
        if problems:
            raise TimeLogError("last entry doesn't match: "
                               + "; ".join(problems), [last.as_dict()])

    new_lines = [text, f"  * start: {_stamp(start, start_tilde)}"]
    if end is not None:
        new_lines.append(f"  * end:   {_stamp(end, end_tilde)}")
    new_lines += [f"  * {note}" for note in notes]

    result = Result()
    if close_prev:
        end_line = f"  * end:   {_stamp(start, start_tilde)}"
        for i in range(last.index + 1, _entry_end(last)):
            if _END.match(lines[i]):
                lines[i] = end_line
                break
        else:
            at = next(i for i in range(last.index + 1, _entry_end(last))
                      if _START.match(lines[i]))
            lines.insert(at + 1, end_line)
            last.lines.insert(at + 1 - last.index, end_line)
        last.end = datetime.combine(last.start.date(), start)
    added = parse_entries(new_lines, 0, file_date)
    if last is not None and last.end is not None and not close_prev:
        result.warnings = _gap_warnings([last, added[0]])

    if last is not None:
        pos = _entry_end(last)
    else:
        pos = heading + 1
        if pos < len(lines) and not lines[pos].strip():
            pos += 1
        else:
            new_lines.insert(0, "")
        if pos < len(lines) and lines[pos].strip():
            new_lines.append("")
    lines[pos:pos] = new_lines
    _write(path, lines)
    at = pos + (1 if new_lines[0] == "" else 0)
    result.written = [{"line": at + 1, "text": "\n".join(
        l for l in new_lines if l)}]
    return result


def update(path: str, expect: str, text: str) -> Result:
    """
    Replace a contiguous run of whole entries with zero or more entries.

    Args:
        path: The note.
        expect: The exact text of the entries to replace.
        text: The replacement entries; empty deletes the matched ones.

    Raises:
        TimeLogError: With nothing written, if `expect` isn't whole
            entries or matches zero or several runs (`current` lists the
            likely entries), or `text` isn't valid entries.
    """
    lines = _read(path)
    heading, stop = _log_section(lines, path)
    file_date = _file_date(path)
    entries = parse_entries(lines[heading + 1:stop], heading + 1, file_date)

    want_lines = expect.rstrip("\n").split("\n")
    wanted = parse_entries(want_lines, 0, file_date, strict=True)
    if not wanted:
        raise TimeLogError("--expect must hold at least one whole entry, "
                           "starting at a '- ' header line")
    n = len(wanted)
    matches = [i for i in range(len(entries) - n + 1)
               if [l for e in entries[i:i + n] for l in e.lines] == want_lines]
    if not matches:
        headers = {e.header for e in wanted}
        starts = {e.start for e in wanted if e.start}
        likely = [e for e in entries
                  if e.header in headers or (e.start and e.start in starts)]
        shown = [{"line": e.index + 1, "text": "\n".join(
            l if l in want_lines else f"~ {l}" for l in e.lines)}
            for e in likely]
        detail = "\n".join(f"line {s['line']}:\n{s['text']}" for s in shown)
        raise TimeLogError(
            "--expect matches no entries in the log"
            + (f"; likely (~ marks lines that differ):\n{detail}"
               if shown else ""), shown)
    if len(matches) > 1:
        raise TimeLogError(
            f"--expect matches {len(matches)} places (lines "
            + ", ".join(str(entries[i].index + 1) for i in matches)
            + "); include more lines")

    at = matches[0]
    run = entries[at:at + n]
    new_text = text.rstrip("\n")
    new_lines = new_text.split("\n") if new_text.strip() else []
    new = parse_entries(new_lines, 0, file_date, strict=True)
    _check_new(new, allow_open_last=at + n == len(entries))

    result = Result()
    result.warnings = _gap_warnings(
        entries[max(at - 1, 0):at] + new + entries[at + n:at + n + 1])
    lines[run[0].index:_entry_end(run[-1])] = new_lines
    _write(path, lines)
    if new:
        result.written = [
            {"line": run[0].index + 1 + sum(len(e.lines) for e in new[:i]),
             "text": "\n".join(new[i].lines)}
            for i in range(len(new))
        ]
    else:
        result.written = []
    return result
