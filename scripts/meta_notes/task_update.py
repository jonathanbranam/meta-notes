"""
Task update: edit one checkbox line's status, tags, and dates in place.

The line is edited as marker tokens (date markers and tags), never
re-rendered from a parsed Task, so everything the edit doesn't touch keeps
the user's order and spacing. Only the target line of the file changes.

The time of day is read from `⏰ HH:MM` (or 12-hour, `⏰ 3:15pm`) and from
a time after the due date (`📅 2026-10-01 15:00`); `time` writes `⏰ HH:MM`.
"""

import re
from dataclasses import dataclass, field
from datetime import date, timedelta

import tasks
from recurrence import Rule, next_date, parse_rule
from tags import TAG_PATTERN, canonical_tag

START_EMOJI = '🛫'
COMPLETED_EMOJI = '✅'
NEW_DUE_EMOJI = '📅'
RECUR_EMOJI = '🔁'
DONE_CHARS = ('x', 'X')
TIME_EMOJI = tasks.TIME_EMOJI

_DATE = r'\d{4}-\d{2}-\d{2}'

# Every emoji that starts a date marker; an added tag goes before the first
_DATE_EMOJI_PATTERN = re.compile(
    '|'.join((START_EMOJI, *tasks.DUE_EMOJIS, COMPLETED_EMOJI, TIME_EMOJI,
     RECUR_EMOJI)))

# A line ending, as Python's universal newlines reads it
_LINE_PATTERN = re.compile(r'[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+\Z')


def _marker_pattern(*emojis: str, time: bool = False) -> re.Pattern:
    """
    A date marker: one of emojis, an optional emoji variation selector, and
    an optional date. The date is matched by shape, so an invalid date after
    the emoji is part of the marker. With time, a 24-hour time after the
    date is part of the marker too.
    """
    clock = r'(?P<clock>[ \t]+\d{1,2}:\d{2}(?![\d:]))?' if time else ''
    return re.compile(
        '(?P<emoji>(?:' + '|'.join(emojis) + r')️?)'
        rf'(?:(?P<sep>\s*)(?P<date>{_DATE}){clock})?')


_DUE_MARKER = _marker_pattern(*tasks.DUE_EMOJIS, time=True)
# ⏰ and its time, in 24-hour or 12-hour form
_TIME_MARKER = re.compile(
    TIME_EMOJI + r'\ufe0f?(?:[ \t]*\d{1,2}:\d{2}(?:[ \t]*[AaPp][Mm])?)?')
_START_MARKER = _marker_pattern(START_EMOJI)
_COMPLETED_MARKER = _marker_pattern(COMPLETED_EMOJI)
# 🔁 and its rule text, which runs to the next date marker or tag
_RECUR_MARKER = tasks._RECURRENCE_MARKER_PATTERN


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
    """
    Outcome of an update: the line before and after, and any warnings.

    created is the next occurrence's text when completing a recurring task
    inserted one, and created_line its line number. It sits directly above
    the target, which has moved down one line.
    """
    old: str
    new: str
    changed: bool
    warnings: list[str] = field(default_factory=list)
    created: str | None = None
    created_line: int | None = None


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


def _set_time(text: str, value: str) -> str:
    """Set the time to ⏰ HH:MM, or remove every time with 'none'."""
    for match in _DUE_MARKER.finditer(text):
        if match.group('clock'):
            text = text[:match.start('clock')] + text[match.end('clock'):]
            break
    if value == 'none':
        return _remove_markers(text, _TIME_MARKER)

    token = f'{TIME_EMOJI} {value}'
    match = _TIME_MARKER.search(text)
    if match:
        return text[:match.start()] + token + text[match.end():]
    first_date = _DATE_EMOJI_PATTERN.search(text)
    return _insert(text, first_date.start() if first_date else len(text), token)


def _set_recur(text: str, value: str) -> str:
    """Set the 🔁 rule, or remove the marker and its rule with 'none'."""
    if value == 'none':
        while match := _RECUR_MARKER.search(text):
            text = _remove_span(text, match.start(), match.end())
        return text

    token = f'{RECUR_EMOJI} {value}'
    match = _RECUR_MARKER.search(text)
    if match:
        return text[:match.start()] + token + text[match.end():]
    first_date = _DATE_EMOJI_PATTERN.search(text)
    return _insert(text, first_date.start() if first_date else len(text), token)


def _recurrence(text: str) -> tuple[Rule | None, bool]:
    """
    The line's rule, and whether the rule has a date to step from.

    The rule is None when there is no 🔁 or its rule isn't supported. A rule
    steps from the due date, else the start date, or from the completion
    date when it is "when done".
    """
    match = _RECUR_MARKER.search(text)
    rule = parse_rule(match.group(1)) if match else None
    if rule is None:
        return None, False
    start_date, due_date, _ = tasks._parse_task_dates(text)
    return rule, (rule.when_done or due_date is not None
                  or start_date is not None)


def _is_recurring(text: str) -> bool:
    rule, has_base = _recurrence(text)
    return rule is not None and has_base


