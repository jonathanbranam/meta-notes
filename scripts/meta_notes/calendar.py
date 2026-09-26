"""
Calendar agenda from a Google Calendar export.

The export is a .zip of one .ics per calendar, or a single .ics, saved into
<root>/.meta-notes-cache/ics/. The newest is read (or --ics), the calendars
selected in .meta-notes are parsed once into a pruned, deduplicated cache in
.meta-notes-cache/calendar/, and occurrences in the period are listed per
day in the display timezone.

This is the only module that uses third-party libraries (icalendar and
recurring_ical_events, installed in the notes root's .venv by init). They're
imported when the command runs, so the rest of the CLI works without them.
"""

import hashlib
import json
import os
import re
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone, tzinfo
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from period import parse_period
from meta_notes import config

CACHE_DIR = ".meta-notes-cache"
ICS_DIR = f"{CACHE_DIR}/ics"
CALENDAR_DIR = f"{CACHE_DIR}/calendar"
EXPORT_SUFFIXES = (".ics", ".zip")
KEEP_EXPORTS = 5
HORIZON_DAYS = 30
# Pruning compares dates in each event's own timezone; this margin keeps
# events that could still reach the horizon in the display timezone
HORIZON_MARGIN = timedelta(days=2)
DEFAULT_STALE_DAYS = 3
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
EXPORT_HELP = ("export from Google Calendar (Settings, Import & export, "
               "Export) and save the .zip into {}")


# Settings

@dataclass
class Settings:
    email: str | None
    tz: tzinfo
    stale_days: int
    calendars: list[str] | None


def _local_timezone() -> tzinfo:
    """The system timezone, by IANA name when it can be found."""
    candidates = []
    if os.environ.get("TZ"):
        candidates.append(os.environ["TZ"].removeprefix(":"))
    link = os.path.realpath("/etc/localtime")
    if "zoneinfo/" in link:
        candidates.append(link.split("zoneinfo/", 1)[1])
    for name in candidates:
        try:
            return ZoneInfo(name)
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return datetime.now().astimezone().tzinfo


def load_settings(root: str) -> Settings:
    """
    Read the [calendar] table from .meta-notes.

    Raises:
        ValueError: If .meta-notes isn't valid TOML or a setting is invalid.
    """
    table = config.table(config.load(root), "calendar")
    where = "[calendar] in .meta-notes"

    email = table.get("email")
    if email is not None and not isinstance(email, str):
        raise ValueError(f"email in {where} must be a string")

    name = table.get("timezone")
    if name is None:
        tz = _local_timezone()
    elif not isinstance(name, str):
        raise ValueError(f"timezone in {where} must be a string")
    else:
        try:
            tz = ZoneInfo(name)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError(f"Unknown timezone in {where}: {name!r} (use an "
                             "IANA name such as America/New_York)") from None

    stale_days = table.get("stale_days", DEFAULT_STALE_DAYS)
    if (not isinstance(stale_days, int) or isinstance(stale_days, bool)
            or stale_days < 0):
        raise ValueError(f"stale_days in {where} must be a whole number of days")

    calendars = table.get("calendars")
    if calendars is not None and (
            not isinstance(calendars, list)
            or not all(isinstance(c, str) for c in calendars)):
        raise ValueError(f"calendars in {where} must be a list of names")

    return Settings(email or None, tz, stale_days, calendars)


def _selection(calendars: list[str] | None) -> list[str] | None:
    """The calendars setting as recorded in a cache entry."""
    return None if calendars is None else sorted({c.lower() for c in calendars})


class NotInstalled(ValueError):
    """The calendar libraries can't be imported."""


def _libraries(root: str):
    """Import icalendar and recurring_ical_events, or raise NotInstalled."""
    try:
        import icalendar
        import recurring_ical_events
    except ImportError:
        fix = ("`meta-notes init --force` (.venv exists but lacks them)"
               if os.path.isdir(os.path.join(root, ".venv"))
               else "`meta-notes init`")
        raise NotInstalled(
            "Calendar support is not installed in this notes root; run "
            f"{fix} in {root}") from None
    return icalendar, recurring_ical_events


