"""
Unit tests for time_report module.
"""

import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from time_report import (
    _daily_note_path,
    _load_days,
    build_day_report,
    build_period_report,
    build_report,
    format_day_report,
    format_period_report,
    format_report,
    generate_report,
    main,
)


def write_note(root: Path, d: date, log: list[str], block: list[str] | None = None) -> Path:
    """Write a daily note with a ### Log section (and optional time block)."""
    path = Path(_daily_note_path(str(root), d))
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {d.isoformat()}", ""]
    if block is not None:
        lines += ["### Time Block", "", "| Time    | Plan | Actual |",
                  "|---------|------|--------|"] + block + [""]
    lines += ["### Log", ""] + log + ["", "### Notes", ""]
    path.write_text("\n".join(lines))
    return path


def entry(text: str, start: str | None, end: str | None) -> list[str]:
    """Time log lines for one entry."""
    lines = [f"- {text}"]
    if start:
        lines.append(f"  * start: {start}")
    if end:
        lines.append(f"  * end:   {end}")
    return lines


TUESDAY = date(2026, 9, 22)
DAY_LOG = (entry("June DMC Connect #meeting", "15:00", "15:50")
           + entry("Tanul & Melissa", "16:00", "16:40")
           + entry("review #horz position paper", "16:40", None)
           + entry("Chris Sparks fraud ring preso #mtg", "17:00", "17:30"))


# Tests for _load_days function

def test_load_days_present_and_missing(tmp_path):
    """Each day is read from its note; a day without a note is None."""
    write_note(tmp_path, TUESDAY, entry("work #code", "09:00", "10:00"))

    days = _load_days(str(tmp_path), date(2026, 9, 21), date(2026, 9, 22))

    assert [d for d, _ in days] == [date(2026, 9, 21), TUESDAY]
    assert days[0][1] is None
    assert len(days[1][1]) == 1
    assert days[1][1][0].activity == "work"


def test_load_days_monday_to_sunday(tmp_path):
    """A Mon-Sun span yields all seven days."""
    days = _load_days(str(tmp_path), date(2026, 9, 21), date(2026, 9, 27))

    assert [d.weekday() for d, _ in days] == list(range(7))


# Tests for build_period_report and format_period_report functions

def test_build_period_report_weekend_entries_counted(tmp_path):
    """Saturday's time counts in the total and its tag."""
    write_note(tmp_path, TUESDAY, entry("sync #meeting", "09:00", "10:00"))
    write_note(tmp_path, date(2026, 9, 26), entry("hack #code", "10:00", "11:00"))

    data = build_period_report(str(tmp_path), date(2026, 9, 21), date(2026, 9, 27))

    assert data['total_minutes'] == 120
    assert data['work_minutes'] == 120
    assert data['by_tag'] == {'code': 60, 'meeting': 60}
    assert data['highlighted'] == [{'label': 'all meetings', 'minutes': 60},
                                   {'label': 'code', 'minutes': 60}]
    saturday = data['days'][5]
    assert saturday == {'date': '2026-09-26', 'weekday': 'Sat', 'logged': True,
                        'work_minutes': 60, 'earliest': '10:00', 'latest': '11:00',
                        'span_minutes': 60}


def test_build_period_report_aliases_combined(tmp_path):
    """#mtg and #meeting across days total under meeting."""
    write_note(tmp_path, TUESDAY, entry("a #mtg", "09:00", "09:30"))
    write_note(tmp_path, date(2026, 9, 23), entry("b #meeting", "09:00", "10:00"))

    data = build_period_report(str(tmp_path), date(2026, 9, 21), date(2026, 9, 27))
    text = "\n".join(format_period_report(data))

    assert data['by_tag'] == {'meeting': 90}
    assert "- meeting:          1 hr 30 min" in text
    assert "mtg" not in text