def _set_status(text: str, status: str, no_completed: bool, today: date) -> str:
    checkbox = tasks.CHECKBOX_PATTERN.match(text)
    was_done = checkbox.group(1) in DONE_CHARS
    completing = status in DONE_CHARS and not was_done
    recurring = completing and _is_recurring(text)
    if recurring and no_completed:
        raise TaskUpdateError(
            "--no-completed can't be used on a recurring task: "
            "its ✅ date records the completion")
    text = text[:checkbox.start(1)] + status + text[checkbox.end(1):]

    if status not in DONE_CHARS:
        return _remove_markers(text, _COMPLETED_MARKER)
    if was_done or no_completed or _COMPLETED_MARKER.search(text):
        return text
    if recurring:
        return _insert(text, len(text), f'{COMPLETED_EMOJI} {today.isoformat()}')
    _, due_date, _ = tasks._parse_task_dates(text)
    if due_date == today:
        return text
    return _insert(text, len(text), f'{COMPLETED_EMOJI} {today.isoformat()}')


def edit_line(text: str, *, status: str | None = None,
              add_tags: list[str] | None = None,
              remove_tags: list[str] | None = None,
              due: str | None = None, start: str | None = None,
              time: str | None = None, recur: str | None = None,
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
        time: HH:MM (24-hour) or 'none'; written as ⏰ HH:MM.
        recur: A rule such as 'every 3 months' (written as 🔁 <rule>), or
            'none' to remove the marker and its rule.
        no_completed: Don't add a ✅ date when marking the task done. A
            recurring task always gets one, so this raises TaskUpdateError
            there.
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
    if time is not None:
        text = _set_time(text, time)
    if recur is not None:
        text = _set_recur(text, recur)
    if status is not None:
        text = _set_status(text, status, no_completed, today)
    for name in add_tags or []:
        text = _add_tag(text, name)
    return text


def _split_ending(line: str) -> tuple[str, str]:
    """Split a line into its content and its line ending."""
    content = line.rstrip('\r\n')
    return content, line[len(content):]


def next_occurrence(done: str, today: date) -> str | None:
    """
    The open line that follows a completed recurring task line.

    Args:
        done: The line as completed, without its line ending.
        today: The completion date, the base of a "when done" rule.

    Returns:
        The next occurrence: the same line, open, without ✅, its due date
        replaced by the next date and its start date moved by as many days,
        or None when the line isn't recurring. The time and rule are kept.
    """
    rule, has_base = _recurrence(done)
    if rule is None or not has_base:
        return None
    start_date, due_date, _ = tasks._parse_task_dates(done)
    if rule.when_done:
        base = today
    else:
        base = due_date or start_date
    following = next_date(rule, base)

    text = _set_status(done, ' ', False, today)
    if due_date is not None or start_date is None:
        text = _set_due(text, following.isoformat())
        if due_date is not None and start_date is not None:
            shifted = start_date + (following - due_date)
            text = _set_start(text, shifted.isoformat())
    else:
        text = _set_start(text, following.isoformat())
    return text


def update(path: str, line_no: int, expect: str, *,
           status: str | None = None, add_tags: list[str] | None = None,
           remove_tags: list[str] | None = None, due: str | None = None,
           start: str | None = None, time: str | None = None,
           recur: str | None = None, no_recur: bool = False,
           no_completed: bool = False,
           today: date | None = None) -> UpdateResult:
    """
    Edit one checkbox line of a file in place.

    Args:
        path: The file.
        line_no: The line, counting from 1.
        expect: The line's text as last read; compared ignoring trailing
            whitespace.
        status, add_tags, remove_tags, due, start, time, recur,
        no_completed, today: See edit_line.
        no_recur: Don't insert the next occurrence when a recurring task is
            marked done.

    Returns:
        The line before and after. The file is written only if it changed.
        Marking a recurring task done (not already done) also inserts its
        next occurrence as a new open line directly above it, in the same
        write; the target then sits one line lower. A done task set to done
        again inserts nothing.

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
                    remove_tags=remove_tags, due=due, start=start, time=time,
                    recur=recur, no_completed=no_completed, today=today)
    result = UpdateResult(old=old, new=new, changed=new != old)
    today = today or date.today()
    completed = (status in DONE_CHARS
                 and tasks.CHECKBOX_PATTERN.match(old).group(1)
                 not in DONE_CHARS)
    spawned = None
    if completed:
        if _is_recurring(new):
            if not no_recur:
                spawned = next_occurrence(new, today)
        else:
            rule, _ = _recurrence(new)
            if rule is not None:
                result.warnings.append(
                    f"Line {line_no} of {path} has a 🔁 rule but no due or "
                    "start date, so no next occurrence was made")
            elif _RECUR_MARKER.search(new):
                result.warnings.append(
                    f"Line {line_no} of {path} has a 🔁 rule that isn't "
                    "supported, so no next occurrence was made")
    if tasks.is_task(old) and not tasks.is_task(new):
        result.warnings.append(
            f"Line {line_no} of {path} is no longer a task "
            "(it has no due emoji or 🛫 date)")
    _, due_date, _ = tasks._parse_task_dates(new)
    due_time, _ = tasks.parse_due_time(new)
    if due_time is not None and due_date is None:
        result.warnings.append(
            f"Line {line_no} of {path} has a time but no due date, "
            "so the time is ignored")

    if spawned is not None:
        result.created = spawned
        result.created_line = line_no
        result.changed = True
        # The last line may lack a line ending; the line above it needs one
        above_ending = ending or next(
            (_split_ending(line)[1] for line in reversed(lines)
             if _split_ending(line)[1]), '\n')
        lines[line_no - 1:line_no] = [spawned + above_ending, new + ending]
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(''.join(lines))
    elif result.changed:
        lines[line_no - 1] = new + ending
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(''.join(lines))
    return result