# Exports

@dataclass
class Export:
    path: Path
    size: int
    mtime_ns: int

    @classmethod
    def of(cls, path: Path) -> "Export":
        st = path.stat()
        return cls(path, st.st_size, st.st_mtime_ns)

    @property
    def is_zip(self) -> bool:
        return self.path.suffix.lower() == ".zip"


def find_exports(ics_dir: Path) -> list[Export]:
    """Exports directly in ics_dir, newest first by modification time."""
    if not ics_dir.is_dir():
        return []
    found = [Export.of(p) for p in ics_dir.iterdir()
             if p.suffix.lower() in EXPORT_SUFFIXES and p.is_file()]
    return sorted(found, key=lambda e: (e.mtime_ns, e.path.name), reverse=True)


@dataclass
class Member:
    """One calendar in an export."""
    name: str          # X-WR-CALNAME, or the file name without .ics
    stem: str
    member: str | None  # the zip member; None for a plain .ics


_CALNAME = re.compile(rb"^X-WR-CALNAME(?:;[^:\r\n]*)?:(.*?)\r?$", re.M)


def _header_name(head: bytes) -> str | None:
    """X-WR-CALNAME from the part of a calendar before its first event."""
    head = head.split(b"BEGIN:VEVENT", 1)[0]
    head = re.sub(rb"\r?\n[ \t]", b"", head)
    match = _CALNAME.search(head)
    if not match:
        return None
    name = match.group(1).decode("utf-8", "replace")
    name = re.sub(r"\\([\\;,])", r"\1", name).strip()
    return name or None


def _read_head(f) -> bytes:
    """Read a calendar stream up to its first event, or to the end."""
    head = b""
    while True:
        chunk = f.read(65536)
        head += chunk
        if not chunk or b"BEGIN:VEVENT" in head:
            return head


def list_members(export: Export) -> list[Member]:
    """
    The calendars in an export, named without parsing their events.

    Raises:
        ValueError: If the file can't be read or a zip holds no .ics.
    """
    path = export.path
    try:
        if not export.is_zip:
            with open(path, "rb") as f:
                name = _header_name(_read_head(f))
            return [Member(name or path.stem, path.stem, None)]
        members = []
        with zipfile.ZipFile(path) as zf:
            for info in zf.infolist():
                if info.is_dir() or not info.filename.lower().endswith(".ics"):
                    continue
                stem = Path(info.filename).stem
                with zf.open(info) as f:
                    name = _header_name(_read_head(f))
                members.append(Member(name or stem, stem, info.filename))
    except (OSError, zipfile.BadZipFile) as e:
        raise ValueError(f"Cannot read calendar export {path}: {e}") from None
    if not members:
        raise ValueError(f"Calendar export {path} holds no .ics calendars")
    return members


def select_members(members: list[Member], calendars: list[str] | None,
                   is_zip: bool) -> list[Member]:
    """
    The members the calendars setting selects: all when unset or for a
    plain .ics, else those whose name or file stem matches, ignoring case.

    Raises:
        ValueError: If a configured name matches no calendar.
    """
    if calendars is None or not is_zip:
        return members
    wanted = {c.lower() for c in calendars}
    unknown = sorted(c for c in calendars
                     if not any(c.lower() in (m.name.lower(), m.stem.lower())
                                for m in members))
    if unknown:
        available = ", ".join(m.name for m in members)
        raise ValueError(
            f"No calendar named {', '.join(unknown)} in the export (calendars "
            f"in [calendar] in .meta-notes); available: {available}")
    return [m for m in members
            if m.name.lower() in wanted or m.stem.lower() in wanted]


def _read_member(export: Export, member: Member) -> bytes:
    try:
        if member.member is None:
            return export.path.read_bytes()
        with zipfile.ZipFile(export.path) as zf:
            return zf.read(member.member)
    except (OSError, zipfile.BadZipFile) as e:
        raise ValueError(f"Cannot read calendar export {export.path}: {e}") from None


# Pruning and deduplicating events

def _day(value) -> date:
    return value.date() if isinstance(value, datetime) else value


