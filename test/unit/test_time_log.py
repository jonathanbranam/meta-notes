"""
Unit tests for scripts/meta_notes/time_log.py
"""

import json
import sys
from datetime import time
from pathlib import Path

import pytest

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import cli, time_log

NOTE = """# Daily Note

### Log

- Work
  * start: 09:45
  * end:   13:00
- Lunch #personal
  * start: 13:00
  * end:   13:30
  * ate soup
- Review #dev
  * start: 13:30

### Time Block

| Time    | Plan |
"""


def make_note(tmp_path, text=NOTE):
    path = tmp_path / "2026-10-01 Thu.md"
    path.write_text(text)
    return str(path)


def lines_of(path):
    return Path(path).read_text().splitlines()


def append(path, **kwargs):
    args = dict(text="- Next #dev", start=time(14, 0), prev="- Review #dev",
                prev_start=time(13, 30), prev_open=True)
    args.update(kwargs)
    return time_log.append(path, **args)


# Tests for append

def test_time_log_append_close_prev(tmp_path):
    path = make_note(tmp_path)
    result = append(path, close_prev=True, end=time(14, 30),
                    notes=["a note", "another"])
    out = lines_of(path)
    assert out[11:18] == [
        "- Review #dev", "  * start: 13:30", "  * end:   14:00",
        "- Next #dev", "  * start: 14:00", "  * end:   14:30",
        "  * a note"]
    assert out[18] == "  * another"
    assert out[19] == ""
    assert result.warnings == []


def test_time_log_append_open_entry(tmp_path):
    path = make_note(tmp_path)
    append(path, start=time(14, 0), close_prev=True)
    assert "  * end:   14:00" in lines_of(path)
    assert lines_of(path)[14:16] == ["- Next #dev", "  * start: 14:00"]


def test_time_log_append_replaces_end_placeholder(tmp_path):
    text = NOTE.replace("  * start: 13:30\n",
                        "  * start: 13:30\n  * end:   HH:MM\n")
    path = make_note(tmp_path, text)
    append(path, close_prev=True)
    assert lines_of(path).count("  * end:   14:00") == 1
    assert "HH:MM" not in Path(path).read_text()


def test_time_log_append_prev_closed(tmp_path):
    path = make_note(tmp_path, NOTE.replace(
        "  * start: 13:30\n", "  * start: 13:30\n  * end:   14:00\n"))
    result = time_log.append(path, "- Next", time(14, 0),
                             prev="- Review #dev", prev_start=time(13, 30))
    assert result.written and result.warnings == []


def test_time_log_append_guard_mismatch_writes_nothing(tmp_path):
    path = make_note(tmp_path)
    for kwargs in ({"prev": "- Other"}, {"prev_start": time(9, 0)},
                   {"prev_open": False}):
        with pytest.raises(time_log.TimeLogError) as e:
            append(path, **kwargs)
        assert "- Review #dev" in e.value.current[0]["text"]
    assert Path(path).read_text() == NOTE


def test_time_log_append_prev_open_but_ended(tmp_path):
    path = make_note(tmp_path, NOTE.replace(
        "  * start: 13:30\n", "  * start: 13:30\n  * end:   14:00\n"))
    with pytest.raises(time_log.TimeLogError, match="already has an end"):
        append(path)


def test_time_log_append_gap_warning(tmp_path):
    path = make_note(tmp_path, NOTE.replace(
        "  * start: 13:30\n", "  * start: 13:30\n  * end:   14:00\n"))
    result = time_log.append(path, "- Next", time(14, 10),
                             prev="- Review #dev", prev_start=time(13, 30))
    assert result.warnings == ["*Gap of 10 min* before 'Next'"]
    assert "- Next" in Path(path).read_text()


def test_time_log_append_overlap_warning(tmp_path):
    path = make_note(tmp_path, NOTE.replace(
        "  * start: 13:30\n", "  * start: 13:30\n  * end:   14:00\n"))
    result = time_log.append(path, "- Next", time(13, 50),
                             prev="- Review #dev", prev_start=time(13, 30))
    assert result.warnings == ["*Overlap of 10 min* before 'Next'"]


def test_time_log_append_first(tmp_path):
    path = make_note(tmp_path, "### Log\n\n### Time Block\n")
    time_log.append(path, "- Start", time(8, 0), first=True)
    assert lines_of(path) == ["### Log", "", "- Start", "  * start: 08:00",
                              "", "### Time Block"]


def test_time_log_append_first_fails_with_entries(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_log.TimeLogError, match="already has entries"):
        time_log.append(path, "- Start", time(8, 0), first=True)


def test_time_log_append_close_prev_needs_open(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_log.TimeLogError, match="--prev-open"):
        append(path, close_prev=True, prev_open=False)


def test_time_log_append_bad_text(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_log.TimeLogError, match="starting with"):
        append(path, text="Next")
    with pytest.raises(time_log.TimeLogError, match="before"):
        append(path, end=time(13, 0))


def test_time_log_append_no_log(tmp_path):
    path = make_note(tmp_path, "# Note\n")
    with pytest.raises(time_log.TimeLogError, match="no '### Log'"):
        append(path)


# Tests for update

WORK = "- Work\n  * start: 09:45\n  * end:   13:00"


def test_time_log_update_split(tmp_path):
    path = make_note(tmp_path)
    result = time_log.update(
        path, WORK,
        "- Work\n  * start: 09:45\n  * end:   11:00\n"
        "- Reviewed PRs #dev\n  * start: 11:00\n  * end:   13:00")
    assert lines_of(path)[4:10] == [
        "- Work", "  * start: 09:45", "  * end:   11:00",
        "- Reviewed PRs #dev", "  * start: 11:00", "  * end:   13:00"]
    assert lines_of(path)[10] == "- Lunch #personal"
    assert result.warnings == []


