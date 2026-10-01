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


def _lines(node: tasks.Node, source: list[str], tree: bool) -> list[str]:
    end = node.subtree_end if tree else node.end_line
    return [line.rstrip() for line in source[node.line_no - 1:end]]


def show(path: str, line_no: int, tree: bool = False) -> tuple[dict, list[str]]:
    """
    Read the task at path:line_no.

    Args:
        path: The note, as given (relative to the working directory).
        line_no: The checkbox line, counting from 1.
        tree: Include the subtree (every descendant) instead of the node
            alone (its line and notes).

    Returns:
        A tuple of (the JSON data, the lines read). The data has file, line,
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
    return data, _lines(node, source, tree)
