"""
Planning record: per day in a period, whether the daily note exists, whether
the day was planned, and how many Time Block Plan cells are `no plan` or
crossed out (wrapped in single tildes). Nothing is written.
"""

import re
from datetime import date, timedelta

import period
from meta_notes import ceremony, checkin, note

NO_PLAN = "no plan"
# A Plan cell in single tildes: ~text~, not ~~text~~
_CROSSED_OUT = re.compile(r"^~(?!~).*(?<!~)~$|^~[^~]~$")


def day_record(day: date) -> dict:
    """
    The planning record for one day's daily note, relative to the current
    directory (the notes root).

    Returns:
        Dict with `date`, `note`, `note_exists`, `planned` (the
        `plan complete` marker is checked, or a Time Block row has a Plan
        other than `no plan`), `no_plan` and `crossed_out` counts.
    """
    path = note.periodic_note("daily", day)[0]
    lines = checkin._read_lines(path)
    record = {"date": day.isoformat(), "note": path,
              "note_exists": lines is not None, "planned": False,
              "no_plan": 0, "crossed_out": 0}
    if lines is None:
        return record
    try:
        rows = checkin.time_block_rows(lines)
    except ValueError:
        rows = []
    plans = [r.plan for r in rows]
    record["no_plan"] = sum(p.lower() == NO_PLAN for p in plans)
    record["crossed_out"] = sum(bool(_CROSSED_OUT.match(p)) for p in plans)
    record["planned"] = (ceremony.find_marker(lines, "plan complete").done
                         or any(p and p.lower() != NO_PLAN for p in plans))
    return record


def report(text: str | None) -> dict:
    """The planning record for each day of a --date period (default today)."""
    start, end = period.parse_period(text)
    days = [day_record(start + timedelta(n))
            for n in range((end - start).days + 1)]
    return {"start": start.isoformat(), "end": end.isoformat(), "days": days,
            "totals": {"days": len(days),
                       "notes": sum(d["note_exists"] for d in days),
                       "planned": sum(d["planned"] for d in days),
                       "no_plan": sum(d["no_plan"] for d in days),
                       "crossed_out": sum(d["crossed_out"] for d in days)}}


def format_report(data: dict) -> list[str]:
    """Text lines: one per day, then the totals."""
    lines = []
    for d in data["days"]:
        if not d["note_exists"]:
            lines.append(f"{d['date']}: no note")
            continue
        lines.append(f"{d['date']}: {'planned' if d['planned'] else 'not planned'}, "
                     f"{d['no_plan']} no plan, {d['crossed_out']} crossed out")
    t = data["totals"]
    lines.append(f"Total: {t['notes']} of {t['days']} days with a note, "
                 f"{t['planned']} planned, {t['no_plan']} no plan, "
                 f"{t['crossed_out']} crossed out")
    return lines


def run(text: str | None) -> tuple[list[str], dict]:
    """Planning record as (text lines, JSON data)."""
    data = report(text)
    return format_report(data), data