def test_format_period_report_layout(tmp_path):
    """Heading, Total Time with highlights, alphabetical tags, and day items."""
    write_note(tmp_path, TUESDAY,
               entry("hire #recruiting", "08:00", "08:22")
               + entry("sync #meeting", "09:00", "11:25")
               + entry("paper #horz", "11:25", "12:00")
               + entry("walk #break", "12:00", "12:20"))

    data = build_period_report(str(tmp_path), date(2026, 9, 21), date(2026, 9, 27))
    lines = format_period_report(data)

    assert lines[:2] == ["# Time Tracking Report", ""]
    i = lines.index("## Summary for 2026-09-21 to 2026-09-27")
    assert lines[i + 2:i + 9] == [
        "### Total Time",
        "",
        "- work duration:    3 hr 22 min",
        "- total duration:   3 hr 42 min",
        "- all meetings:     2 hr 25 min",
        "- recruiting:       22 min",
        "",
    ]
    j = lines.index("### Time per tag")
    assert lines[j + 2:j + 6] == ["- break:            20 min",
                                  "- horz:             35 min",
                                  "- meeting:          2 hr 25 min",
                                  "- recruiting:       22 min"]
    k = lines.index("### Day Summaries")
    assert lines[k + 2:k + 4] == ["- 2026-09-21 Mon", "  * (no log)"]
    assert lines[k + 4:k + 9] == ["- 2026-09-22 Tue",
                                  "  * work duration:    3 hr 22 min",
                                  "  * earliest time:    08:00",
                                  "  * latest time:      12:20",
                                  "  * total time:       4 hr 20 min"]


def test_build_period_report_day_without_log(tmp_path):
    """A note with no log entries shows (no log)."""
    write_note(tmp_path, TUESDAY, [])

    data = build_period_report(str(tmp_path), TUESDAY, TUESDAY)

    assert data['days'][0]['logged'] is False
    assert "  * (no log)" in format_period_report(data)


def test_build_period_report_day_without_times(tmp_path):
    """Entries with no parseable times (template placeholders) are no log."""
    write_note(tmp_path, TUESDAY, entry("placeholder", "HH:MM", "HH:MM"))

    data = build_period_report(str(tmp_path), TUESDAY, TUESDAY)

    assert data['days'][0]['logged'] is False
    assert "  * (no log)" in format_period_report(data)


def test_build_period_report_month(tmp_path):
    """A month has one day item per day."""
    data = build_period_report(str(tmp_path), date(2026, 9, 1), date(2026, 9, 30))
    lines = format_period_report(data)

    assert len(data['days']) == 30
    assert "## Summary for 2026-09-01 to 2026-09-30" in lines
    assert lines.count("  * (no log)") == 30


# Tests for build_day_report and format_day_report functions

def test_format_day_report_section_order(tmp_path):
    """Log, Total Time, tags, work split, plan adherence, then the week."""
    path = write_note(tmp_path, TUESDAY, DAY_LOG,
                      ["|  3:00pm | meeting | meeting #mtg |"])

    lines = format_day_report(build_day_report(str(tmp_path), TUESDAY, str(path)))
    headings = [line for line in lines if line.startswith('#')]

    assert headings == ["# Time Tracking Report", "## Time Log", "### Total Time",
                        "## Time Log Summary", "### Time by Tag",
                        "### Work vs Non-Work", "## Plan Adherence",
                        "### Summary (1 blocks)",
                        "## Summary for 2026-09-21 to 2026-09-27",
                        "### Total Time", "### Time per tag", "### Day Summaries"]
    assert lines[-1] != ""


def test_format_day_report_entries(tmp_path):
    """Entries, a gap, and a missing end are listed in file order."""
    path = write_note(tmp_path, TUESDAY, DAY_LOG)

    lines = format_day_report(build_day_report(str(tmp_path), TUESDAY, str(path)))
    i = lines.index("## Time Log")

    assert lines[i + 2:i + 27] == [
        "- June DMC Connect #meeting",
        "  * start: 15:00",
        "  * end:   15:50",
        "  * time:  50 min",
        "  * tags:  meeting",
        "- *GAP of 10 min*",
        "  * start: 15:50",
        "  * end:   16:00",
        "- Tanul & Melissa",
        "  * start: 16:00",
        "  * end:   16:40",
        "  * time:  40 min",
        "- review #horz position paper",
        "  * start: 16:40",
        "  * end:   *MISSING END TIME*",
        "  * tags:  horz",
        "- Chris Sparks fraud ring preso #mtg",
        "  * start: 17:00",
        "  * end:   17:30",
        "  * time:  30 min",
        "  * tags:  meeting",
        "",
        "### Total Time",
        "",
        "- work duration:    2 hr 0 min",
    ]


