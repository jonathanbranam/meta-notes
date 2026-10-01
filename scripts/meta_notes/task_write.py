"""
Task write: replace a task's notes, replace a node or a whole subtree, and
add a subtask, each with an --expect guard and one write.

A node is a checkbox line and its own notes; the subtree adds every
descendant (see tasks.parse_outline and task_show). Only the lines the edit
names change, and the file keeps its line endings.
"""

from dataclasses import dataclass, field

import tasks
from meta_notes import task_show
from meta_notes.task_update import (
    DONE_CHARS, TaskUpdateError, _LINE_PATTERN, _split_ending, new_task_line,
    update_ancestors)


@dataclass
class WriteResult:
    """
    Outcome of a write: the lines replaced (old) and written (new), without
    endings, where the written lines start (line) and end (end_line), and
    the ancestors whose status changed (see update_ancestors).
    """
    old: list[str]
    new: list[str]
    line: int
    end_line: int
    changed: bool
    ancestors: list[dict] = field(default_factory=list)


def _read(path: str) -> list[str]:
    try:
        with open(path, encoding='utf-8', newline='') as f:
            return _LINE_PATTERN.findall(f.read())
    except FileNotFoundError:
        raise TaskUpdateError(f"No such file: {path}")
    except (OSError, UnicodeDecodeError) as e:
        raise TaskUpdateError(f"Could not read {path}: {e}")


def _node(path: str, lines: list[str], line_no: int) -> tasks.Node:
    contents = [_split_ending(line)[0] for line in lines]
    if not 1 <= line_no <= len(lines):
        raise TaskUpdateError(
            f"Line {line_no} is out of range: {path} has {len(lines)} lines")
    node = next((n for n in tasks.parse_outline(contents)
                 if n.line_no == line_no), None)
    if node is None:
        raise TaskUpdateError(f"Line {line_no} of {path} is not a checkbox")
    return node


def _joined(lines: list[str]) -> str:
    return '\n'.join(line.rstrip() for line in lines)


def _guard(path: str, line_no: int, expect: str, current: list[str]) -> None:
    if _joined(expect.splitlines()) != _joined(current):
        raise TaskUpdateError(
            f"Line {line_no} of {path} has changed; it is now:\n"
            + _joined(current), current=_joined(current))


def _new_lines(text: str) -> list[str]:
    return [line.rstrip() for line in text.splitlines()]


def _store(path: str, lines: list[str]) -> None:
    default = next((_split_ending(line)[1] for line in lines
                    if _split_ending(line)[1]), '\n')
    # Only the last line may lack an ending
    lines = [line if _split_ending(line)[1] else line + default
             for line in lines[:-1]] + lines[-1:]
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(''.join(lines))


def _ending(lines: list[str], line_no: int) -> str:
    return (_split_ending(lines[line_no - 1])[1]
            or next((_split_ending(line)[1] for line in lines
                     if _split_ending(line)[1]), '\n'))


def _splice(path: str, lines: list[str], node: tasks.Node, drop: list[int],
            new: list[str], old: list[str]) -> WriteResult:
    """Replace the lines numbered drop with new, which start at node's line."""
    ending = _ending(lines, node.line_no)
    first = node.line_no
    kept = [line for n, line in enumerate(lines, 1) if n not in set(drop)]
    kept[first - 1:first - 1] = [line + ending for line in new]
    result = WriteResult(old=old, new=new, line=first,
                         end_line=first + len(new) - 1,
                         changed=new != old)
    old_char = node.status_char
    box = tasks.CHECKBOX_PATTERN.match(new[0]) if new else None
    if box and box.group(1) != old_char:
        result.ancestors = update_ancestors(kept, first)
    if result.changed or result.ancestors:
        _store(path, kept)
    return result


def replace_notes(path: str, line_no: int, expect: str,
                  text: str) -> WriteResult:
    """
    Replace the notes of the task at path:line_no.

    Args:
        path: The note.
        line_no: The checkbox line, counting from 1.
        expect: The task's notes as last read (task show's lines after the
            first), compared ignoring trailing whitespace; empty for none.
        text: The new notes, one per line, as written (indented deeper than
            the task, no checkbox lines, no blank lines); empty removes the
            notes. They go directly under the task line, before its
            subtasks, replacing every note the task owned (also any after
            its subtasks).

    Returns:
        The old and new notes; line is the first note's line, or the line
        below the task when there are none. The file is written only if
        the notes changed.

    Raises:
        TaskUpdateError: If the file can't be read, the line isn't a
            checkbox line, the notes don't match expect (the error's
            current is the notes), or a new note is invalid.
    """
    lines = _read(path)
    node = _node(path, lines, line_no)
    own = task_show.line_numbers(node, False)[1:]
    old = [_split_ending(lines[n - 1])[0] for n in own]
    _guard(path, line_no, expect, old)
    new = _new_lines(text)
    for note in new:
        if not note.strip():
            raise TaskUpdateError("A note can't be a blank line: it would "
                                  "end the task")
        if tasks.CHECKBOX_PATTERN.match(note):
            raise TaskUpdateError(f"A note can't be a checkbox line: {note!r}"
                                  " (use task add --under for a subtask)")
        if tasks._indent_of(note) <= node.indent:
            raise TaskUpdateError(
                f"A note must be indented deeper than its task: {note!r}")
    ending = _ending(lines, node.line_no)
    kept = [line for n, line in enumerate(lines, 1) if n not in set(own)]
    kept[line_no:line_no] = [line + ending for line in new]
    result = WriteResult(old=old, new=new, line=line_no + 1,
                         end_line=line_no + len(new), changed=new != old)
    if result.changed:
        _store(path, kept)
    return result


