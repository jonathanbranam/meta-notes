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
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime

import find_tasks
import tasks as task_model
from recurrence import parse_rule
from tags import canonical_tag
from meta_notes import (__version__, brief, calendar, ceremony, changes,
                        checkin, config, conventions, hours, init, note, note_write, ops, outlook, planning,
                        prime,
                        projects, query, task_show, task_update, task_write, time,
                        time_block, time_log, ui)
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
    if args.agenda:
        if set(args.modes or ()) - {"undated"} or args.date or args.at:
            raise CliError("--agenda combines only with --through and --undated")
        try:
            lines, sections, warnings = query.agenda(
                ".", through=args.through, undated="undated" in (args.modes or ()), later=args.later,
                tags=args.tags, folder=args.folder, status=args.status,
                condensed=args.condensed or args.format == "condensed")
        except ValueError as e:
            raise CliError(str(e))
        return Output({"agenda": sections}, lines, warnings)
    if args.through:
        raise CliError("--through needs --agenda")
    try:
        lines, tasks, warnings = query.run(
            ".", period=args.date, modes=args.modes, later=args.later,
            tags=args.tags, group_by=args.group_by, folder=args.folder,
            status=args.status, at=args.at,
            condensed=args.condensed or args.format == "condensed")
    except ValueError as e:
        raise CliError(str(e))
    return Output({"tasks": tasks}, lines, warnings)


def cmd_time(args, root: str) -> Output:
    try:
        lines, data = time.run(".", args.date)
    except ValueError as e:
        raise CliError(str(e))
    return Output(data | {"report": "\n".join(lines)}, lines)


def cmd_changes(args, root: str) -> Output:
    try:
        lines, data = changes.run(".", args.date)
    except ValueError as e:
        raise CliError(str(e))
    return Output(data, lines)


def cmd_calendar(args, root: str) -> Output:
    try:
        lines, data, warnings = calendar.run(root, args.date, args.ics,
                                              names=args.with_names,
                                              searches=args.search)
    except ValueError as e:
        raise CliError(str(e))
    return Output(data, lines, warnings,
                  notices=[f"Deleted: {path}" for path in data["pruned"]])


def cmd_outlook(args, root: str) -> Output:
    day = date.fromisoformat(args.date) if args.date else date.today()
    only = getattr(args, "kind", None)
    try:
        # Plain `outlook` never fails: it runs in note templates
        lines, data = outlook.run(root, day, args.location, only,
                                  lenient=only is None)
    except ValueError as e:
        raise CliError(str(e))
    return Output(data, lines)


def cmd_cache_clear(args, root: str) -> Output:
    deleted = calendar.clear(root)
    count = len(deleted)
    return Output({"deleted": deleted, "count": count},
                  [f"Deleted {count} cached calendar file(s) from "
                   f"{calendar.CALENDAR_DIR}/"])


def _ui_output(root: str, info: dict, **extra) -> Output:
    link = ui.url(root, info)
    data = {"running": True, "url": link, "pid": info["pid"],
            "host": info.get("host"), "port": info.get("port"),
            "version": info.get("version"), **extra}
    return Output(data, [link])


def cmd_ui_start(args, root: str) -> Output:
    try:
        info = ui.start(root, args.path, args.host, args.port)
    except ValueError as e:
        raise CliError(str(e)) from None
    return _ui_output(root, info)


def cmd_ui_stop(args, root: str) -> Output:
    stopped = ui.stop(root)
    return Output({"stopped": stopped},
                  ["Stopped the UI" if stopped else "The UI is not running"])


def cmd_ui_status(args, root: str) -> Output:
    info = ui.status(root)
    if not info:
        return Output({"running": False}, ["The UI is not running"])
    return Output({"running": True, "url": info["url"], "pid": info["pid"],
                   "host": info.get("host"), "port": info.get("port"),
                   "version": info.get("version")},
                  [f"The UI is running at {info['url']}",
                   f"pid {info['pid']}, version {info.get('version')}"])


def cmd_ui_url(args, root: str) -> Output:
    info = ui.status(root)
    if not info:
        raise CliError("The UI is not running: run `meta-notes ui start`")
    return _ui_output(root, info)


def cmd_ui_open(args, root: str) -> Output:
    info = ui.status(root)
    started = info is None
    if started:
        try:
            info = ui.start(root, args.path, args.host, args.port)
        except ValueError as e:
            raise CliError(str(e)) from None
    out = _ui_output(root, info, started=started)
    try:
        ui.open_url(out.data["url"])
    except ValueError as e:
        raise CliError(str(e)) from None
    return out


def _root_mode(root: str) -> str:
    """The root's mode; a root without .meta-notes (an older one) is work."""
    if not os.path.isfile(os.path.join(root, SENTINEL)):
        return "work"
    try:
        return config.mode(root)
    except ValueError as e:
        raise CliError(str(e))


def _line_range(value: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d+)\.\.(\d+)", value)
    if not m:
        raise CliError(f"--lines must be A..B, got {value!r}")
    return int(m.group(1)), int(m.group(2))


