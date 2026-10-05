"""
Note write: replace a range of a note's lines, or the whole file, with an
--expect guard and one write.

The caller states the lines it read; nothing is written when the file holds
anything else, so a stale read can't clobber a change made in Vim. Line
endings and the file's trailing newline are kept as they are.
"""

import os
import re
from dataclasses import dataclass

_LINE = re.compile(r"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+")
_ENDING = re.compile(r"(\r\n|\r|\n)$")


class NoteWriteError(ValueError):
    """A write that wrote nothing. `current` lists the lines found, if any."""

    def __init__(self, message: str, current: list[str] | None = None):
        super().__init__(message)
        self.current = current


@dataclass
class WriteResult:
    """The lines now at the edit (1-based, inclusive; end = line - 1 if none)."""
    line: int
    end_line: int
    changed: bool


def _block(text: str) -> list[str]:
    """The lines of a --text or --expect value; '' is none."""
    return [] if text == "" else text.removesuffix("\n").split("\n")


def _check_path(path: str) -> None:
    normal = os.path.normpath(path) if path else ""
    if (normal in ("", ".") or os.path.isabs(normal) or normal == ".."
            or normal.startswith("../")):
        raise NoteWriteError(f"Path is outside the notes root: {path!r}")
    if (os.path.exists(path) and not os.path.realpath(path).startswith(
            os.path.realpath(".") + os.sep)):
        raise NoteWriteError(f"Path is outside the notes root: {path!r}")


def write(path: str, expect: str, text: str, first: int | None = None,
          last: int | None = None, create: bool = False) -> WriteResult:
    """
    Replace lines first..last of `path` (relative to the cwd, the notes
    root) with `text`, only if they are exactly `expect`.

    Args:
        first, last: 1-based inclusive range; None for both is the whole file.
        create: Make a missing file (and its folders); needs expect ''.

    Raises:
        NoteWriteError: On a bad path or range, a missing file, or lines
            that differ from expect (current holds the lines found).
    """
    _check_path(path)
    try:
        with open(path, encoding="utf-8", newline="") as f:
            lines = _LINE.findall(f.read())
        exists = True
    except FileNotFoundError:
        lines, exists = [], False
    except (OSError, UnicodeDecodeError) as e:
        raise NoteWriteError(f"Could not read {path}: {e}")
    if not exists and not create:
        raise NoteWriteError(f"No such file: {path} (--create makes it)")

    if first is None:
        first, last = 1, len(lines)
    if first < 1 or last < first - 1:
        raise NoteWriteError(f"Invalid line range {first}..{last}")
    old = lines[first - 1:last]
    content = [_ENDING.sub("", line) for line in old]
    if "\n".join(content) != "\n".join(_block(expect)) or last > len(lines):
        raise NoteWriteError(
            f"{path} lines {first}..{last} are not what was expected",
            current=content)

    ending = next((m.group(1) for m in map(_ENDING.search, lines) if m), "\n")
    new = _block(text)
    # Every new line ends with a newline, except the last of a file that
    # had none, or of a new file whose text had none
    out = [line + ending for line in new]
    unterminated = (not exists and not text.endswith("\n")) or (
        exists and last == len(lines) and bool(old)
        and not _ENDING.search(old[-1]))
    if out and unterminated:
        out[-1] = new[-1]
    result = WriteResult(first, first + len(new) - 1, old != out)
    if exists and not result.changed:
        return result
    lines[first - 1:last] = out
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("".join(lines))
    return result