def replace_node(path: str, line_no: int, expect: str, text: str,
                 tree: bool = False) -> WriteResult:
    """
    Replace the task at path:line_no: the line and its notes, or with tree
    the whole subtree.

    Args:
        path: The note.
        line_no: The checkbox line, counting from 1.
        expect: The lines replaced as last read (what task show prints for
            the same target), compared ignoring trailing whitespace.
        text: The new lines, as written. The first must be a checkbox line
            at the task's indent, the rest indented deeper than it, and none
            blank. Replacing the node alone leaves its subtasks where they
            are, below the new lines.
        tree: Replace the subtree.

    Returns:
        The old and new lines. When the first line's status character
        changed, the ancestors' statuses follow it (see update_ancestors);
        the same write. The file is written only if something changed.

    Raises:
        TaskUpdateError: If the file can't be read, the line isn't a
            checkbox line, the lines don't match expect (the error's
            current is the lines), or text is invalid.
    """
    lines = _read(path)
    node = _node(path, lines, line_no)
    numbers = task_show.line_numbers(node, tree)
    old = [_split_ending(lines[n - 1])[0] for n in numbers]
    _guard(path, line_no, expect, old)
    new = _new_lines(text)
    if not new or not tasks.CHECKBOX_PATTERN.match(new[0]):
        raise TaskUpdateError("The first line of the new text must be a "
                              "checkbox line")
    if tasks._indent_of(new[0]) != node.indent:
        raise TaskUpdateError("The first line must keep the task's indent")
    for line in new[1:]:
        if not line.strip():
            raise TaskUpdateError("The new text can't have a blank line: it "
                                  "would end the task")
        if tasks._indent_of(line) <= node.indent:
            raise TaskUpdateError(
                f"Every line after the first must be indented deeper than "
                f"the task: {line!r}")
    return _splice(path, lines, node, numbers, new, old)


def add_subtask(path: str, parent_line: int, expect: str, text: str, *,
                due: str | None = None, start: str | None = None,
                time: str | None = None, recur: str | None = None,
                add_tags: list[str] | None = None) -> WriteResult:
    """
    Add an open subtask to the task at path:parent_line, after its notes
    and existing subtasks (and any note after them).

    Args:
        path: The note.
        parent_line: The parent checkbox line, counting from 1.
        expect: The parent line as last read, ignoring trailing whitespace.
        text, due, start, time, recur, add_tags: As in task_update.add.

    Returns:
        The added line (old is empty), indented like the parent's first
        subtask, else two columns deeper than the parent (a tab, if the
        parent's indent has one). The parent's status is left as it is.

    Raises:
        TaskUpdateError: If the file can't be read, the line isn't a
            checkbox line, doesn't match expect (the error's current is
            the line), or the arguments are invalid (see add).
    """
    lines = _read(path)
    node = _node(path, lines, parent_line)
    parent, _ = _split_ending(lines[parent_line - 1])
    if parent.rstrip() != expect.rstrip():
        raise TaskUpdateError(
            f"Line {parent_line} of {path} has changed; it is now: "
            f"{parent.rstrip()}", current=parent.rstrip())
    task = new_task_line(text, due, start, time, recur, add_tags)
    if node.children:
        child = _split_ending(lines[node.children[0].line_no - 1])[0]
        indent = child[:len(child) - len(child.lstrip())]
    else:
        lead = parent[:len(parent) - len(parent.lstrip())]
        indent = lead + ('\t' if '\t' in lead else '  ')
    new = indent + task
    at = node.subtree_end
    ending = _ending(lines, at)
    lines[at - 1] = _split_ending(lines[at - 1])[0] + ending
    lines.insert(at, new + ending)
    _store(path, lines)
    return WriteResult(old=[], new=[new], line=at + 1, end_line=at + 1,
                       changed=True)
