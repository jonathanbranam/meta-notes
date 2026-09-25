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
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date

import find_tasks
from tags import canonical_tag
from meta_notes import __version__, init, note, ops, query, task_update, time
from meta_notes.root import SENTINEL, find_root


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


class _ShowVersion(Exception):
    """--version was given; report the version instead of running a command."""


class _VersionAction(argparse.Action):
    """Raise _ShowVersion when --version is parsed, so main() formats it."""

    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, nargs=0,
                         default=argparse.SUPPRESS, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        raise _ShowVersion()


class _Parser(argparse.ArgumentParser):
    """ArgumentParser that raises instead of printing and exiting."""

    def error(self, message):
        raise CliError(f"{self.prog}: {message}")


def resolve_root(explicit: str | None, env: str | None, cwd: str,
                 home: str | None = None) -> str:
    """
    Resolve the notes root.

    Args:
        explicit: --root value, used as-is if given.
        env: META_NOTES_ROOT value, used as-is if given.
        cwd: Directory to search upward from otherwise.
        home: $HOME, where the upward search stops.

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

    root = find_root(cwd, home)
    if root is None:
        raise CliError(
            f"No notes root found (a directory containing {SENTINEL}); run "
            "`meta-notes init` in the notes root, or pass --root")
    return root


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
    except ops.ArchiveError as e:
        # A project may be marked archived even though it didn't move
        return Output({"fields_written": e.fields_written, "home": e.home},
                      warnings=e.warnings, error=str(e))
    except ops.OpError as e:
        raise CliError(str(e))

    batch = len(paths) > 1 or ops.has_wildcard(paths[0])
    out = Output()
    moves: list[list[str]] = []
    links: list[str] = []
    item_data = []
    for item in items:
        data = {"path": item.path, "ok": item.ok, "message": item.message,
                "fields_written": item.fields_written, "home": item.home}
        out.warnings.extend(item.warnings)
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
            ".", period=args.date, modes=args.modes, later=args.later,
            tags=args.tags, group_by=args.group_by, folder=args.folder,
            status=args.status,
            condensed=args.condensed or args.format == "condensed")
    except ValueError as e:
        raise CliError(str(e))
    return Output({"tasks": tasks}, lines)


def cmd_time(args, root: str) -> Output:
    try:
        lines, data = time.run(".", args.date)
    except ValueError as e:
        raise CliError(str(e))
    return Output(data | {"report": "\n".join(lines)}, lines)


def cmd_note(args, root: str) -> Output:
    if args.kind == "new":
        value = to_root_relative(args.path, root)
        template_name = args.template
    else:
        value = args.date
        template_name = None
    try:
        result = note.create(args.kind, value, template_name=template_name,
                             render_only=args.render)
    except note.NoteError as e:
        raise CliError(str(e))

    out = Output({"path": result.path, "exists": result.exists,
                  "created": result.created, "template": result.template},
                 warnings=result.warnings)
    if not args.render:
        out.text = [result.path]
    elif result.exists:
        out.notices = [f"Note already exists: {result.path}"]
    else:
        out.data["content"] = result.content
        out.text = [result.content.removesuffix("\n")]
    return out


STATUS_CHARS = (" ", "x", "X", ">", "-", ".", "o", "O")


def _date_value(value: str, keywords: tuple[str, ...]) -> str:
    """Check a --due or --start value: YYYY-MM-DD or one of keywords."""
    if value in keywords:
        return value
    # fromisoformat alone also accepts forms such as 20261001
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        try:
            date.fromisoformat(value)
            return value
        except ValueError:
            pass
    raise argparse.ArgumentTypeError(
        f"invalid value: {value!r} (expected YYYY-MM-DD or "
        f"{' or '.join(keywords)})")


def _due_value(value: str) -> str:
    return _date_value(value, ("undated", "none"))


def _start_value(value: str) -> str:
    return _date_value(value, ("none",))


def _tag_value(value: str) -> str:
    """Check a tag name, with or without #; return it without #."""
    bare = value.removeprefix("#")
    if not re.fullmatch(r"[\w-]+", bare):
        raise argparse.ArgumentTypeError(
            f"invalid tag: {value!r} (letters, digits, _, or - after an "
            "optional #)")
    return bare


