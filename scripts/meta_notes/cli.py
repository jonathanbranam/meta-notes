"""
meta-notes command line interface.

Every command resolves the notes root, changes into it, and treats paths as
relative to it. Output is human-readable text by default. With --json, stdout
carries exactly one JSON object on success and failure, and nothing is
written to stderr (Vim's system() merges stderr into the captured output).
"""

import argparse
import contextlib
import io
import json
import os
import sys
from dataclasses import dataclass, field

from meta_notes import ops, query

ROOT_MARKERS = ("plan", "project", "area")


class CliError(Exception):
    """A command failed; the message is reported to the user."""


@dataclass
class Output:
    """What a command produced: JSON fields, text lines, and any error."""
    data: dict = field(default_factory=dict)
    text: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
    # Text-mode-only stderr lines, for details the JSON carries elsewhere
    notices: list[str] = field(default_factory=list)


class _Parser(argparse.ArgumentParser):
    """ArgumentParser that raises instead of printing and exiting."""

    def error(self, message):
        raise CliError(f"{self.prog}: {message}")


def is_notes_root(path: str) -> bool:
    return all(os.path.isdir(os.path.join(path, m)) for m in ROOT_MARKERS)


def resolve_root(explicit: str | None, env: str | None, cwd: str) -> str:
    """
    Resolve the notes root.

    Args:
        explicit: --root value, used as-is if given.
        env: META_NOTES_ROOT value, used as-is if given.
        cwd: Directory to walk up from otherwise.

    Returns:
        Absolute path of the notes root.

    Raises:
        CliError: If the given root isn't a directory or none is found.
    """
    given = explicit or env
    if given:
        root = os.path.abspath(os.path.expanduser(given))
        if not os.path.isdir(root):
            raise CliError(f"Notes root is not a directory: {given}")
        return root

    path = os.path.abspath(cwd)
    while True:
        if is_notes_root(path):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            raise CliError(
                "No notes root found (a directory containing plan/, project/, "
                "and area/); use --root or set META_NOTES_ROOT")
        path = parent


def to_root_relative(path: str, root: str) -> str:
    """Make an absolute path inside the root relative to it."""
    if not os.path.isabs(path):
        return path
    rel = os.path.relpath(path, root)
    return path if rel == ".." or rel.startswith("../") else rel


def _move_data(result: ops.MoveResult) -> dict:
    return {
        "source": result.source,
        "dest": result.dest,
        "moves": [list(m) for m in result.moves],
        "links_updated": result.links_updated,
    }


def _move_text(result: ops.MoveResult) -> list[str]:
    count = len(result.moves)
    if count <= 1:
        return [f"Moved: {result.source} → {result.dest}"]
    return [f"Moved: {result.source} → {result.dest} ({count} files)"]


def cmd_move(args, root: str) -> Output:
    try:
        result = ops.move(to_root_relative(args.source, root),
                          to_root_relative(args.dest, root))
    except ops.OpError as e:
        raise CliError(str(e))
    return Output(_move_data(result), _move_text(result), result.warnings)


def cmd_rename(args, root: str) -> Output:
    source = to_root_relative(args.source, root)
    try:
        result = ops.rename(source, to_root_relative(args.new_name, root))
    except ops.OpError as e:
        raise CliError(str(e))
    text = [f"Renamed: {result.source} → {result.dest}"]
    return Output(_move_data(result), text, result.warnings)


def cmd_archive(args, root: str) -> Output:
    paths = [to_root_relative(p, root) for p in args.paths]
    try:
        items = ops.archive(paths)
    except ops.OpError as e:
        raise CliError(str(e))

    batch = len(paths) > 1 or ops.has_wildcard(paths[0])
    out = Output()
    moves: list[list[str]] = []
    links: list[str] = []
    item_data = []
    for item in items:
        data = {"path": item.path, "ok": item.ok, "message": item.message}
        if item.ok:
            data.update(is_file=item.is_file, archive_path=item.archive_path,
                        **_move_data(item.result))
            moves.extend(data["moves"])
            links.extend(f for f in item.result.links_updated if f not in links)
            out.warnings.extend(item.result.warnings)
            out.text.append(item.message)
        else:
            data["error"] = item.error
            out.notices.append(item.message)
        item_data.append(data)

    failed = sum(1 for i in items if not i.ok)
    if failed:
        out.error = f"{failed} of {len(items)} item(s) failed to archive"

    out.data = {"batch": batch, "items": item_data, "archived": len(items) - failed,
                "failed": failed, "moves": moves, "links_updated": links}
    if batch:
        out.data["summary"] = ops.archive_summary(items)
        out.text.append(out.data["summary"])
    return out