def cmd_note_write(args, root: str) -> Output:
    path = to_root_relative(args.file, root)
    first, last = _line_range(args.lines) if args.lines else (None, None)
    try:
        result = note_write.write(
            path, _block_text(args.expect), _block_text(args.text), first,
            last, args.create)
    except note_write.NoteWriteError as e:
        if e.current is None:
            raise CliError(str(e))
        return Output({"file": path, "current": e.current}, e.current,
                      error=str(e))
    data = {"file": path, "line": result.line, "end_line": result.end_line,
            "changed": result.changed}
    return Output(data, [f"{path}:{result.line}..{result.end_line}"
                         if result.changed else f"{path}: unchanged"])


def cmd_note(args, root: str) -> Output:
    if args.kind == "write":
        return cmd_note_write(args, root)
    if args.kind == "new":
        value = to_root_relative(args.path, root)
        template_name = args.template
    else:
        value = args.date
        template_name = None
    mode = _root_mode(root)
    try:
        result = note.create(args.kind, value, template_name=template_name,
                             render_only=args.render, mode=mode)
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


STATUS_CHARS = tuple(task_model.STATUS_CHARS)


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
    expected = " or ".join(("YYYY-MM-DD", *keywords))
    raise argparse.ArgumentTypeError(
        f"invalid value: {value!r} (expected {expected})")


def _due_value(value: str) -> str:
    return _date_value(value, ("undated", "none"))


def _start_value(value: str) -> str:
    return _date_value(value, ("none",))


def _day_value(value: str) -> str:
    return _date_value(value, ())


def _time_value(value: str) -> str:
    """Check a --time value: HH:MM (24-hour) or none; return HH:MM."""
    if value == "none":
        return value
    match = re.fullmatch(r"(\d{1,2}):(\d{2})", value)
    if match and int(match.group(1)) < 24 and int(match.group(2)) < 60:
        return f"{int(match.group(1)):02d}:{match.group(2)}"
    raise argparse.ArgumentTypeError(
        f"invalid value: {value!r} (expected HH:MM, 00:00 to 23:59, or none)")


def _recur_value(value: str) -> str:
    """Check a --recur value: a supported rule or none; return it trimmed."""
    value = value.strip()
    if value == "none" or parse_rule(value) is not None:
        return value
    raise argparse.ArgumentTypeError(
        f"invalid value: {value!r} (expected a rule like 'every 3 months', "
        "'every week when done', or 'every weekday', or none)")


def _text_value(value: str) -> str:
    """Check a --text value: one non-empty line; return it trimmed."""
    value = value.strip()
    if not value or re.search(r"[\r\n]", value):
        raise argparse.ArgumentTypeError("the text must be one non-empty line")
    return value


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
    if sep and path and line.isdigit():
        line_no = int(line)
    else:
        path, line_no = args.target, None
    path = to_root_relative(path, root)

    add_tags, remove_tags = args.add_tags or [], args.remove_tags or []
    both = ({canonical_tag(t).lower() for t in add_tags}
            & {canonical_tag(t).lower() for t in remove_tags})
    if both:
        raise CliError(f"{prog}: tag given to both --add-tag and --remove-tag: "
                       f"{', '.join(sorted(both))}")
    if (args.status is None and args.text is None and args.due is None and args.start is None
            and args.time is None and args.recur is None
            and not add_tags and not remove_tags):
        raise CliError(f"{prog}: give at least one of --status, --text, "
                       "--add-tag, --remove-tag, --due, --start, --time, "
                       "or --recur")

    try:
        if line_no is None:
            line_no = task_update.find_line(path, args.expect)
        result = task_update.update(
            path, line_no, args.expect, status=args.status, new_text=args.text,
            add_tags=add_tags, remove_tags=remove_tags, due=args.due, start=args.start,
            time=args.time, recur=args.recur, no_recur=args.no_recur,
            no_completed=args.no_completed)
    except task_update.TaskUpdateError as e:
        if e.current is None:
            raise CliError(str(e))
        return Output({"file": path, "line": line_no, "current": e.current},
                      error=str(e))

    out = Output({"file": path, "line": line_no, "old": result.old,
                  "new": result.new, "changed": result.changed,
                  "created": None, "ancestors": result.ancestors},
                 warnings=result.warnings)
    if result.created is not None:
        out.data["created"] = {"file": path, "line": result.created_line,
                               "text": result.created}
        out.text = [f"{path}:{line_no}", f"- {result.old}", f"+ {result.new}",
                    f"{path}:{result.created_line} created (the task is now "
                    f"on line {line_no + 1})", f"+ {result.created}"]
    elif result.changed:
        out.text = [f"{path}:{line_no}", f"- {result.old}", f"+ {result.new}"]
    else:
        out.text = [f"{path}:{line_no} unchanged"]
    for anc in result.ancestors:
        out.text += [f"{path}:{anc['line']} status", f"- {anc['old']}",
                     f"+ {anc['new']}"]
    return out


def cmd_task_show(args, root: str) -> Output:
    path, sep, line = args.target.rpartition(":")
    if not sep or not path or not line.isdigit():
        raise CliError("meta-notes task show: target must be <file>:<line>, "
                       f"got {args.target!r}")
    path = to_root_relative(path, root)
    try:
        data, lines, numbers = task_show.show(path, int(line), tree=args.tree)
    except task_show.TaskShowError as e:
        raise CliError(f"meta-notes task show: {e}")
    return Output(data, [f"{path}:{task_show.format_ranges(numbers)}", *lines])


