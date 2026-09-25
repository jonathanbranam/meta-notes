"""
Task update: edit one checkbox line's status, tags, and dates in place.

The line is edited as marker tokens (date markers and tags), never
re-rendered from a parsed Task, so everything the edit doesn't touch keeps
the user's order and spacing. Only the target line of the file changes.
"""

import re
from dataclasses import dataclass, field
from datetime import date

import tasks
from tags import TAG_PATTERN, canonical_tag

START_EMOJI = '🛫'
COMPLETED_EMOJI = '✅'
NEW_DUE_EMOJI = '📅'
DONE_CHARS = ('x', 'X')

_DATE = r'\d{4}-\d{2}-\d{2}'

# Every emoji that starts a date marker; an added tag goes before the first
_DATE_EMOJI_PATTERN = re.compile(
    '|'.join((START_EMOJI, *tasks.DUE_EMOJIS, COMPLETED_EMOJI)))

# A line ending, as Python's universal newlines reads it
_LINE_PATTERN = re.compile(r'[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+\Z')


def _marker_pattern(*emojis: str) -> re.Pattern:
    """
    A date marker: one of emojis, an optional emoji variation selector, and
    an optional date. The date is matched by shape, so an invalid date after
    the emoji is part of the marker.
    """
    return re.compile(
        '(?P<emoji>(?:' + '|'.join(emojis) + r')️?)'
        rf'(?:(?P<sep>\s*)(?P<date>{_DATE}))?')


_DUE_MARKER = _marker_pattern(*tasks.DUE_EMOJIS)
_START_MARKER = _marker_pattern(START_EMOJI)
_COMPLETED_MARKER = _marker_pattern(COMPLETED_EMOJI)


class TaskUpdateError(Exception):
    """An update failed; nothing was written.

    Attributes:
        current: The line's current text when it didn't match --expect.
    """

    def __init__(self, message: str, current: str | None = None):
        super().__init__(message)
        self.current = current


@dataclass
class UpdateResult:
    """Outcome of an update: the line before and after, and any warnings."""
    old: str
    new: str
    changed: bool
    warnings: list[str] = field(default_factory=list)


# Marker token helpers

def _remove_span(text: str, start: int, end: int) -> str:
    """
    Remove text[start:end] and the whitespace that separated it.

    Takes the whitespace before the span, or the whitespace after it when
    the span directly follows the checkbox. A span at the end of the line
    takes any trailing whitespace too.
    """
    checkbox_end = tasks.CHECKBOX_PATTERN.match(text).end()
    ws_start = start
    while ws_start > 0 and text[ws_start - 1] in ' \t':
        ws_start -= 1
    ws_end = end
    while ws_end < len(text) and text[ws_end] in ' \t':
        ws_end += 1

    if ws_end == len(text):
        return text[:ws_start]
    if ws_start == checkbox_end:
        return text[:start] + text[ws_end:]
    return text[:ws_start] + text[end:]


def _insert(text: str, pos: int, token: str) -> str:
    """Insert token at pos, separated from its neighbors by single spaces."""
    before, after = text[:pos], text[pos:]
    if not after.strip():
        return before.rstrip() + ' ' + token
    if before and not before[-1].isspace():
        token = ' ' + token
    if not after[0].isspace():
        token = token + ' '
    return before + token + after


def _remove_markers(text: str, pattern: re.Pattern) -> str:
    """Remove every marker that pattern matches."""
    while match := pattern.search(text):
        text = _remove_span(text, match.start(), match.end())
    return text


def _set_marker_date(text: str, match: re.Match, value: str | None) -> str:
    """Set the date of an existing marker, or remove its date when value is None."""
    if value is None:
        return text[:match.end('emoji')] + text[match.end():]
    if match.group('date') is not None:
        return text[:match.start('date')] + value + text[match.end('date'):]
    return text[:match.end('emoji')] + ' ' + value + text[match.end('emoji'):]


# Edits, applied in order: remove tags, due, start, status and ✅, add tags

def _tag_positions(text: str, name: str) -> list[re.Match]:
    """Tags on the line that match name, ignoring case and applying aliases."""
    target = canonical_tag(name).lower()
    return [m for m in TAG_PATTERN.finditer(text)
            if canonical_tag(m.group(1)).lower() == target]


def _remove_tag(text: str, name: str) -> str:
    while found := _tag_positions(text, name):
        text = _remove_span(text, found[0].start(), found[0].end())
    return text


def _add_tag(text: str, name: str) -> str:
    bare = name.removeprefix('#')
    if _tag_positions(text, bare):
        return text
    first_date = _DATE_EMOJI_PATTERN.search(text)
    pos = first_date.start() if first_date else len(text)
    return _insert(text, pos, '#' + bare)