def cmd_task_update(args, root: str) -> Output:
    prog = "meta-notes task update"
    path, sep, line = args.target.rpartition(":")
    if not sep or not path or not line.isdigit():
        raise CliError(f"{prog}: target must be <file>:<line>, got "
                       f"{args.target!r}")
    path = to_root_relative(path, root)
    line_no = int(line)

    add_tags, remove_tags = args.add_tags or [], args.remove_tags or []
    both = ({canonical_tag(t).lower() for t in add_tags}
            & {canonical_tag(t).lower() for t in remove_tags})
    if both:
        raise CliError(f"{prog}: tag given to both --add-tag and --remove-tag: "
                       f"{', '.join(sorted(both))}")
    if (args.status is None and args.due is None and args.start is None
            and not add_tags and not remove_tags):
        raise CliError(f"{prog}: give at least one of --status, --add-tag, "
                       "--remove-tag, --due, or --start")

    try:
        result = task_update.update(
            path, line_no, args.expect, status=args.status, add_tags=add_tags,
            remove_tags=remove_tags, due=args.due, start=args.start,
            no_completed=args.no_completed)
    except task_update.TaskUpdateError as e:
        if e.current is None:
            raise CliError(str(e))
        return Output({"file": path, "line": line_no, "current": e.current},
                      error=str(e))

    out = Output({"file": path, "line": line_no, "old": result.old,
                  "new": result.new, "changed": result.changed},
                 warnings=result.warnings)
    if result.changed:
        out.text = [f"{path}:{line_no}", f"- {result.old}", f"+ {result.new}"]
    else:
        out.text = [f"{path}:{line_no} unchanged"]
    return out


INIT_MESSAGES = {
    ("folder", "created"): "Created directory: {}",
    ("folder", "exists"): "Directory already exists: {}",
    ("template", "created"): "Created template: {}",
    ("template", "overwritten"): "Overwrote template: {}",
    ("template", "exists"): "Template already exists: {}",
    ("sentinel", "created"): "Created notes root marker: {}",
    ("sentinel", "exists"): "Notes root marker already exists: {}",
    ("skill", "created"): "Linked skill: {}",
    ("skill", "exists"): "Skill already linked: {}",
    ("skill", "repointed"): "Relinked skill: {}",
    ("skill", "replaced"): "Replaced with skill link: {}",
}


def cmd_init(args, root: None) -> Output:
    # init doesn't resolve a root: it initializes --root or the current
    # directory, and ignores META_NOTES_ROOT
    target = getattr(args, "root", None) or os.getcwd()
    try:
        result = init.init(target, force=args.force, home=os.environ.get("HOME"))
    except init.InitError as e:
        raise CliError(str(e))

    items = [{"kind": i.kind, "path": i.path, "status": i.status}
             for i in result.items]
    text = [INIT_MESSAGES[(i.kind, i.status)].format(i.path)
            for i in result.items if (i.kind, i.status) in INIT_MESSAGES]
    text.append("Meta-notes initialization complete!")
    return Output({"root": result.root, "items": items}, text, result.warnings)


# The plugin checkout: scripts/meta_notes/cli.py -> the plugin directory
PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


