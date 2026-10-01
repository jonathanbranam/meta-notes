"""
Task show: read one checkbox line of a note with its notes, alone or with
its subtree.
"""

import tasks
from meta_notes.query import node_ref


class TaskShowError(Exception):
    """The line can't be shown."""


def _node_data(node: tasks.Node, rel: str, tree: bool) -> dict:
    data = node_ref(node, rel)
    data["end_line"] = node.subtree_end if tree else node.end_line
    data["notes"] = list(node.notes)
    if tree:
        data["subtasks"] = [_node_data(c, rel, True) for c in node.children]
    return data


def line_numbers(node: tasks.Node, tree: bool) -> list[int]:
    """
    The lines a read covers, counting from 1. The subtree is every line from
    the task through its last descendant. The node alone is the task line
    and its own notes, which skips the subtasks (and their notes) when a
    note follows them.
    """
    if tree:
        return list(range(node.line_no, node.subtree_end + 1))
    skipped = {n for child in node.children
               for n in range(child.line_no, child.subtree_end + 1)}
    return [n for n in range(node.line_no, node.end_line + 1)
            if n not in skipped]


def format_ranges(numbers: list[int]) -> str:
    """Line numbers as runs, like `1-2,5-5`; a run is first-last."""
    runs: list[list[int]] = []
    for n in numbers:
        if runs and runs[-1][1] == n - 1:
            runs[-1][1] = n
        else:
            runs.append([n, n])
    return ",".join(f"{a}-{b}" for a, b in runs)


def show(path: str, line_no: int,
         tree: bool = False) -> tuple[dict, list[str], list[int]]:
    """
    Read the task at path:line_no.

    Args:
        path: The note, as given (relative to the working directory).
        line_no: The checkbox line, counting from 1.
        tree: Include the subtree (every descendant) instead of the node
            alone (its line and notes).

    Returns:
        A tuple of (the JSON data, the lines read, their line numbers). The
        node alone has only its own lines, so the numbers may skip lines
        (see line_numbers). The data has file, line,
        end_line (the last line read), text, status, notes, and parent (null
        at the top); with tree, subtasks too, nested the same way.

    Raises:
        TaskShowError: If the file can't be read or the line isn't a
            checkbox line.
    """
    try:
        with open(path, encoding="utf-8") as f:
            source = f.read().splitlines()
    except (OSError, UnicodeDecodeError) as e:
        raise TaskShowError(f"can't read {path}: {e}")
    nodes = {n.line_no: n for n in tasks.parse_outline(source)}
    node = nodes.get(line_no)
    if node is None:
        raise TaskShowError(f"{path}:{line_no} is not a checkbox line")
    data = _node_data(node, path, tree)
    data["parent"] = node_ref(node.parent, path) if node.parent else None
    numbers = line_numbers(node, tree)
    return data, [source[n - 1].rstrip() for n in numbers], numbers