def cmd_task_add(args, root: str) -> Output:
    path = to_root_relative(args.file, root)
    if args.under is None:
        if args.expect is not None:
            raise CliError("meta-notes task add: --expect is for --under")
    elif args.expect is None:
        raise CliError("meta-notes task add: --under needs --expect, the "
                       "parent line as last read")
    elif args.line is not None:
        raise CliError("meta-notes task add: --under and --line can't be "
                       "used together")
    try:
        if args.under is not None:
            result = task_write.add_subtask(
                path, args.under, args.expect, args.text, due=args.due,
                start=args.start, time=args.time, recur=args.recur,
                add_tags=args.add_tags or [])
        else:
            result = task_update.add(
                path, args.text, due=args.due, start=args.start,
                time=args.time, recur=args.recur,
                add_tags=args.add_tags or [], line_no=args.line)
    except task_update.TaskUpdateError as e:
        if e.current is None:
            raise CliError(f"meta-notes task add: {e}")
        return Output({"file": path, "line": args.under,
                       "current": e.current}, error=str(e))
    if args.under is not None:
        line, text, warnings = result.line, result.new[0], []
    else:
        line, text, warnings = result.created_line, result.new, result.warnings
    data = {"file": path, "line": line, "text": text}
    return Output(data, [f"{path}:{line} added", f"+ {text}"],
                  warnings=warnings)


def _block_text(value: str) -> str:
    """A multi-line argument; "-" reads it from standard input."""
    return sys.stdin.read() if value == "-" else value


def _write_output(path: str, result: task_write.WriteResult) -> Output:
    data = {"file": path, "line": result.line, "end_line": result.end_line,
            "old": result.old, "new": result.new, "changed": result.changed,
            "ancestors": result.ancestors}
    if not result.changed and not result.ancestors:
        return Output(data, [f"{path}:{result.line} unchanged"])
    text = [f"{path}:{result.line}", *(f"- {line}" for line in result.old),
            *(f"+ {line}" for line in result.new)]
    for anc in result.ancestors:
        text += [f"{path}:{anc['line']} status", f"- {anc['old']}",
                 f"+ {anc['new']}"]
    return Output(data, text)


def _task_write(args, root: str, prog: str, call) -> Output:
    path, sep, line = args.target.rpartition(":")
    if not sep or not path or not line.isdigit():
        raise CliError(f"{prog}: target must be <file>:<line>, got "
                       f"{args.target!r}")
    path = to_root_relative(path, root)
    try:
        result = call(path, int(line), _block_text(args.expect),
                      _block_text(args.text))
    except task_update.TaskUpdateError as e:
        if e.current is None:
            raise CliError(f"{prog}: {e}")
        return Output({"file": path, "line": int(line), "current": e.current},
                      error=str(e))
    return _write_output(path, result)


def cmd_task_notes(args, root: str) -> Output:
    return _task_write(args, root, "meta-notes task notes",
                       task_write.replace_notes)


def cmd_task_replace(args, root: str) -> Output:
    return _task_write(
        args, root, "meta-notes task replace",
        lambda path, line, expect, text: task_write.replace_node(
            path, line, expect, text, tree=args.tree))


def cmd_ceremony_status(args, root: str) -> Output:
    day = date.fromisoformat(args.date) if args.date else date.today()
    lines, data = ceremony.run(day, _root_mode(root))
    return Output(data, lines)


def cmd_planning(args, root: str) -> Output:
    try:
        lines, data = planning.run(args.date)
    except ValueError as e:
        raise CliError(str(e))
    return Output(data, lines)


def _clock_value(value: str) -> str:
    try:
        checkin.parse_time(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))
    return value


def _clock_value_with_tilde(value: str) -> str:
    """Validate a time value that may have a leading tilde (for time-log)."""
    try:
        # Strip tilde before parsing
        clean = value.lstrip('~')
        checkin.parse_time(clean)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))
    return value


def _minutes_value(value: str) -> int:
    if not value.isdigit() or int(value) < 1:
        raise argparse.ArgumentTypeError(
            f"invalid minutes: {value!r}; use a positive integer")
    return int(value)


def _checkin_day(args) -> date:
    return date.fromisoformat(args.date) if args.date else date.today()


def _checkin_output(data: dict) -> Output:
    return Output(data, checkin.format_status(data))


def cmd_checkin_status(args, root: str) -> Output:
    at = (checkin.parse_time(args.at) if args.at
          else datetime.now().time().replace(second=0, microsecond=0))
    return _checkin_output(checkin.status(_checkin_day(args), at))


def cmd_checkin_wait(args, root: str) -> Output:
    try:
        settings = config.table(config.load(root), "checkin")
    except ValueError as e:
        raise CliError(str(e))
    every = args.every
    mode = _root_mode(root)
    end = args.end or settings.get("end", hours.for_mode(mode).checkin_end)
    if every is None:
        every = settings.get("interval", checkin.DEFAULT_INTERVAL)
    try:
        if not isinstance(every, int) or isinstance(every, bool) or every < 1:
            raise ValueError("[checkin] interval must be a positive integer")
        end_time = checkin.parse_time(str(end))
    except ValueError as e:
        raise CliError(str(e))
    reason = checkin.wait(datetime.now(), every, end_time)[1]
    at = datetime.now().time().replace(second=0, microsecond=0)
    out = _checkin_output(checkin.status(_checkin_day(args), at))
    out.data["reason"] = reason
    out.text.insert(0, f"check-in {reason}")
    return out


