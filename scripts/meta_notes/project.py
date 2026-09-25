"""
Projects, their home notes, and the `key: value` field list in a home note.

A project is a note or folder directly in `project/` (or `archive/project/`).
Its fields are the `- key: value` items of the first list after the home
note's title. See "Project model" in docs/planning-system.md.
"""

import os
import re

PROJECT_FOLDERS = ("project", "archive/project")
HOME_NOTE = "Home.md"

_HEADING = re.compile(rb"^#{1,6}(\s|$)")
_LIST_ITEM = re.compile(rb"^[-*+]\s")
_FIELD = re.compile(rb"^[-*+] ([A-Za-z0-9_-]+):[ \t]*(.*?)[ \t]*$")
_CHECKBOX = re.compile(rb"^[-*+] \[.\]")


def project_for(path: str, root_dir: str = ".") -> str | None:
    """
    The project a path names, or None if it isn't one.

    Args:
        path: A note (with or without `.md`) or folder path, relative to the
            notes root.
        root_dir: Notes root.

    Returns:
        The project path (`project/foo.md` or `project/foo`), or None for
        anything not directly in a project folder.
    """
    path = path.rstrip("/")
    parent, name = os.path.split(path)
    if parent not in PROJECT_FOLDERS or not name:
        return None
    if os.path.isdir(os.path.join(root_dir, path)):
        return path
    if not path.endswith(".md"):
        path += ".md"
    return path if os.path.isfile(os.path.join(root_dir, path)) else None


def home_note(project: str) -> str | None:
    """The home note of a project: the note itself, or its folder's Home.md."""
    if os.path.isdir(project):
        home = os.path.join(project, HOME_NOTE)
        return home if os.path.isfile(home) else None
    return project if os.path.isfile(project) else None


def _body(line: bytes) -> bytes:
    return line.rstrip(b"\r\n")


def _is_field(line: bytes) -> bool:
    body = _body(line)
    return bool(_FIELD.match(body)) and not _CHECKBOX.match(body)


def _find_title(lines: list[bytes]) -> int | None:
    for i, line in enumerate(lines):
        if _HEADING.match(_body(line)):
            return i
    return None


def _find_field_list(lines: list[bytes], title: int | None) -> tuple[int, int] | None:
    """
    Line span [start, end) of the field list, or None.

    The field list is the first list after the title (or at the top of a
    note with no title), before any other heading, with a field item.
    """
    i = 0 if title is None else title + 1
    while i < len(lines):
        body = _body(lines[i])
        if _HEADING.match(body):
            return None
        if _LIST_ITEM.match(body):
            start = i
            while i < len(lines) and _LIST_ITEM.match(_body(lines[i])):
                i += 1
            if any(_is_field(line) for line in lines[start:i]):
                return start, i
            return None
        if title is None and body.strip():
            # With no title, only a list at the top of the note counts
            return None
        i += 1
    return None


def _split(content: bytes) -> list[bytes]:
    return content.splitlines(keepends=True)


def parse_fields(content: bytes) -> dict[str, str]:
    """Fields of a home note's content, with lowercase keys (first wins)."""
    lines = _split(content)
    span = _find_field_list(lines, _find_title(lines))
    fields: dict[str, str] = {}
    if span is None:
        return fields
    for line in lines[span[0]:span[1]]:
        if not _is_field(line):
            continue
        m = _FIELD.match(_body(line))
        key = m.group(1).decode("utf-8").lower()
        fields.setdefault(key, m.group(2).decode("utf-8"))
    return fields


def read_fields(path: str) -> dict[str, str]:
    """
    Read a home note's fields.

    Args:
        path: Home note path.

    Returns:
        The fields with lowercase keys; empty if the note has no field list.
    """
    with open(path, "rb") as f:
        return parse_fields(f.read())


def _field_line(key: str, value: str, eol: bytes) -> bytes:
    return f"- {key.lower()}: {value}".encode("utf-8") + eol


def apply_fields(content: bytes, fields: dict[str, str]) -> bytes:
    """
    Set fields in a home note's content and return the new content.

    An existing item keeps its position; later items with the same key are
    dropped; missing keys are appended to the list. With no field list, a
    new one goes after the title (or at the top of the note).
    """
    lines = _split(content)
    first = lines[0] if lines else b""
    eol = b"\r\n" if first.endswith(b"\r\n") else b"\n"
    title = _find_title(lines)
    span = _find_field_list(lines, title)
    wanted = {k.lower(): v for k, v in fields.items()}

    if span is None:
        new = [_field_line(k, v, eol) for k, v in wanted.items()]
        if title is None:
            rest = lines
            if rest and _body(rest[0]).strip():
                new.append(eol)
            return b"".join(new + rest)

        before = lines[:title + 1]
        if not before[-1].endswith(b"\n"):
            before[-1] += eol
        after = lines[title + 1:]
        # Replace blank lines between the title and the next content with
        # exactly one on each side of the new list.
        while after and not _body(after[0]).strip():
            after.pop(0)
        block = [eol] + new
        if after:
            block.append(eol)
        return b"".join(before + block + after)

    start, end = span
    seen: set[str] = set()
    items: list[bytes] = []
    for line in lines[start:end]:
        if _is_field(line):
            key = _FIELD.match(_body(line)).group(1).decode("utf-8").lower()
            if key in wanted:
                if key in seen:
                    continue
                seen.add(key)
                line_eol = line[len(_body(line)):] or eol
                line = _field_line(key, wanted[key], line_eol)
        items.append(line)
    if items and not items[-1].endswith(b"\n"):
        items[-1] += eol
    items.extend(_field_line(k, v, eol) for k, v in wanted.items() if k not in seen)
    if end == len(lines) and not content.endswith(b"\n"):
        # Keep a note without a trailing newline without one
        items[-1] = _body(items[-1])
    return b"".join(lines[:start] + items + lines[end:])


def set_fields(path: str, fields: dict[str, str]) -> None:
    """
    Set fields in a home note on disk.

    Args:
        path: Home note path.
        fields: Keys and values to set.

    Raises:
        OSError: If the note can't be read or written.
    """
    with open(path, "rb") as f:
        content = f.read()
    new = apply_fields(content, fields)
    if new != content:
        with open(path, "wb") as f:
            f.write(new)