def test_format_day_report_overlap_and_long_entry(tmp_path):
    """An overlap shows the earlier end first; over an hour shows hours."""
    path = write_note(tmp_path, TUESDAY,
                      entry("deep work", "08:00", "09:25")
                      + entry("slides #code", "09:10", "09:40")
                      + entry("*placeholder*", None, "10:00"))

    text = "\n".join(format_day_report(build_day_report(str(tmp_path), TUESDAY, str(path))))

    assert "  * time:  1 hr 25 min" in text
    assert "- *Overlap of 15 min*\n  * start: 09:25\n  * end:   09:10" in text
    assert "  * start: *MISSING START TIME*\n  * end:   10:00" in text


def test_format_day_report_missing_time(tmp_path):
    """Unlogged time above 10 minutes is reported in Total Time."""
    path = write_note(tmp_path, TUESDAY,
                      entry("a", "07:08", "12:00") + entry("b", "13:37", "17:51"))

    lines = format_day_report(build_day_report(str(tmp_path), TUESDAY, str(path)))
    i = lines.index("### Total Time")

    assert lines[i + 2:i + 8] == ["- work duration:    9 hr 6 min",
                                  "- total duration:   9 hr 6 min",
                                  "- earliest time:    07:08",
                                  "- latest time:      17:51",
                                  "- total time:       10 hr 43 min",
                                  "- *missing time*:   1 hr 37 min"]


def test_format_day_report_no_log(tmp_path):
    """A note without a log still has plan adherence and the week."""
    path = write_note(tmp_path, TUESDAY, [])

    lines = format_day_report(build_day_report(str(tmp_path), TUESDAY, str(path)))

    assert "No time log entries found." in lines
    assert "### Total Time" not in lines[:lines.index("## Plan Adherence")]
    assert "## Plan Adherence" in lines
    assert "No time block entries found." in lines
    assert "## Summary for 2026-09-21 to 2026-09-27" in lines


def test_build_day_report_data(tmp_path):
    """The day report dict has the JSON fields."""
    path = write_note(tmp_path, TUESDAY, DAY_LOG)

    data = build_day_report(str(tmp_path), TUESDAY, str(path))

    assert data['kind'] == 'day'
    assert data['start'] == data['end'] == '2026-09-22'
    assert data['file'] == 'plan/daily/26-Q3/2026-09-22 Tue.md'
    assert data['entries'][0] == {'kind': 'entry', 'line': 5,
                                  'text': 'June DMC Connect #meeting',
                                  'start': '15:00', 'end': '15:50',
                                  'minutes': 50, 'tags': ['meeting']}
    assert data['entries'][1] == {'kind': 'gap', 'minutes': 10,
                                  'start': '15:50', 'end': '16:00'}
    assert data['by_tag'] == {'meeting': 80}
    assert data['plan_adherence'] is None
    assert data['week']['start'] == '2026-09-21'
    assert len(data['week']['days']) == 7


def test_generate_report_wraps_day_report(tmp_path):
    """generate_report renders the same day report from a file path."""
    path = write_note(tmp_path, TUESDAY, DAY_LOG)

    expected = "\n".join(format_day_report(build_day_report(str(tmp_path), TUESDAY, str(path))))

    assert generate_report(str(path)) == expected


# Tests for build_report function

def test_build_report_single_day(tmp_path):
    """A single-day period is the day report."""
    write_note(tmp_path, TUESDAY, DAY_LOG)

    assert build_report(str(tmp_path), "2026-09-22")['kind'] == 'day'


