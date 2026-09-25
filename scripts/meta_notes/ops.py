"""
File operations: move, rename, and archive notes and folders.

Ported from autoload/meta_notes/file_ops.vim. All paths are relative to the
current directory, which the CLI sets to the notes root. Error messages match
the Vimscript because the vader tests match on them.
"""

import glob
import os
import shutil
from dataclasses import dataclass, field

import update_links

ARCHIVABLE_FOLDERS = ("project", "area", "resource")


class OpError(Exception):
    """A file operation failed; the message is shown to the user."""


@dataclass
class MoveResult:
    """Outcome of a move: what moved where and which files had links rewritten."""
    source: str
    dest: str
    moves: list[tuple[str, str]] = field(default_factory=list)
    links_updated: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ArchiveItem:
    """Outcome of archiving a single path."""
    path: str
    ok: bool
    message: str
    error: str = ""
    is_file: bool = False
    archive_path: str = ""
    result: MoveResult | None = None


def _relpath(path: str) -> str:
    """Path relative to the current directory, like Vim's `:p:.`."""
    abs_path = os.path.abspath(path)
    rel = os.path.relpath(abs_path)
    return abs_path if rel == ".." or rel.startswith("../") else rel


def _strip_md(path: str) -> str:
    return path[:-3] if path.endswith(".md") else path


def _update_header(old_path: str, new_path: str) -> None:
    """Rewrite the first line of new_path if it is exactly `# <old path>`."""
    if not os.path.isfile(new_path):
        return

    with open(new_path, "rb") as f:
        content = f.read()
    if not content:
        return

    first, sep, rest = content.partition(b"\n")
    expected = ("# " + _strip_md(_relpath(old_path))).encode("utf-8")
    if first != expected:
        return

    header = ("# " + _strip_md(_relpath(new_path))).encode("utf-8")
    with open(new_path, "wb") as f:
        f.write(header + sep + rest)


def _update_links(result: MoveResult) -> None:
    """Rewrite wiki-links for every entry in the move list."""
    for old_path, new_path in result.moves:
        old_link = _strip_md(_relpath(old_path))
        new_link = _strip_md(_relpath(new_path))
        try:
            # "." rather than an absolute root: update_links skips any path
            # with a dot directory.
            stats = update_links.update_all_links(".", old_link, new_link)
        except Exception as e:  # noqa: BLE001 - reported, move already done
            result.warnings.append(
                f"Failed to update wiki-links for: {old_link} ({e})")
            continue
        for filepath, _count in stats["modified_files"]:
            if filepath not in result.links_updated:
                result.links_updated.append(filepath)


def move(source: str, dest: str) -> MoveResult:
    """
    Move a note or folder, rewriting headers and wiki-links.

    Args:
        source: Existing file or folder path.
        dest: Destination path. `.md` is appended for a `.md` source.

    Returns:
        MoveResult with the move list and link-rewritten files.

    Raises:
        OpError: If the source is missing, the target exists, or the move fails.
    """
    source = source.rstrip("/") or source
    dest = dest.rstrip("/") or dest
    is_file = os.path.isfile(source)
    is_dir = os.path.isdir(source)

    if not is_file and not is_dir:
        raise OpError(f"Source not found: {source}")

    if is_file:
        if source.endswith(".md") and not dest.endswith(".md"):
            dest = dest + ".md"

        if os.path.isfile(dest) or os.path.isdir(dest):
            raise OpError(f"Target file already exists: {dest}")

        target_dir = os.path.dirname(dest)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)

        try:
            shutil.move(source, dest)
        except OSError:
            raise OpError(f"Failed to move file: {source}")

        result = MoveResult(source, dest, [(source, dest)])
    else:
        # Every note under the folder, then the folder itself so links to the
        # folder (e.g. [[project/folder]]) are rewritten even with no notes.
        pattern = os.path.join(glob.escape(source), "**", "*.md")
        prefix_len = len(source)
        moves = [(f, dest + f[prefix_len:])
                 for f in sorted(glob.glob(pattern, recursive=True))]
        moves.append((source, dest))

        dest_parent = os.path.dirname(dest)
        if dest_parent:
            os.makedirs(dest_parent, exist_ok=True)

        try:
            shutil.move(source, dest)
        except (OSError, shutil.Error) as e:
            raise OpError(f"Failed to move directory: {source}\n{e}")

        result = MoveResult(source, dest, moves)

    for old_path, new_path in result.moves:
        _update_header(old_path, new_path)

    _update_links(result)
    return result


