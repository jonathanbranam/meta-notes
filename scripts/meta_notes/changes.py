"""
Notes changed in a period, from the notes root's git history and working tree.

Committed changes count when their author date, in its own timezone, falls
in the period; uncommitted changes (staged, unstaged, untracked) count when
the period includes today. All of a note's changes fold into one entry under
its current path. Nothing here writes to the repository.
"""

import os
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import period

FOLDERS = ("plan", "project", "area", "resource", "archive")


def _git(root_dir: str, *args: str) -> str:
    """
    Run git in root_dir without taking optional locks.

    Returns:
        Its stdout.

    Raises:
        ValueError: If git is missing or exits non-zero.
    """
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "-C", root_dir, *args],
            stdin=subprocess.DEVNULL, capture_output=True, text=True,
            encoding="utf-8", errors="surrogateescape")
    except OSError as e:
        raise ValueError(f"Could not run git: {e.strerror or e}") from None
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()
        raise ValueError(f"git {args[0]} failed"
                         + (f": {detail[-1]}" if detail else ""))
    return result.stdout


def _check_top_level(root_dir: str) -> None:
    """Raise ValueError unless root_dir is the top level of a git work tree."""
    try:
        top = _git(root_dir, "rev-parse", "--show-toplevel").strip()
    except ValueError as e:
        if str(e).startswith("Could not run git"):
            raise
        raise ValueError(
            f"Notes root is not a git repository: {root_dir}") from None
    if os.path.realpath(top) != os.path.realpath(root_dir):
        raise ValueError("Notes root must be the top level of its git "
                         f"repository ({top}): {root_dir}")


@dataclass
class _Change:
    """One file's change in a commit or the working tree."""
    status: str
    path: str
    old_path: str | None = None
    added: int = 0
    removed: int = 0


def _parse_diff(tokens: list[str]) -> list[_Change]:
    """
    Parse NUL-separated `--raw --numstat -z` output into changes.

    Raw entries come first (":<modes> <hashes> <status>", then one path, or
    two for a rename or copy), then numstat entries ("<added>\\t<removed>\\t
    <path>", or with an empty path followed by old and new paths).
    """
    found: list[_Change] = []
    counts: dict[str, tuple[int, int]] = {}
    i = 0
    while i < len(tokens):
        token = tokens[i].lstrip("\n")
        i += 1
        if not token:
            continue
        if token.startswith(":"):
            status = token.split()[-1][0]
            if status in "RC":
                found.append(_Change(status, tokens[i + 1], tokens[i]))
                i += 2
            else:
                found.append(_Change(status, tokens[i]))
                i += 1
            continue
        added, removed, path = token.split("\t", 2)
        if not path:
            path = tokens[i + 1]
            i += 2
        # Binary files report "-"
        counts[path] = (int(added) if added.isdigit() else 0,
                        int(removed) if removed.isdigit() else 0)
    for change in found:
        change.added, change.removed = counts.get(change.path, (0, 0))
    return found


def _committed(root_dir: str, start: date, end: date) -> list[list[_Change]]:
    """Change sets of the commits authored in start..end, oldest first."""
    # --since compares committer dates, never earlier than author dates; the
    # UTC midnight a day early covers any author offset
    since = f"{start - timedelta(days=1)}T00:00:00+00:00"
    out = _git(root_dir, "log", "--reverse", "--no-merges", "-M", "-z",
               "--format=%x01%H%x00%aI", "--raw", "--numstat",
               f"--since={since}", "--", *FOLDERS)
    sets = []
    for chunk in out.split("\x01")[1:]:
        tokens = chunk.split("\0")
        day = datetime.fromisoformat(tokens[1]).date()
        if start <= day <= end:
            sets.append(_parse_diff(tokens[2:]))
    return sets


def _line_count(path: str) -> int:
    with open(path, "rb") as f:
        data = f.read()
    return data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)


def _has_head(root_dir: str) -> bool:
    """Whether the repository has any commits."""
    try:
        _git(root_dir, "rev-parse", "--verify", "-q", "HEAD")
    except ValueError:
        return False
    return True