def cmd_checkin_actual(args, root: str) -> Output:
    try:
        first = checkin.parse_time(args.time)
        last = checkin.parse_time(args.through) if args.through else first
        data = checkin.fill_actual(_checkin_day(args), first, last,
                                   args.text, args.force)
    except ValueError as e:
        raise CliError(str(e))
    text = [f"{data['note']}: wrote {', '.join(data['written']) or 'nothing'}"]
    if data["skipped"]:
        text.append(f"skipped (filled): {', '.join(data['skipped'])}")
    return Output(data, text)


def cmd_time_block_update(args, root: str) -> Output:
    path = to_root_relative(args.file, root)
    try:
        first = checkin.parse_time(args.time)
        last = checkin.parse_time(args.through) if args.through else first
        if args.kind == "replace":
            result = time_block.replace(path, first, last, args.expect,
                                        args.text)
        else:
            result = time_block.update(path, first, last, args.plan,
                                       args.actual, args.expect, args.create)
    except time_block.TimeBlockError as e:
        if e.current is None:
            raise CliError(str(e))
        return Output({"file": path, "current": e.current}, error=str(e))
    except ValueError as e:
        raise CliError(str(e))
    data = {"file": path, "written": result.written,
            "created": result.created}
    text = [f"{path}: wrote {', '.join(result.written)}"]
    if result.created:
        text.append(f"created: {', '.join(result.created)}")
    return Output(data, text)


def _time_log_output(path: str, call) -> Output:
    try:
        result = call()
    except time_log.TimeLogError as e:
        if e.current is None:
            raise CliError(str(e))
        return Output({"file": path, "current": e.current}, error=str(e))
    except ValueError as e:
        raise CliError(str(e))
    data = {"file": path, "written": result.written}
    text = [f"{path}: wrote {len(result.written)} "
            f"{'entry' if len(result.written) == 1 else 'entries'}"
            if result.written else f"{path}: deleted entries"]
    return Output(data, text, warnings=result.warnings)


def _parse_time_with_tilde(text: str | None) -> tuple[__import__('datetime').time, bool] | None:
	"""Parse a time string and return (time, has_tilde)."""
	if not text:
		return None
	text = text.strip()
	has_tilde = text.startswith('~')
	clean = text.lstrip('~')
	t = checkin.parse_time(clean)
	return t, has_tilde


def cmd_time_log_append(args, root: str) -> Output:
    path = to_root_relative(args.file, root)
    if args.start:
        start, start_tilde = _parse_time_with_tilde(args.start)
    else:
        start = datetime.now().time().replace(second=0, microsecond=0)
        start_tilde = False

    end_result = _parse_time_with_tilde(args.end)
    end = end_result[0] if end_result else None
    end_tilde = end_result[1] if end_result else False

    prev_start_result = _parse_time_with_tilde(args.prev_start)
    prev_start = prev_start_result[0] if prev_start_result else None
    prev_start_tilde = prev_start_result[1] if prev_start_result else False

    return _time_log_output(path, lambda: time_log.append(
        path, args.text, start, end, args.note,
        args.prev, prev_start,
        args.prev_open, args.close_prev, args.first,
        start_tilde=start_tilde, end_tilde=end_tilde, prev_start_tilde=prev_start_tilde))


def cmd_time_log_update(args, root: str) -> Output:
    path = to_root_relative(args.file, root)
    return _time_log_output(path, lambda: time_log.update(
        path, args.expect, args.text))


def cmd_projects(args, root: str) -> Output:
    lines, entries = projects.run(".", warnings_only=args.warnings)
    return Output({"projects": entries}, lines)


def cmd_project_brief(args, root: str) -> Output:
    since = date.fromisoformat(args.since) if args.since else None
    try:
        lines, data = brief.run(".", to_root_relative(args.path, root), since)
    except ValueError as e:
        raise CliError(str(e))
    return Output({"project": data}, lines)


def _optional_root_mode(args) -> tuple[str | None, str]:
    """The notes root, if any, and its mode ("work" with no root)."""
    # Works outside a notes root: an explicit --root or META_NOTES_ROOT must
    # still be valid, but finding no root by search isn't an error
    explicit = getattr(args, "root", None) or os.environ.get("META_NOTES_ROOT")
    if explicit:
        found = resolve_root(explicit, None, os.getcwd())
    else:
        found = find_root(os.getcwd(), os.environ.get("HOME"))
    if not found:
        return None, "work"
    try:
        return found, config.mode(found)
    except ValueError as e:
        raise CliError(str(e))


def cmd_conventions(args, root: None) -> Output:
    _, mode = _optional_root_mode(args)
    text = conventions.run(mode)
    return Output({"version": __version__, "mode": mode, "text": text,
                   "tag_aliases": conventions.tag_aliases_json(mode)},
                  [text.removesuffix("\n")])