def test_time_log_update_merge(tmp_path):
    path = make_note(tmp_path)
    expect = WORK + "\n- Lunch #personal\n  * start: 13:00\n" \
        "  * end:   13:30\n  * ate soup"
    time_log.update(path, expect,
                    "- Work\n  * start: 09:45\n  * end:   13:30")
    assert lines_of(path)[4:8] == ["- Work", "  * start: 09:45",
                                   "  * end:   13:30", "- Review #dev"]


def test_time_log_update_delete(tmp_path):
    path = make_note(tmp_path)
    result = time_log.update(path, WORK, "")
    assert lines_of(path)[3:6] == ["", "- Lunch #personal",
                                   "  * start: 13:00"]
    assert result.written == []
    assert result.warnings == []


def test_time_log_update_no_match_lists_likely(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_log.TimeLogError) as e:
        time_log.update(path, "- Work\n  * start: 09:45\n  * end:   12:00",
                        "- Work\n  * start: 09:45\n  * end:   12:30")
    assert "matches no entries" in str(e.value)
    assert "~   * end:   13:00" in e.value.current[0]["text"]
    assert Path(path).read_text() == NOTE


def test_time_log_update_two_matches(tmp_path):
    entry = "- Same\n  * start: 09:00\n  * end:   10:00\n"
    path = make_note(tmp_path, "### Log\n\n" + entry + entry)
    with pytest.raises(time_log.TimeLogError, match="matches 2"):
        time_log.update(path, entry, "")


def test_time_log_update_expect_must_be_whole_entries(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_log.TimeLogError):
        time_log.update(path, "  * start: 09:45", "")
    with pytest.raises(time_log.TimeLogError):
        time_log.update(path, "", "")


def test_time_log_update_invalid_text_writes_nothing(tmp_path):
    path = make_note(tmp_path)
    bad = ["Work", "- Work\n  * end:   13:00", "- Work\n  * start: 9:99",
           "- Work\n  * start: 09:45\n  * end:   xx",
           "- Work\n  * start: 09:45\n  * end:   09:00",
           "- Work\n  * start: 09:45",  # open, but not the last entry
           "- Work\n  * start: 09:45\n\n- More\n  * start: 10:00"]
    for text in bad:
        with pytest.raises(time_log.TimeLogError):
            time_log.update(path, WORK, text)
    assert Path(path).read_text() == NOTE


def test_time_log_update_last_entry_may_be_open(tmp_path):
    path = make_note(tmp_path)
    time_log.update(path, "- Review #dev\n  * start: 13:30",
                    "- Review #dev\n  * start: 13:35")
    assert "  * start: 13:35" in lines_of(path)


def test_time_log_update_warns_on_gap_and_overlap(tmp_path):
    path = make_note(tmp_path)
    result = time_log.update(path, WORK,
                             "- Work\n  * start: 09:45\n  * end:   12:30")
    assert result.warnings == ["*Gap of 30 min* before 'Lunch #personal'"]
    path = make_note(tmp_path)
    result = time_log.update(path, WORK,
                             "- Work\n  * start: 09:45\n  * end:   13:10")
    assert result.warnings == ["*Overlap of 10 min* before "
                               "'Lunch #personal'"]


def test_time_log_update_only_touches_log(tmp_path):
    path = make_note(tmp_path)
    time_log.update(path, WORK, "- Work\n  * start: 09:45\n  * end:   12:00")
    assert lines_of(path)[-4:] == NOTE.splitlines()[-4:]


# Tests for the CLI

def run_cli(tmp_path, capsys, *argv):
    code = cli.main(["--root", str(tmp_path), "--json", "time-log", *argv])
    return code, json.loads(capsys.readouterr().out)


def test_time_log_cli_append_json(tmp_path, capsys):
    path = make_note(tmp_path)
    code, out = run_cli(tmp_path, capsys, "append", path, "--text", "- Next",
                        "--start", "2:00pm", "--prev", "- Review #dev",
                        "--prev-start", "13:30", "--prev-open",
                        "--close-prev", "--note", "hi")
    assert code == 0 and out["ok"] and out["written"][0]["line"] == 15
    assert "  * hi" in lines_of(path)


def test_time_log_cli_append_mismatch_json_has_current(tmp_path, capsys):
    path = make_note(tmp_path)
    code, out = run_cli(tmp_path, capsys, "append", path, "--text", "- Next",
                        "--start", "14:00", "--prev", "- Nope",
                        "--prev-start", "13:30", "--prev-open")
    assert code == 1 and not out["ok"]
    assert out["current"][0]["text"].startswith("- Review #dev")


def test_time_log_cli_update_json_warnings(tmp_path, capsys):
    path = make_note(tmp_path)
    code, out = run_cli(tmp_path, capsys, "update", path, "--expect", WORK,
                        "--text", "- Work\n  * start: 09:45\n  * end:   12:30")
    assert code == 0 and out["warnings"] == [
        "*Gap of 30 min* before 'Lunch #personal'"]


def test_time_log_cli_update_invalid_is_error(tmp_path, capsys):
    path = make_note(tmp_path)
    code, out = run_cli(tmp_path, capsys, "update", path, "--expect", WORK,
                        "--text", "bad")
    assert code == 1 and not out["ok"]