def test_build_report_default_today(tmp_path):
    """No date means today."""
    write_note(tmp_path, TUESDAY, DAY_LOG)

    assert build_report(str(tmp_path), None, today=TUESDAY)['start'] == '2026-09-22'


def test_build_report_period(tmp_path):
    """A longer period is the period report."""
    data = build_report(str(tmp_path), "2026-09")

    assert data['kind'] == 'period'
    assert (data['start'], data['end']) == ('2026-09-01', '2026-09-30')
    assert format_report(data)[2] == "## Summary for 2026-09-01 to 2026-09-30"


def test_build_report_missing_note(tmp_path):
    """A single day without a note names the expected path."""
    with pytest.raises(ValueError, match="Daily note not found: .*2026-09-22 Tue.md"):
        build_report(str(tmp_path), "2026-09-22")


def test_build_report_invalid_date(tmp_path):
    """An invalid period raises the date-period error."""
    with pytest.raises(ValueError, match="Invalid date: 2026-02-30"):
        build_report(str(tmp_path), "2026-02-30")


# Tests for main function

def test_main_date(tmp_path, monkeypatch, capsys):
    """--date finds the note under the current directory."""
    write_note(tmp_path, TUESDAY, DAY_LOG)
    monkeypatch.chdir(tmp_path)

    assert main(["--date", "2026-09-22"]) == 0
    out = capsys.readouterr().out

    assert "File: 2026-09-22 Tue.md" in out
    assert "- *GAP of 10 min*" in out


def test_main_file_matches_date(tmp_path, monkeypatch, capsys):
    """A file path prints the same report as --date."""
    write_note(tmp_path, TUESDAY, DAY_LOG)
    monkeypatch.chdir(tmp_path)

    main(["--date", "2026-09-22"])
    by_date = capsys.readouterr().out
    main(["plan/daily/26-Q3/2026-09-22 Tue.md"])
    by_file = capsys.readouterr().out

    assert by_file == by_date


def test_main_default_today(tmp_path, monkeypatch, capsys):
    """No file or --date reports today."""
    write_note(tmp_path, date.today(), entry("work", "09:00", "10:00"))
    monkeypatch.chdir(tmp_path)

    assert main([]) == 0
    assert f"File: {date.today().strftime('%Y-%m-%d %a')}.md" in capsys.readouterr().out


def test_main_period(tmp_path, monkeypatch, capsys):
    """A period prints the period report."""
    monkeypatch.chdir(tmp_path)

    assert main(["--date", "2026-09-21..2026-09-27"]) == 0
    assert "## Summary for 2026-09-21 to 2026-09-27" in capsys.readouterr().out


def test_main_missing_note(tmp_path, monkeypatch, capsys):
    """A single day without a note fails with the path."""
    monkeypatch.chdir(tmp_path)

    assert main(["--date", "2026-09-22"]) == 1
    captured = capsys.readouterr()

    assert captured.out == ""
    assert "Daily note not found: plan/daily/26-Q3/2026-09-22 Tue.md" in captured.err


def test_main_file_and_date(tmp_path, monkeypatch, capsys):
    """A file and --date together are an error."""
    path = write_note(tmp_path, TUESDAY, DAY_LOG)
    monkeypatch.chdir(tmp_path)

    assert main([str(path), "--date", "2026-09-22"]) == 1
    captured = capsys.readouterr()

    assert captured.out == ""
    assert "not both" in captured.err


def test_main_invalid_date(tmp_path, monkeypatch, capsys):
    """An invalid --date prints the date-period error."""
    monkeypatch.chdir(tmp_path)

    assert main(["--date", "2026-02-30"]) == 1
    captured = capsys.readouterr()

    assert captured.out == ""
    assert "Error: Invalid date: 2026-02-30" in captured.err


def test_main_script_exit_code(tmp_path):
    """Run as a script, errors exit non-zero."""
    result = subprocess.run([sys.executable, str(scripts_dir / 'time_report.py'),
                             "--date", "2026-02-30"],
                            cwd=tmp_path, capture_output=True, text=True)

    assert result.returncode == 1
    assert "Invalid date" in result.stderr