def cmd_tasks(args, root: str) -> Output:
    try:
        lines, tasks = query.run(
            ".", folder=args.folder, due_on=args.due_on, due_by=args.due_by,
            due_between=args.due_between, status=args.status,
            condensed=args.condensed or args.format == "condensed")
    except ValueError as e:
        raise CliError(str(e))
    return Output({"tasks": tasks}, lines)


def build_parser() -> argparse.ArgumentParser:
    # --root and --json are accepted before or after the subcommand. Both
    # default to SUPPRESS so the subcommand's copy doesn't overwrite the top
    # level's; read them with getattr.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", default=argparse.SUPPRESS,
                        help="notes root (default: $META_NOTES_ROOT, or the "
                             "nearest directory containing plan/, project/, area/)")
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="write one JSON object to stdout")

    parser = _Parser(prog="meta-notes", parents=[common],
                     description="Operate on a meta-notes notes root.")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                parser_class=_Parser)
    sub.required = True

    p = sub.add_parser("move", parents=[common],
                       help="move a note or folder, updating headers and links")
    p.add_argument("source")
    p.add_argument("dest")
    p.set_defaults(handler=cmd_move)

    p = sub.add_parser("rename", parents=[common],
                       help="rename a note (a bare name keeps its directory)")
    p.add_argument("source")
    p.add_argument("new_name")
    p.set_defaults(handler=cmd_rename)

    p = sub.add_parser("archive", parents=[common],
                       help="move items from project/, area/, or resource/ "
                            "to archive/ (supports * and ?)")
    p.add_argument("paths", nargs="+", metavar="path")
    p.set_defaults(handler=cmd_archive)

    p = sub.add_parser("tasks", parents=[common],
                       help="list tasks (same options and output as find_tasks.py)")
    p.add_argument("--folder",
                   help="filter tasks from specific folder (includes subfolders)")
    p.add_argument("--due-on", metavar="DATE",
                   help="show tasks due on specific date (YYYY-MM-DD)")
    p.add_argument("--due-by", metavar="DATE",
                   help="show tasks due on or before date (YYYY-MM-DD)")
    p.add_argument("--due-between", nargs=2, metavar=("START", "END"),
                   help="show tasks due between dates (YYYY-MM-DD YYYY-MM-DD)")
    p.add_argument("--status", default="incomplete",
                   choices=["incomplete", "completed", "rescheduled", "canceled", "all"],
                   help="filter by task status (default: incomplete)")
    p.add_argument("--format", choices=["standard", "condensed"], default="standard",
                   help="output format (default: standard)")
    p.add_argument("--condensed", action="store_true",
                   help="use condensed output format (synonym for --format=condensed)")
    p.set_defaults(handler=cmd_tasks)

    return parser


def _run(argv: list[str]) -> Output:
    args = build_parser().parse_args(argv)
    root = resolve_root(getattr(args, "root", None), os.environ.get("META_NOTES_ROOT"), os.getcwd())
    os.chdir(root)
    return args.handler(args, root)


def main(argv: list[str] | None = None) -> int:
    """Run the CLI. Returns the process exit code."""
    argv = sys.argv[1:] if argv is None else argv
    # Checked before parsing so argument errors are reported as JSON too
    as_json = "--json" in argv

    captured = io.StringIO()
    redirect = (contextlib.redirect_stderr(captured) if as_json
                else contextlib.nullcontext())
    try:
        with redirect:
            out = _run(argv)
    except CliError as e:
        out = Output(error=str(e))

    # Anything library code wrote to stderr becomes a warning under --json
    out.warnings = ([line for line in captured.getvalue().splitlines() if line]
                    + out.warnings)

    if as_json:
        payload = {"ok": out.error is None}
        if out.error is not None:
            payload["error"] = out.error
        payload.update(out.data)
        payload["warnings"] = out.warnings
        print(json.dumps(payload, ensure_ascii=False))
    else:
        if out.text:
            print("\n".join(out.text))
        for notice in out.notices:
            print(notice, file=sys.stderr)
        for warning in out.warnings:
            print(f"Warning: {warning}", file=sys.stderr)
        if out.error is not None:
            print(f"Error: {out.error}", file=sys.stderr)

    return 0 if out.error is None else 1