def _as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _event_end(event):
    start = event["DTSTART"].dt
    if "DTEND" in event:
        return event["DTEND"].dt
    if "DURATION" in event:
        return start + event["DURATION"].dt
    return start


def ends_before(event, cutoff: date) -> bool:
    """
    Whether an event can't reach cutoff or later: a one-off event that
    ends before it, a series whose every RRULE has an UNTIL before it, or an
    override whose RECURRENCE-ID and DTSTART are both before it. COUNT and
    endless series, and anything with RDATE, are kept.
    """
    if "DTSTART" not in event:
        return False
    if "RECURRENCE-ID" in event:
        return (_day(event["RECURRENCE-ID"].dt) < cutoff
                and _day(event["DTSTART"].dt) < cutoff)
    rrules = _as_list(event.get("RRULE"))
    if "RDATE" in event:
        return False
    if rrules:
        for rule in rrules:
            until = rule.get("UNTIL")
            if not until or _day(until[0]) >= cutoff:
                return False
        return True
    return _day(_event_end(event)) < cutoff


def _instant(value) -> float:
    """A LAST-MODIFIED or RECURRENCE-ID value as a sortable timestamp."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.timestamp()
    if isinstance(value, date):
        return datetime.combine(value, time(), timezone.utc).timestamp()
    return float("-inf")


def _version(event) -> tuple[int, float]:
    try:
        sequence = int(event.get("SEQUENCE", 0))
    except (TypeError, ValueError):
        sequence = 0
    modified = event.get("LAST-MODIFIED")
    return sequence, _instant(modified.dt) if modified is not None else float("-inf")


def _occurrence_key(event) -> tuple:
    rid = event.get("RECURRENCE-ID")
    uid = str(event["UID"]) if "UID" in event else id(event)
    return uid, None if rid is None else _instant(rid.dt)


def prepare(calendar, cutoff: date | None):
    """
    Drop events that end before cutoff (none when None), and keep only the
    latest version, by (SEQUENCE, LAST-MODIFIED), of each (UID,
    RECURRENCE-ID). VTIMEZONEs and calendar properties are kept. Changes
    calendar in place and returns it.
    """
    others = []
    latest = {}
    for component in calendar.subcomponents:
        if component.name != "VEVENT":
            others.append(component)
            continue
        if cutoff is not None and ends_before(component, cutoff):
            continue
        key = _occurrence_key(component)
        if key not in latest or _version(component) > _version(latest[key]):
            latest[key] = component
    calendar.subcomponents[:] = others + list(latest.values())
    return calendar


# The cache

def cache_key(export: Export, loaded: list[str]) -> str:
    parts = [export.path.name, str(export.size), str(export.mtime_ns),
             *sorted(loaded)]
    return hashlib.sha256("\0".join(parts).encode()).hexdigest()[:16]


def read_entries(cal_dir: Path) -> dict[str, dict]:
    """Cache entries with both files, by key, from their .json records."""
    entries = {}
    if not cal_dir.is_dir():
        return entries
    for meta_path in cal_dir.glob("*.json"):
        key = meta_path.stem
        if not (cal_dir / f"{key}.ics").is_file():
            continue
        try:
            meta = json.loads(meta_path.read_text())
        except (OSError, ValueError):
            continue
        if isinstance(meta, dict) and isinstance(meta.get("mtime_ns"), int):
            entries[key] = meta
    return entries


def _load_entry(ical, cal_dir: Path, key: str, meta: dict) -> list[tuple]:
    data = (cal_dir / f"{key}.ics").read_bytes()
    calendars = ical.Calendar.from_ical(data, multiple=True) if data.strip() else []
    names = meta.get("loaded") or []
    if len(names) != len(calendars):
        raise ValueError(f"Cached calendar {CALENDAR_DIR}/{key}.ics is damaged; "
                         "run `meta-notes cache clear`")
    return list(zip(names, calendars))


def _build_entry(ical, export: Export, members: list[Member],
                 selected: list[Member], cal_dir: Path, key: str,
                 calendars: list[str] | None, today: date) -> list[tuple]:
    horizon = today - timedelta(days=HORIZON_DAYS)
    loaded = []
    for member in selected:
        calendar = ical.Calendar.from_ical(_read_member(export, member))
        loaded.append((member.name, prepare(calendar, horizon - HORIZON_MARGIN)))

    cal_dir.mkdir(parents=True, exist_ok=True)
    (cal_dir / f"{key}.ics").write_bytes(
        b"".join(calendar.to_ical() for _, calendar in loaded))
    meta = {
        "key": key,
        "source": str(export.path.resolve()),
        "name": export.path.name,
        "size": export.size,
        "mtime_ns": export.mtime_ns,
        "calendars": _selection(calendars) if export.is_zip else None,
        "available": [m.name for m in members],
        "loaded": [m.name for m in selected],
        "horizon": horizon.isoformat(),
        "built": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    # Written last: an entry counts only once its .json exists
    (cal_dir / f"{key}.json").write_text(json.dumps(meta, indent=2) + "\n")
    return loaded


def prune(root: str, exports: list[Export], calendars: list[str] | None,
          used: str | None) -> list[str]:
    """
    Delete exports in ics/ beyond the newest KEEP_EXPORTS, and cache entries
    not built from a kept export with the current calendars setting (or,
    with no exports, all but the newest). The entry `used` is always kept.

    Returns:
        Deleted paths, relative to root.
    """
    deleted = []
    kept = exports[:KEEP_EXPORTS]
    for export in exports[KEEP_EXPORTS:]:
        export.path.unlink()
        deleted.append(os.path.relpath(export.path, root))

    cal_dir = Path(root, CALENDAR_DIR)
    if not cal_dir.is_dir():
        return deleted
    entries = read_entries(cal_dir)

    def matches(meta: dict, export: Export) -> bool:
        setting = _selection(calendars) if export.is_zip else None
        return (meta.get("name") == export.path.name
                and meta.get("size") == export.size
                and meta.get("mtime_ns") == export.mtime_ns
                and meta.get("calendars") == setting)

    if kept:
        keep = {key for key, meta in entries.items()
                if any(matches(meta, export) for export in kept)}
    elif entries:
        keep = {max(entries, key=lambda k: entries[k]["mtime_ns"])}
    else:
        keep = set()
    if used:
        keep.add(used)

    for path in sorted(cal_dir.iterdir()):
        if path.is_file() and path.name.split(".", 1)[0] not in keep:
            path.unlink()
            deleted.append(os.path.relpath(path, root))
    return deleted


def clear(root: str) -> list[str]:
    """
    Delete every file in the cache's calendar/ folder.

    Returns:
        Deleted paths, relative to root.
    """
    cal_dir = Path(root, CALENDAR_DIR)
    if not cal_dir.is_dir():
        return []
    deleted = []
    for path in sorted(cal_dir.iterdir()):
        if path.is_file() or path.is_symlink():
            path.unlink()
            deleted.append(os.path.relpath(path, root))
    return deleted


# The agenda

MAX_ATTENDEES = 20
RESPONSES = {"ACCEPTED": "yes", "TENTATIVE": "maybe",
             "NEEDS-ACTION": "no-reply", "DECLINED": "no"}
NOT_PEOPLE = ("ROOM", "RESOURCE")


def _address(value) -> str:
    """An ORGANIZER or ATTENDEE address without mailto:."""
    text = str(value).strip()
    return text[7:] if text.lower().startswith("mailto:") else text


def _param(value, name: str) -> str:
    params = getattr(value, "params", None) or {}
    return str(params.get(name, "")).strip()


def _declined(event, email: str | None) -> bool:
    if not email:
        return False
    return any(_address(a).lower() == email.lower()
               and _param(a, "PARTSTAT").upper() == "DECLINED"
               for a in _as_list(event.get("ATTENDEE")))


def attendance(event, email: str | None, calendar_name: str) -> dict:
    """
    The organizer, whether the event is the user's own, the user's
    response, and the attendees who are people (the first MAX_ATTENDEES).
    """
    organizer = event.get("ORGANIZER")
    attendees = _as_list(event.get("ATTENDEE"))
    me = email.lower() if email else None

    response = None
    people = []
    for attendee in attendees:
        address = _address(attendee)
        answer = RESPONSES.get(_param(attendee, "PARTSTAT").upper())
        if me and address.lower() == me and answer != "no":
            response = answer
        if _param(attendee, "CUTYPE").upper() in NOT_PEOPLE:
            continue
        people.append({"name": _param(attendee, "CN") or None,
                       "email": address, "response": answer})

    if organizer is not None:
        mine = bool(me) and _address(organizer).lower() == me
        organizer = {"name": _param(organizer, "CN") or None,
                     "email": _address(organizer)}
    else:
        mine = bool(me) and not attendees and calendar_name.lower() == me

    return {"mine": mine, "organizer": organizer, "response": response,
            "attendee_count": len(people),
            "attendees": people[:MAX_ATTENDEES]}


def _local(value, tz: tzinfo) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=tz)
    return value.astimezone(tz)


def agenda(rie, calendars: list[tuple], start: date, end: date, tz: tzinfo,
           email: str | None) -> dict[date, list[dict]]:
    """
    Occurrences overlapping each day from start to end in tz, leaving out
    cancelled and declined events. All-day events appear on each day they
    cover; timed events on the day they start (or the first day, when they
    started earlier). All-day first, then by start time. Each event
    carries its attendance (see attendance()).
    """
    days = {start + timedelta(days=n): [] for n in range((end - start).days + 1)}
    low = datetime.combine(start, time(), tz)
    high = datetime.combine(end + timedelta(days=1), time(), tz)

    for name, calendar in calendars:
        # One day of slack each side; the overlap check below is exact
        # (.between() can return an event outside the range)
        query = rie.of(calendar, skip_bad_series=True)
        for event in query.between(start - timedelta(days=1),
                                   end + timedelta(days=2)):
            if str(event.get("STATUS", "")).upper() == "CANCELLED":
                continue
            if _declined(event, email):
                continue
            title = str(event.get("SUMMARY") or "").strip() or "(no title)"
            location = str(event.get("LOCATION") or "").strip() or None
            people = attendance(event, email, name)
            first = event["DTSTART"].dt
            last = _event_end(event)

            if not isinstance(first, datetime):
                last = _day(last)
                if last <= first:
                    last = first + timedelta(days=1)
                entry = {"start": first.isoformat(),
                         "end": (last - timedelta(days=1)).isoformat(),
                         "all_day": True, "title": title,
                         "location": location, "calendar": name, **people,
                         "_sort": (0, 0.0, title)}
                day = max(first, start)
                while day < last and day <= end:
                    days[day].append(entry)
                    day += timedelta(days=1)
                continue

            first = _local(first, tz)
            last = _local(last, tz) if isinstance(last, datetime) else first
            if not (first < high and (last > low or (last == first and first >= low))):
                continue
            days[max(first.date(), start)].append({
                "start": first.isoformat(), "end": last.isoformat(),
                "all_day": False, "title": title, "location": location,
                "calendar": name, **people,
                "_sort": (1, first.timestamp(), title)})

    for events in days.values():
        events.sort(key=lambda e: e["_sort"])
    return {day: [{k: v for k, v in e.items() if k != "_sort"} for e in events]
            for day, events in days.items()}


def agenda_lines(days: dict[date, list[dict]], multiple: bool) -> list[str]:
    lines = []
    for day, events in days.items():
        if lines:
            lines.append("")
        lines.append(f"## {day.isoformat()} {WEEKDAYS[day.weekday()]}")
        for event in events:
            if event["all_day"]:
                when = "all day"
            else:
                when = (f"{datetime.fromisoformat(event['start']):%H:%M}-"
                        f"{datetime.fromisoformat(event['end']):%H:%M}")
            line = f"{when}  {event['title']}"
            # Only responses that matter for planning; the rest is in JSON
            if not event["mine"] and event["response"] in ("maybe", "no-reply"):
                line += f" [{event['response']}]"
            if multiple:
                line += f" ({event['calendar']})"
            lines.append(line)
    return lines


# The command

def run(root: str, period: str | None = None, ics: str | None = None,
        today: date | None = None) -> tuple[list[str], dict, list[str]]:
    """
    Build the agenda for a period.

    Args:
        root: The notes root (absolute).
        period: A --date value; None for today.
        ics: An export to read instead of the newest in ics/.
        today: Today's date in the display timezone (default: now).

    Returns:
        (text lines, JSON fields: days, source, pruned; warnings)

    Raises:
        ValueError: On invalid config or period, a missing or unreadable
            export, an unknown calendar name, or missing libraries.
    """
    settings = load_settings(root)
    tz = settings.tz
    today = today or datetime.now(tz).date()
    start, end = parse_period(period, today)
    ical, rie = _libraries(root)

    warnings = []
    if not settings.email:
        warnings.append("email is not set in [calendar] in .meta-notes, so "
                        "declined events are listed")

    ics_dir = Path(root, ICS_DIR)
    cal_dir = Path(root, CALENDAR_DIR)
    cal_dir.mkdir(parents=True, exist_ok=True)
    exports = find_exports(ics_dir)
    entries = read_entries(cal_dir)

    if ics is not None:
        path = Path(os.path.expanduser(ics))
        if not path.is_file():
            raise ValueError(f"Calendar export not found: {ics}")
        export = Export.of(path)
    else:
        export = exports[0] if exports else None

    used = None
    if export is not None:
        members = list_members(export)
        selected = select_members(members, settings.calendars, export.is_zip)
        key = cache_key(export, [m.name for m in selected])
        meta = entries.get(key)
        horizon = (date.fromisoformat(meta["horizon"]) if meta
                   else today - timedelta(days=HORIZON_DAYS))
        if start < horizon:
            # Before the cache's horizon: read the whole export
            loaded = [(m.name, prepare(ical.Calendar.from_ical(
                _read_member(export, m)), None)) for m in selected]
            cached = False
            used = key if meta else None
        elif meta:
            loaded = _load_entry(ical, cal_dir, key, meta)
            cached = True
            used = key
        else:
            loaded = _build_entry(ical, export, members, selected, cal_dir,
                                  key, settings.calendars, today)
            cached = False
            used = key
        source_path = str(export.path.resolve())
        mtime_ns = export.mtime_ns
        available = [m.name for m in members]
    else:
        if not entries:
            raise ValueError("No calendar export found; "
                             + EXPORT_HELP.format(ics_dir))
        used = max(entries, key=lambda k: entries[k]["mtime_ns"])
        meta = entries[used]
        loaded = _load_entry(ical, cal_dir, used, meta)
        cached = True
        source_path = meta.get("source") or meta.get("name") or ""
        mtime_ns = meta["mtime_ns"]
        available = meta.get("available") or []
        warnings.append(
            f"The calendar export {meta.get('name')} is missing from "
            f"{ICS_DIR}, so the calendar cached from it was used; to update, "
            + EXPORT_HELP.format(ics_dir))
        horizon = date.fromisoformat(meta["horizon"])
        if start < horizon:
            warnings.append(
                f"Events before {horizon.isoformat()} may be missing: the "
                "cached calendar leaves them out and its export is missing")

    exported = datetime.fromtimestamp(mtime_ns / 1e9, tz)
    age = (today - exported.date()).days
    if age > settings.stale_days:
        warnings.append(f"The calendar export is {age} days old; for a current "
                        "agenda, " + EXPORT_HELP.format(ics_dir))

    pruned = prune(root, exports, settings.calendars, used)

    days = agenda(rie, loaded, start, end, tz, settings.email)
    names = [name for name, _ in loaded]
    lines = agenda_lines(days, len(names) > 1)
    data = {
        "days": [{"date": day.isoformat(), "events": events}
                 for day, events in days.items()],
        "source": {"path": source_path,
                   "exported": exported.isoformat(timespec="seconds"),
                   "age_days": age, "cached": cached,
                   "available": available, "loaded": names},
        "pruned": pruned,
    }
    return lines, data, warnings