def _git(plugin_dir: str, *args: str) -> str | None:
    """Run git in plugin_dir; return its stdout, or None if it fails."""
    try:
        result = subprocess.run(["git", "-C", plugin_dir, *args],
                                stdin=subprocess.DEVNULL, capture_output=True,
                                text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout if result.returncode == 0 else None


def git_commit(plugin_dir: str) -> tuple[str | None, bool]:
    """
    Find the commit a plugin checkout is on.

    Args:
        plugin_dir: The plugin directory.

    Returns:
        (short hash, dirty), where dirty means tracked files have uncommitted
        changes. (None, False) if plugin_dir isn't the top level of a git
        working tree (so an enclosing repository isn't reported) or git
        fails.
    """
    out = _git(plugin_dir, "rev-parse", "--show-toplevel", "--short", "HEAD")
    lines = out.split() if out else []
    if (len(lines) != 2
            or os.path.realpath(lines[0]) != os.path.realpath(plugin_dir)):
        return None, False
    status = _git(plugin_dir, "status", "--porcelain", "--untracked-files=no")
    return lines[1], bool(status and status.strip())


def cmd_version(plugin_dir: str = PLUGIN_DIR) -> Output:
    commit, dirty = git_commit(plugin_dir)
    line = f"meta-notes {__version__}"
    if commit:
        line += f" ({commit}{'-dirty' if dirty else ''})"
    return Output({"version": __version__, "commit": commit, "dirty": dirty},
                  [line])


def build_parser() -> argparse.ArgumentParser:
    # --root and --json are accepted before or after the subcommand. Both
    # default to SUPPRESS so the subcommand's copy doesn't overwrite the top
    # level's; read them with getattr.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", default=argparse.SUPPRESS,
                        help="notes root (default: $META_NOTES_ROOT, or the "
                             f"nearest directory containing {SENTINEL})")
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="write one JSON object to stdout")
    common.add_argument("--version", action=_VersionAction,
                        help="show the meta-notes version and exit")

    parser = _Parser(prog="meta-notes", parents=[common],
                     description="Operate on a meta-notes notes root.")
    parser.set_defaults(resolves_root=True)
    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                parser_class=_Parser)
    sub.required = True

    p = sub.add_parser("init", parents=[common],
                       help="set up a notes root (--root or the current "
                            "directory): folders, templates, sentinel, skills")
    p.add_argument("--force", action="store_true",
                   help="overwrite templates and replace skill targets "
                        "that aren't links")
    p.set_defaults(handler=cmd_init, resolves_root=False)

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
    find_tasks.add_query_arguments(p)
    p.set_defaults(handler=cmd_tasks)

    p = sub.add_parser("time", parents=[common],
                       help="time report for a day or period (same output as "
                            "time_report.py --date)")
    p.add_argument("--date", metavar="DATE",
                   help="YYYY-MM-DD for a day report; YYYY-MM-DD..YYYY-MM-DD, "
                        "YYYY-MM, YYYY-Qn, or YYYY for a period report "
                        "(default: today)")
    p.set_defaults(handler=cmd_time)

    p = sub.add_parser("note", parents=[common],
                       help="create a note from its template, unless it exists; "
                            "print its path")
    kinds = p.add_subparsers(dest="kind", metavar="KIND", parser_class=_Parser)
    kinds.required = True
    render = argparse.ArgumentParser(add_help=False)
    render.add_argument("--render", action="store_true",
                        help="print the rendered note instead of writing it")
    for kind, period in (("daily", "day"), ("weekly", "week"),
                         ("quarterly", "quarter"), ("yearly", "year")):
        k = kinds.add_parser(kind, parents=[common, render],
                             help=f"the {period}'s plan note")
        k.add_argument("date", nargs="?",
                       help=f"a date in the {period}, YYYY-MM-DD (default: today)")
    k = kinds.add_parser("new", parents=[common, render],
                         help="any other note, by path (.md added if missing)")
    k.add_argument("path")
    k.add_argument("--template", metavar="NAME",
                   help="use resource/template/NAME.md instead of "
                        "template discovery")
    p.set_defaults(handler=cmd_note)

    p = sub.add_parser("task", parents=[common],
                       help="edit a task line in place")
    kinds = p.add_subparsers(dest="kind", metavar="KIND", parser_class=_Parser)
    kinds.required = True
    k = kinds.add_parser("update", parents=[common],
                         help="edit one checkbox line's status, tags, and dates")
    k.add_argument("target", metavar="FILE:LINE",
                   help="the note, relative to the notes root, and the line "
                        "number (from 1)")
    k.add_argument("--expect", required=True, metavar="TEXT",
                   help="the line as last read; nothing is written if it "
                        "differs (ignoring trailing whitespace)")
    k.add_argument("--status", choices=STATUS_CHARS, metavar="CHAR",
                   help="set the status character: ' ', x, X, >, -, ., o, "
                        "or O")
    k.add_argument("--add-tag", dest="add_tags", action="append",
                   type=_tag_value, metavar="TAG",
                   help="add a tag before the first date (repeatable)")
    k.add_argument("--remove-tag", dest="remove_tags", action="append",
                   type=_tag_value, metavar="TAG",
                   help="remove a tag, ignoring case and applying aliases "
                        "(repeatable)")
    k.add_argument("--due", type=_due_value, metavar="DATE",
                   help="YYYY-MM-DD, undated (a bare due emoji), or none")
    k.add_argument("--start", type=_start_value, metavar="DATE",
                   help="YYYY-MM-DD or none")
    k.add_argument("--no-completed", action="store_true",
                   help="don't add a ✅ date when marking the task done")
    p.set_defaults(handler=cmd_task_update)

    return parser


def _run(argv: list[str]) -> Output:
    try:
        args = build_parser().parse_args(argv)
    except _ShowVersion:
        return cmd_version()
    if not args.resolves_root:
        return args.handler(args, None)
    root = resolve_root(getattr(args, "root", None), os.environ.get("META_NOTES_ROOT"),
                        os.getcwd(), os.environ.get("HOME"))
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