def cmd_prime(args, root: None) -> Output:
    found, mode = _optional_root_mode(args)
    text = prime.run(found, mode=mode)
    return Output({"version": __version__, "root": found, "mode": mode,
                   "text": text},
                  [text.removesuffix("\n")])


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
    ("cache-readme", "created"): "Created cache README: {}",
    ("cache-readme", "overwritten"): "Overwrote cache README: {}",
    ("cache-readme", "exists"): "Cache README already exists: {}",
    ("claude-md", "found"): "Agents load the notes guide: {}",
    ("claude-md", "missing"):
        "Add this line to {} so agents load the notes guide:\n    "
        + init.PRIME_LINE + "\nOr start from the suggested CLAUDE.md:\n    cp "
        + shlex.quote(str(init.SUGGESTED_CLAUDE_MD)).replace("{", "{{")
        .replace("}", "}}") + " CLAUDE.md",
    ("gitignore", "created"): "Added to .gitignore: {}",
    ("gitignore", "exists"): "Already in .gitignore: {}",
    ("venv", "created"): "Created virtualenv: {}",
    ("venv", "rebuilt"): "Rebuilt virtualenv: {}",
    ("venv", "exists"):
        "Virtualenv already exists, left alone (--force rebuilds it): {}",
}


def cmd_init(args, root: None) -> Output:
    # init doesn't resolve a root: it initializes --root or the current
    # directory, and ignores META_NOTES_ROOT
    target = getattr(args, "root", None) or os.getcwd()
    try:
        result = init.init(target, force=args.force, home=os.environ.get("HOME"),
                           python=args.python, mode=args.mode)
    except init.InitError as e:
        raise CliError(str(e))

    items = [{"kind": i.kind, "path": i.path, "status": i.status}
             for i in result.items]
    suggested = shlex.quote(str(init.suggested_claude_md(result.mode)))
    text = [INIT_MESSAGES[(i.kind, i.status)].format(i.path)
            .replace(shlex.quote(str(init.SUGGESTED_CLAUDE_MD)), suggested)
            for i in result.items if (i.kind, i.status) in INIT_MESSAGES]
    text.append("Meta-notes initialization complete!")
    return Output({"root": result.root, "mode": result.mode, "items": items},
                  text, result.warnings)


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
                            "directory): folders, templates, sentinel, skills, "
                            "cache, .gitignore, and .venv")
    p.add_argument("--force", action="store_true",
                   help="overwrite templates and the cache README, replace "
                        "skill targets that aren't links, and rebuild .venv")
    p.add_argument("--python", metavar="PATH",
                   help="interpreter to build .venv with (default: python3 "
                        "on PATH); ignored when .venv exists, without --force")
    p.add_argument("--mode", metavar="MODE",
                   help="work or personal: written to a new .meta-notes "
                        "(personal also installs daily-personal.md); never "
                        "changes an existing root's mode")
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
    p.add_argument("--agenda", action="store_true",
                   help="Overdue, Today, then a section per day through the "
                        "horizon (5+ days and through next Monday; on Thu/Fri "
                        "through the Wednesday after); --undated adds undated tasks")
    p.add_argument("--through", metavar="DATE",
                   help="with --agenda: last day, in --date forms")
    p.set_defaults(handler=cmd_tasks)

    p = sub.add_parser("time", parents=[common],
                       help="time report for a day or period (same output as "
                            "time_report.py --date)")
    p.add_argument("--date", metavar="DATE",
                   help="YYYY-MM-DD for a day report; YYYY-MM-DD..YYYY-MM-DD, "
                        "YYYY-MM, YYYY-Qn, or YYYY for a period report "
                        "(default: today)")
    p.set_defaults(handler=cmd_time)

    p = sub.add_parser("changes", parents=[common],
                       help="list notes changed in a period, from git history "
                            "and uncommitted changes")
    p.add_argument("--date", metavar="PERIOD",
                   help="YYYY-MM-DD, YYYY-MM-DD..YYYY-MM-DD, YYYY-MM, YYYY-Qn, "
                        "or YYYY (default: today)")
    p.set_defaults(handler=cmd_changes)

    p = sub.add_parser("calendar", parents=[common],
                       help="agenda for a period from the newest Google "
                            "Calendar export in .meta-notes-cache/ics/")
    p.add_argument("--date", metavar="PERIOD",
                   help="YYYY-MM-DD, YYYY-MM-DD..YYYY-MM-DD, YYYY-MM, YYYY-Qn, "
                        "or YYYY (default: today)")
    p.add_argument("--ics", metavar="PATH",
                   help="read this .zip or .ics export instead")
    p.add_argument("--with", dest="with_names", metavar="NAME",
                   action="append", default=[],
                   help="only events with this organizer or attendee, by "
                        "word starts of name or email (repeatable)")
    p.add_argument("--search", metavar="TEXT", action="append", default=[],
                   help="only events whose title, location, or description "
                        "contains TEXT (repeatable)")
    p.set_defaults(handler=cmd_calendar)

    p = sub.add_parser("outlook", parents=[common],
                       help="the day's weather, sun and alerts for a place")
    p.add_argument("--date", type=_day_value, metavar="DAY",
                   help="YYYY-MM-DD (default: today)")
    p.add_argument("--location", metavar="PLACE",
                   help='"Mason, OH" or a ZIP code (default: location in '
                        "[outlook] in .meta-notes)")
    kinds = p.add_subparsers(dest="kind", metavar="KIND", parser_class=_Parser)
    for kind, text in (("weather", "only the Weather line"),
                       ("sun", "only the Sun line")):
        k = kinds.add_parser(kind, parents=[common], help=text)
        k.add_argument("--date", type=_day_value, metavar="DAY",
                       default=argparse.SUPPRESS)
        k.add_argument("--location", metavar="PLACE",
                       default=argparse.SUPPRESS)
    p.set_defaults(handler=cmd_outlook)

    p = sub.add_parser("cache", parents=[common],
                       help="manage .meta-notes-cache/")
    kinds = p.add_subparsers(dest="kind", metavar="KIND", parser_class=_Parser)
    kinds.required = True
    kinds.add_parser("clear", parents=[common],
                     help="delete the parsed calendars in "
                          ".meta-notes-cache/calendar/ (never the exports)")
    p.set_defaults(handler=cmd_cache_clear)

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
    k = kinds.add_parser("write", parents=[common],
                         help="replace a note's lines, only if they are "
                              "what you expect")
    k.add_argument("file", metavar="FILE",
                   help="the note, relative to the notes root")
    k.add_argument("--lines", metavar="A..B",
                   help="the lines replaced, 1-based and inclusive "
                        "(default: the whole file)")
    k.add_argument("--expect", required=True, metavar="TEXT",
                   help="those lines as last read, or - for stdin; nothing "
                        "is written if they differ")
    k.add_argument("--text", required=True, metavar="TEXT",
                   help="the new lines, or - for stdin (empty deletes)")
    k.add_argument("--create", action="store_true",
                   help="make the file if missing (with --expect '')")
    p.set_defaults(handler=cmd_note)

    p = sub.add_parser("task", parents=[common],
                       help="edit, add or read a task line, its notes and subtasks")
    kinds = p.add_subparsers(dest="kind", metavar="KIND", parser_class=_Parser)
    kinds.required = True
    k = kinds.add_parser("update", parents=[common],
                         help="edit one checkbox line's text, status, tags, and dates")
    k.add_argument("target", metavar="FILE[:LINE]",
                   help="the note, relative to the notes root, and the line "
                        "number (from 1); without it, the one line equal "
                        "to --expect")
    k.add_argument("--expect", required=True, metavar="TEXT",
                   help="the line as last read; nothing is written if it "
                        "differs (ignoring trailing whitespace); without "
                        ":LINE it finds the line, and must match exactly "
                        "one")
    k.add_argument("--status", choices=STATUS_CHARS, metavar="CHAR",
                   help="set the status character: ' ', x, X, >, -, ., o, "
                        "or O")
    k.add_argument("--text", type=_text_value, metavar="TEXT",
                   help="replace the task's words (tags among them), keeping "
                        "the checkbox, tags and dates after them")
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
    k.add_argument("--time", type=_time_value, metavar="TIME",
                   help="HH:MM (24-hour), written as ⏰ HH:MM, or none")
    k.add_argument("--recur", type=_recur_value, metavar="RULE",
                   help="set the 🔁 rule (like 'every 3 months') or none")
    k.add_argument("--no-recur", action="store_true",
                   help="mark a recurring task done without adding its next "
                        "occurrence")
    k.add_argument("--no-completed", action="store_true",
                   help="don't add a ✅ date when marking the task done "
                        "(not allowed on a recurring task)")
    p.set_defaults(handler=cmd_task_update)

    k = kinds.add_parser("show", parents=[common],
                         help="read one task with its notes, or its subtree")
    k.add_argument("target", metavar="FILE:LINE",
                   help="the note, relative to the notes root, and the "
                        "checkbox line's number (from 1)")
    k.add_argument("--tree", action="store_true",
                   help="include every subtask, nested, not just the line "
                        "and its notes")
    k.set_defaults(handler=cmd_task_show)

    k = kinds.add_parser("add", parents=[common],
                         help="add an open task line to a note")
    k.add_argument("file", metavar="FILE",
                   help="the note, relative to the notes root; it must exist")
    k.add_argument("text", metavar="TEXT",
                   help="the task's description, without the checkbox")
    k.add_argument("--due", type=_due_value, metavar="DATE",
                   help="YYYY-MM-DD or undated (a bare due emoji)")
    k.add_argument("--start", type=_day_value, metavar="DATE",
                   help="the 🛫 date, YYYY-MM-DD")
    k.add_argument("--time", type=_time_value, metavar="TIME",
                   help="HH:MM (24-hour), written as ⏰ HH:MM; needs --due")
    k.add_argument("--recur", type=_recur_value, metavar="RULE",
                   help="the 🔁 rule, like 'every 3 months'")
    k.add_argument("--tag", dest="add_tags", action="append",
                   type=_tag_value, metavar="TAG",
                   help="add a tag (repeatable)")
    k.add_argument("--line", type=int, metavar="N",
                   help="insert before line N (from 1); default: the end "
                        "of the file")
    k.add_argument("--under", type=int, metavar="N",
                   help="add a subtask of the task on line N (from 1), after "
                        "its notes and subtasks; needs --expect")
    k.add_argument("--expect", metavar="TEXT",
                   help="with --under, the parent line as last read; nothing "
                        "is written if it differs (ignoring trailing "
                        "whitespace)")
    k.set_defaults(handler=cmd_task_add)

    k = kinds.add_parser("notes", parents=[common],
                         help="replace one task's notes")
    k.add_argument("target", metavar="FILE:LINE",
                   help="the note and the checkbox line's number (from 1)")
    k.add_argument("--expect", required=True, metavar="TEXT",
                   help="the task's notes as last read (task show's lines "
                        "after the first; empty for none), or - for stdin; "
                        "nothing is written if they differ")
    k.add_argument("--text", required=True, metavar="TEXT",
                   help="the new notes, one per line as written, indented "
                        "deeper than the task; empty removes them; - reads "
                        "stdin")
    k.set_defaults(handler=cmd_task_notes)

    k = kinds.add_parser("replace", parents=[common],
                         help="replace a task's lines, or its whole subtree")
    k.add_argument("target", metavar="FILE:LINE",
                   help="the note and the checkbox line's number (from 1)")
    k.add_argument("--expect", required=True, metavar="TEXT",
                   help="the lines replaced as last read (what task show "
                        "prints), or - for stdin; nothing is written if "
                        "they differ")
    k.add_argument("--text", required=True, metavar="TEXT",
                   help="the new lines, as written; the first is a checkbox "
                        "line at the task's indent; - reads stdin")
    k.add_argument("--tree", action="store_true",
                   help="replace the whole subtree, not just the line and "
                        "its notes")
    k.set_defaults(handler=cmd_task_replace)

    p = sub.add_parser("ceremony", parents=[common],
                       help="read ceremony markers in daily and weekly notes")
    kinds = p.add_subparsers(dest="kind", metavar="KIND", parser_class=_Parser)
    kinds.required = True
    k = kinds.add_parser("status", parents=[common],
                         help="which ceremonies are done for a day and its "
                              "week")
    k.add_argument("--date", type=_day_value, metavar="DAY",
                   help="YYYY-MM-DD (default: today)")
    p.set_defaults(handler=cmd_ceremony_status)

    p = sub.add_parser("planning", parents=[common],
                       help="per day: daily note, planned, no-plan and "
                            "crossed-out Plan counts")
    p.add_argument("--date", metavar="PERIOD",
                   help="YYYY-MM-DD, YYYY-MM-DD..YYYY-MM-DD, YYYY-MM, "
                        "YYYY-Qn, or YYYY (default: today)")
    p.set_defaults(handler=cmd_planning)

    p = sub.add_parser("checkin", parents=[common],
                       help="stay-on-task check-ins and the Time Block's "
                            "Actual column")
    kinds = p.add_subparsers(dest="kind", metavar="KIND", parser_class=_Parser)
    kinds.required = True
    k = kinds.add_parser("status", parents=[common],
                         help="the Time Block's current row and unfilled "
                              "rows")
    k.add_argument("--date", type=_day_value, metavar="DAY",
                   help="YYYY-MM-DD (default: today)")
    k.add_argument("--at", type=_clock_value, metavar="TIME",
                   help="HH:MM (default: now)")
    k.set_defaults(handler=cmd_checkin_status)
    k = kinds.add_parser("wait", parents=[common],
                         help="sleep until a check-in is due, then report "
                              "the status and exit")
    k.add_argument("--every", type=_minutes_value, metavar="MINUTES",
                   help="minutes until the check-in (default: [checkin] "
                        "interval, or 30)")
    k.add_argument("--end", type=_clock_value, metavar="TIME",
                   help="end of the workday, HH:MM (default: [checkin] "
                        "end, or the mode's: 17:30 work, 21:00 personal)")
    k.add_argument("--date", type=_day_value, metavar="DAY",
                   help="YYYY-MM-DD (default: today)")
    k.set_defaults(handler=cmd_checkin_wait)
    k = kinds.add_parser("actual", parents=[common],
                         help="write text into Time Block Actual cells")
    k.add_argument("time", type=_clock_value, metavar="TIME",
                   help="the row, HH:MM or 9:15am")
    k.add_argument("text", metavar="TEXT", help="what happened")
    k.add_argument("--through", type=_clock_value, metavar="TIME",
                   help="also fill the rows through this one")
    k.add_argument("--force", action="store_true",
                   help="overwrite cells that aren't empty")
    k.add_argument("--date", type=_day_value, metavar="DAY",
                   help="YYYY-MM-DD (default: today)")
    k.set_defaults(handler=cmd_checkin_actual)

    p = sub.add_parser("time-block", parents=[common],
                       help="edit the Time Block's Plan and Actual cells")
    kinds = p.add_subparsers(dest="kind", metavar="KIND", parser_class=_Parser)
    kinds.required = True
    k = kinds.add_parser("update", parents=[common],
                         help="write Plan and/or Actual cells of rows found "
                              "by time")
    k.add_argument("file", metavar="FILE",
                   help="the note, relative to the notes root")
    k.add_argument("--time", required=True, type=_clock_value, metavar="TIME",
                   help="the row, HH:MM or 9:30am")
    k.add_argument("--through", type=_clock_value, metavar="TIME",
                   help="also cover the rows through this one")
    k.add_argument("--plan", metavar="TEXT", help="the Plan cell text")
    k.add_argument("--actual", metavar="TEXT", help="the Actual cell text")
    k.add_argument("--expect", metavar="TEXT",
                   help="the text a non-empty cell must hold to be "
                        "overwritten (default: cells must be empty)")
    k.add_argument("--create", action="store_true",
                   help="add the row when it's missing (not with --through)")
    k = kinds.add_parser("replace", parents=[common],
                         help="rewrite the rows from --time through "
                              "--through, all or nothing")
    k.add_argument("file", metavar="FILE",
                   help="the note, relative to the notes root")
    k.add_argument("--time", required=True, type=_clock_value, metavar="TIME",
                   help="the first row, HH:MM or 9:30am")
    k.add_argument("--through", required=True, type=_clock_value,
                   metavar="TIME", help="the last row")
    k.add_argument("--expect", required=True, metavar="ROWS",
                   help="the rows now there, one '| time | plan | actual |' "
                        "per line, compared cell by cell")
    k.add_argument("--text", required=True, metavar="ROWS",
                   help="the new rows, same form, padding optional")
    p.set_defaults(handler=cmd_time_block_update)

    p = sub.add_parser("time-log", parents=[common],
                       help="append and replace entries in the daily "
                            "note's ### Log")
    kinds = p.add_subparsers(dest="kind", metavar="KIND", parser_class=_Parser)
    kinds.required = True
    k = kinds.add_parser("append", parents=[common],
                         help="add one entry at the end of the log")
    k.add_argument("file", metavar="FILE",
                   help="the note, relative to the notes root")
    k.add_argument("--text", required=True, metavar="TEXT",
                   help="the new entry's header line, '- text #tags'")
    k.add_argument("--start", type=_clock_value_with_tilde, metavar="TIME",
                   help="HH:MM or 9:30am (default: now); prefix with ~ for approximately")
    k.add_argument("--end", type=_clock_value_with_tilde, metavar="TIME",
                   help="the new entry's end (default: open); prefix with ~ for approximately")
    k.add_argument("--note", action="append", default=[], metavar="TEXT",
                   help="an extra '* note' line; repeat for more")
    k.add_argument("--prev", metavar="LINE",
                   help="the last entry's header line, exactly")
    k.add_argument("--prev-start", type=_clock_value_with_tilde, metavar="TIME",
                   help="the last entry's start")
    k.add_argument("--prev-open", action="store_true",
                   help="the last entry has no end")
    k.add_argument("--close-prev", action="store_true",
                   help="write the last entry's end as --start "
                        "(needs --prev-open)")
    k.add_argument("--first", action="store_true",
                   help="the log is empty (instead of the --prev options)")
    k.set_defaults(handler=cmd_time_log_append)
    k = kinds.add_parser("update", parents=[common],
                         help="replace a run of whole entries with other "
                              "entries")
    k.add_argument("file", metavar="FILE",
                   help="the note, relative to the notes root")
    k.add_argument("--expect", required=True, metavar="TEXT",
                   help="the exact text of the whole entries to replace")
    k.add_argument("--text", required=True, metavar="TEXT",
                   help="the replacement entries (empty deletes)")
    k.set_defaults(handler=cmd_time_log_update)

    p = sub.add_parser("projects", parents=[common],
                       help="list projects with status, latest date, last "
                            "review, and warnings")
    p.add_argument("--warnings", action="store_true",
                   help="only projects with at least one warning")
    p.set_defaults(handler=cmd_projects)

    p = sub.add_parser("project", parents=[common],
                       help="report on one project")
    kinds = p.add_subparsers(dest="kind", metavar="KIND", parser_class=_Parser)
    kinds.required = True
    k = kinds.add_parser("brief", parents=[common],
                         help="a project's fields, files, tasks, dates, and "
                              "warnings")
    k.add_argument("path",
                   help="a note or folder directly in project/ or "
                        "archive/project/ (.md and trailing / optional)")
    k.add_argument("--since", type=_day_value, metavar="DAY",
                   help="list tasks completed on or after YYYY-MM-DD "
                        "(default: 90 days ago)")
    p.set_defaults(handler=cmd_project_brief)

    p = sub.add_parser("ui", parents=[common],
                       help="start, stop and open the meta-notes-ui server")
    kinds = p.add_subparsers(dest="kind", metavar="KIND", parser_class=_Parser)
    kinds.required = True
    launch = argparse.ArgumentParser(add_help=False)
    launch.add_argument("--path", metavar="DIR",
                        help="the meta-notes-ui clone (default: [ui] path)")
    launch.add_argument("--host", help="address to bind (default: [ui] host)")
    launch.add_argument("--port", type=int,
                        help="port to listen on (default: [ui] port)")
    for kind, handler, extra, text in (
            ("start", cmd_ui_start, [launch],
             "start the server detached; print its URL with the token"),
            ("stop", cmd_ui_stop, [], "stop the server"),
            ("status", cmd_ui_status, [],
             "report whether the server is running"),
            ("url", cmd_ui_url, [],
             "print the running server's URL with the token"),
            ("open", cmd_ui_open, [launch],
             "start the server if needed and open it in the browser")):
        k = kinds.add_parser(kind, parents=[common, *extra], help=text)
        k.set_defaults(handler=handler)

    p = sub.add_parser("conventions", parents=[common],
                       help="print the note syntax and editing conventions "
                            "skills follow, as markdown")
    p.set_defaults(handler=cmd_conventions, resolves_root=False)

    p = sub.add_parser("prime", parents=[common],
                       help="print a guide to the notes root for an agent: "
                            "structure, plan notes, projects, archive, "
                            "commands, and conventions")
    p.set_defaults(handler=cmd_prime, resolves_root=False)

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