def _uncommitted(root_dir: str, has_head: bool) -> list[_Change]:
    """Staged, unstaged, and untracked changes, as one change set."""
    # With no commits yet, compare with the empty tree
    base = ("HEAD" if has_head else
            _git(root_dir, "hash-object", "-t", "tree", os.devnull).strip())
    found = _parse_diff(_git(root_dir, "diff", base, "-M", "-z", "--raw",
                             "--numstat", "--", *FOLDERS).split("\0"))
    untracked = _git(root_dir, "ls-files", "--others", "--exclude-standard",
                     "-z", "--", *FOLDERS)
    for path in filter(None, untracked.split("\0")):
        if path.endswith(".md"):
            found.append(_Change(
                "A", path, added=_line_count(os.path.join(root_dir, path))))
    return found


@dataclass
class _Record:
    """A note's changes so far, under its current path."""
    start_path: str
    existed_at_start: bool
    deleted: bool = False
    added: int = 0
    removed: int = 0
    rename_only: bool = True


def _fold(change_sets: list[list[_Change]]) -> dict[str, _Record]:
    """Fold change sets, oldest first, into one record per current path."""
    records: dict[str, _Record] = {}
    for change_set in change_sets:
        for change in change_set:
            if change.status == "R":
                record = (records.pop(change.old_path, None)
                          or _Record(change.old_path, True))
                records[change.path] = record
                if change.added or change.removed:
                    record.rename_only = False
            elif change.status in "AC":
                record = records.get(change.path)
                if record is None or not record.deleted:
                    record = _Record(change.path, False)
                    records[change.path] = record
                record.deleted = False
                record.rename_only = False
            else:
                record = records.setdefault(change.path,
                                            _Record(change.path, True))
                record.deleted = change.status == "D"
                record.rename_only = False
            record.added += change.added
            record.removed += change.removed
    return records


def _is_note(path: str) -> bool:
    return path.endswith(".md") and path.split("/", 1)[0] in FOLDERS


def _entries(records: dict[str, _Record]) -> list[dict]:
    """Change entries for the records that are notes, sorted by path."""
    found = []
    for path, record in records.items():
        existed = record.existed_at_start and _is_note(record.start_path)
        if not _is_note(path):
            # A note renamed to a non-note is gone as a note
            if not existed:
                continue
            path, deleted = record.start_path, True
        else:
            deleted = record.deleted
        if deleted:
            kind = "deleted"
        elif not existed:
            kind = "added"
        elif record.start_path != path:
            kind = "renamed"
        else:
            kind = "modified"
        found.append({
            "path": path,
            "kind": kind,
            "old_path": record.start_path if kind == "renamed" else None,
            "added": record.added,
            "removed": record.removed,
            "rename_only": kind == "renamed" and record.rename_only,
        })
    return sorted(found, key=lambda e: e["path"])


def _format(entries: list[dict]) -> list[str]:
    """One text line per entry: kind letter, +added -removed, path."""
    added = max((len(str(e["added"])) for e in entries), default=1)
    removed = max((len(str(e["removed"])) for e in entries), default=1)
    lines = []
    for e in entries:
        line = (f"{e['kind'][0].upper()}  {'+' + str(e['added']):>{added + 1}}"
                f"  {'-' + str(e['removed']):>{removed + 1}}  {e['path']}")
        if e["old_path"]:
            line += f"  <- {e['old_path']}"
        if e["rename_only"]:
            line += "  (rename only)"
        lines.append(line)
    return lines


def run(root_dir: str, date_text: str | None = None,
        today: date | None = None) -> tuple[list[str], dict]:
    """
    List the notes changed in a period.

    Args:
        root_dir: Notes root, the top level of a git repository.
        date_text: A date-period value, or None for today.
        today: Reference date for the default and for whether uncommitted
            changes count (default: today).

    Returns:
        Tuple of (text lines, one per entry; data with start, end, and
        changes).

    Raises:
        ValueError: If date_text is invalid, git is missing or fails, or
            root_dir isn't the top level of a git repository.
    """
    today = today or date.today()
    start, end = period.parse_period(date_text, today)
    _check_top_level(root_dir)

    has_head = _has_head(root_dir)
    change_sets = _committed(root_dir, start, end) if has_head else []
    if start <= today <= end:
        change_sets.append(_uncommitted(root_dir, has_head))

    found = _entries(_fold(change_sets))
    return _format(found), {"start": start.isoformat(),
                            "end": end.isoformat(), "changes": found}
