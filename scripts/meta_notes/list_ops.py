"""
List operations that reach outside the list note: items sourced from a task,
and the current list recorded in today's daily note.

An item added with a source holds the task's note link, line number and text
as read. Checking the item closes that task the way `task update --expect`
does, so the task must still read exactly as copied (found by its text when
its line moved); otherwise nothing is written and the item stays as it was.
The closed task line is kept on the item, so unchecking reopens only a task
the list closed.
"""

import os
import re
from datetime import date

import tasks
from meta_notes import list_note, note, task_update
from meta_notes.list_note import ListError, ListNote

CURRENT_RE = re.compile(r'^Current list: \[\[(.+?)\]\]\s*$')


def read_source(path: str, line_no: int) -> dict:
    """The source of an item: the task line at path:line_no, copied exactly."""
    try:
        with open(path, encoding='utf-8', newline='') as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        raise ListError(f'No such file: {path}')
    except (OSError, UnicodeDecodeError) as e:
        raise ListError(f'Could not read {path}: {e}')
    if not 1 <= line_no <= len(lines):
        raise ListError(f'Line {line_no} is out of range: {path} has '
                        f'{len(lines)} lines')
    text = lines[line_no - 1].rstrip()
    match = tasks.CHECKBOX_PATTERN.match(text)
    if not match:
        raise ListError(f'Line {line_no} of {path} is not a checkbox')
    if match.group(1) != ' ':
        raise ListError(f'Line {line_no} of {path} is not an open task')
    return {'file': path.removesuffix('.md'), 'line': line_no, 'text': text}


def _update_task(path: str, line_no: int, expect: str, status: str):
    """task update --expect: at the line, else at the one line of that text."""
    try:
        try:
            return line_no, task_update.update(path, line_no, expect,
                                               status=status)
        except task_update.TaskUpdateError as e:
            if e.current is None:
                raise
            line_no = task_update.find_line(path, expect)
            return line_no, task_update.update(path, line_no, expect,
                                               status=status)
    except task_update.TaskUpdateError as e:
        raise ListError(f'{e}. Nothing was changed.')


def _close(item: list_note.Item) -> None:
    s = item.source
    path = s['file'] + '.md'
    line_no, result = _update_task(path, s['line'], s['text'], 'x')
    # A recurring task gets its next occurrence inserted above the line
    now = line_no + 1 if result.created is not None else line_no
    item.closed = {'line': now, 'text': result.new}


def _reopen(item: list_note.Item) -> None:
    path = item.source['file'] + '.md'
    _update_task(path, item.closed['line'], item.closed['text'], ' ')
    item.closed = None


def set_state(note_: ListNote, number: int, state: str,
              expect: str | None = None) -> None:
    """
    Set an item's state, closing or reopening its source task as needed.
    The task is written only after the item and the task have both been
    checked; a mismatch raises ListError with both files untouched.
    """
    _, item = list_note.item_at(note_, number, expect)
    if item.state == state:
        return
    if state == 'done' and item.source and not item.closed:
        _close(item)
    elif state != 'done' and item.closed:
        _reopen(item)
    item.state = state


# The current list

def _daily_path(day: date) -> str:
    return note.periodic_note('daily', day)[0]


def current(day: date) -> str | None:
    """The list path linked from the day's daily note, if any."""
    try:
        with open(_daily_path(day), encoding='utf-8') as f:
            for line in f:
                if m := CURRENT_RE.match(line):
                    return m.group(1) + '.md'
    except (FileNotFoundError, UnicodeDecodeError):
        pass
    return None


def set_current(path: str, day: date, mode: str = 'work') -> str:
    """Record path as the day's current list; returns the daily note's path."""
    daily = _daily_path(day)
    try:
        note.create('daily', day.isoformat(), mode=mode, today=day)
    except note.NoteError as e:
        raise ListError(str(e))
    with open(daily, encoding='utf-8') as f:
        lines = f.read().split('\n')
    link = f'Current list: [[{path.removesuffix(".md")}]]'
    for i, line in enumerate(lines):
        if CURRENT_RE.match(line):
            lines[i] = link
            break
    else:
        at = 0
        if lines and lines[0].startswith('# '):
            at = 1
            if len(lines) > 1 and not lines[1].strip():
                at = 2
        lines[at:at] = [link, ""]
    tmp = daily + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    os.replace(tmp, daily)
    return daily