def rename(source: str, new_name: str) -> MoveResult:
    """
    Rename a note. A bare name keeps the source's directory.

    Args:
        source: Existing note path.
        new_name: New name, or a path if it contains `/`. `.md` is appended.

    Returns:
        MoveResult from the underlying move.
    """
    if "/" in new_name:
        new_path = new_name
    else:
        new_path = os.path.join(os.path.dirname(source), new_name)

    if not new_path.endswith(".md") and not os.path.isdir(source):
        new_path = new_path + ".md"

    return move(source, new_path)


def archive_item(path: str) -> ArchiveItem:
    """
    Archive one note or folder from project/, area/, or resource/.

    Args:
        path: Note path (with or without `.md`) or folder path.

    Returns:
        ArchiveItem describing the archived item.

    Raises:
        OpError: If the path is missing, not archivable, or the move fails.
    """
    path_no_ext = _strip_md(path)
    is_file = os.path.isfile(path)
    is_dir = os.path.isdir(path_no_ext)

    if not is_file and not is_dir:
        if os.path.isfile(path_no_ext + ".md"):
            path = path_no_ext + ".md"
            is_file = True
        else:
            raise OpError(f"Path not found: {path}")

    parts = [p for p in path_no_ext.split("/") if p]
    if not parts:
        raise OpError(f"Invalid path: {path}")

    if parts[0] not in ARCHIVABLE_FOLDERS:
        raise OpError(
            "Can only archive items from project/, area/, or resource/ folders")

    archive_path = "archive/" + path_no_ext
    source = path if is_file else path_no_ext

    result = move(source, archive_path)

    if len(result.moves) > 1:
        message = (f"Archived: {path_no_ext} → {archive_path} "
                   f"({len(result.moves)} files)")
    else:
        message = (f"Archived: {path} → {archive_path}"
                   + (".md" if is_file else ""))

    return ArchiveItem(path=source, ok=True, message=message, is_file=is_file,
                       archive_path=result.dest, result=result)


def has_wildcard(path: str) -> bool:
    return "*" in path or "?" in path


def archive(paths: list[str]) -> list[ArchiveItem]:
    """
    Archive each path, expanding `*` and `?`.

    A single path without wildcards raises on failure. Otherwise every match
    is archived independently and failures are returned per item.

    Raises:
        OpError: For a single-path failure, or a pattern matching nothing.
    """
    if len(paths) == 1 and not has_wildcard(paths[0]):
        return [archive_item(paths[0])]

    items: list[str] = []
    for path in paths:
        if has_wildcard(path):
            matches = sorted(glob.glob(path))
            if not matches:
                raise OpError(f"No items match wildcard pattern: {path}")
            items.extend(matches)
        else:
            items.append(path)

    results: list[ArchiveItem] = []
    for item in items:
        try:
            results.append(archive_item(item))
        except OpError as e:
            results.append(ArchiveItem(
                path=item, ok=False, error=str(e),
                message=f"Failed to archive: {item} ({e})"))
    return results


def archive_summary(items: list[ArchiveItem]) -> str:
    """Summary line for a batch archive."""
    archived = sum(1 for i in items if i.ok)
    failed = len(items) - archived
    return (f"Archived {archived} item(s)"
            + (f" ({failed} failed)" if failed else ""))