def _set_due(text: str, value: str) -> str:
    if value == 'none':
        return _remove_markers(text, _DUE_MARKER)
    new_date = None if value == 'undated' else value
    match = _DUE_MARKER.search(text)
    if match:
        return _set_marker_date(text, match, new_date)

    token = NEW_DUE_EMOJI if new_date is None else f'{NEW_DUE_EMOJI} {new_date}'
    start = _START_MARKER.search(text)
    completed = _COMPLETED_MARKER.search(text)
    if start:
        return _insert(text, start.end(), token)
    if completed:
        return _insert(text, completed.start(), token)
    return _insert(text, len(text), token)


def _set_start(text: str, value: str) -> str:
    if value == 'none':
        return _remove_markers(text, _START_MARKER)
    match = _START_MARKER.search(text)
    if match:
        return _set_marker_date(text, match, value)

    token = f'{START_EMOJI} {value}'
    later = [m.start() for m in (_DUE_MARKER.search(text),
                                 _COMPLETED_MARKER.search(text)) if m]
    return _insert(text, min(later) if later else len(text), token)


def _set_status(text: str, status: str, no_completed: bool, today: date) -> str:
    checkbox = tasks.CHECKBOX_PATTERN.match(text)
    was_done = checkbox.group(1) in DONE_CHARS
    text = text[:checkbox.start(1)] + status + text[checkbox.end(1):]

    if status not in DONE_CHARS:
        return _remove_markers(text, _COMPLETED_MARKER)
    if was_done or no_completed or _COMPLETED_MARKER.search(text):
        return text
    _, due_date, _ = tasks._parse_task_dates(text)
    if due_date == today:
        return text
    return _insert(text, len(text), f'{COMPLETED_EMOJI} {today.isoformat()}')


def edit_line(text: str, *, status: str | None = None,
              add_tags: list[str] | None = None,
              remove_tags: list[str] | None = None,
              due: str | None = None, start: str | None = None,
              no_completed: bool = False,
              today: date | None = None) -> str:
    """
    Apply edits to a checkbox line.

    Args:
        text: The line, without its line ending. Must be a checkbox line.
        status: New status character.
        add_tags, remove_tags: Tag names, with or without #.
        due: YYYY-MM-DD, 'undated', or 'none'.
        start: YYYY-MM-DD or 'none'.
        no_completed: Don't add a ✅ date when marking the task done.
        today: The ✅ date and the date compared with the due date
            (default: today).

    Returns:
        The edited line.
    """
    today = today or date.today()
    for name in remove_tags or []:
        text = _remove_tag(text, name)
    if due is not None:
        text = _set_due(text, due)
    if start is not None:
        text = _set_start(text, start)
    if status is not None:
        text = _set_status(text, status, no_completed, today)
    for name in add_tags or []:
        text = _add_tag(text, name)
    return text


def _split_ending(line: str) -> tuple[str, str]:
    """Split a line into its content and its line ending."""
    content = line.rstrip('\r\n')
    return content, line[len(content):]


def update(path: str, line_no: int, expect: str, *,
           status: str | None = None, add_tags: list[str] | None = None,
           remove_tags: list[str] | None = None, due: str | None = None,
           start: str | None = None, no_completed: bool = False,
           today: date | None = None) -> UpdateResult:
    """
    Edit one checkbox line of a file in place.

    Args:
        path: The file.
        line_no: The line, counting from 1.
        expect: The line's text as last read; compared ignoring trailing
            whitespace.
        status, add_tags, remove_tags, due, start, no_completed, today:
            See edit_line.

    Returns:
        The line before and after. The file is written only if it changed.

    Raises:
        TaskUpdateError: If the file can't be read, the line is out of
            range, doesn't match expect (the error's current is the line),
            or isn't a checkbox line.
    """
    try:
        with open(path, encoding='utf-8', newline='') as f:
            content = f.read()
    except FileNotFoundError:
        raise TaskUpdateError(f"No such file: {path}")
    except (OSError, UnicodeDecodeError) as e:
        raise TaskUpdateError(f"Could not read {path}: {e}")

    lines = _LINE_PATTERN.findall(content)
    if not 1 <= line_no <= len(lines):
        raise TaskUpdateError(
            f"Line {line_no} is out of range: {path} has {len(lines)} lines")

    old, ending = _split_ending(lines[line_no - 1])
    if old.rstrip() != expect.rstrip():
        raise TaskUpdateError(
            f"Line {line_no} of {path} has changed; it is now: {old.rstrip()}",
            current=old.rstrip())
    if not tasks.CHECKBOX_PATTERN.match(old):
        raise TaskUpdateError(f"Line {line_no} of {path} is not a checkbox")

    new = edit_line(old, status=status, add_tags=add_tags,
                    remove_tags=remove_tags, due=due, start=start,
                    no_completed=no_completed, today=today)
    result = UpdateResult(old=old, new=new, changed=new != old)
    if tasks.is_task(old) and not tasks.is_task(new):
        result.warnings.append(
            f"Line {line_no} of {path} is no longer a task "
            "(it has no due emoji or 🛫 date)")

    if result.changed:
        lines[line_no - 1] = new + ending
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(''.join(lines))
    return result
