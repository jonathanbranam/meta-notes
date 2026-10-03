"""
Unit tests for scripts/meta_notes/time_block.py
"""

import json
import sys
from datetime import time
from pathlib import Path

import pytest

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import cli, time_block

NOTE = """# Daily Note

### Time Block

| Time    | Plan                 | Actual          |
| ------- | -------------------- | --------------- |
|  8:45am |                      |                 |
|  9:00am | mtg: standup         |                 |
|  9:15am |                      |                 |
|  9:30am |                      |                 |
| 10:00am |                      |                 |

### Log

|  1:00pm | not a block row      |                 |
"""


def make_note(tmp_path, text=NOTE):
    path = tmp_path / "daily.md"
    path.write_text(text)
    return str(path)


def lines_of(path):
    return Path(path).read_text().splitlines()


# Tests for update

def test_time_block_update_plan_padded(tmp_path):
    path = make_note(tmp_path)
    result = time_block.update(path, time(9, 15), time(9, 15), plan="write")
    assert result.written == ["9:15am"]
    assert lines_of(path)[8] == "|  9:15am | write                |                 |"


def test_time_block_update_plan_and_actual(tmp_path):
    path = make_note(tmp_path)
    time_block.update(path, time(9, 15), time(9, 15), plan="a", actual="b")
    assert lines_of(path)[8] == "|  9:15am | a                    | b               |"


def test_time_block_update_sanitizes_text(tmp_path):
    path = make_note(tmp_path)
    time_block.update(path, time(9, 15), time(9, 15), plan="a|b\nc")
    assert "| a/b c " in lines_of(path)[8]


def test_time_block_update_range_covers_rows(tmp_path):
    path = make_note(tmp_path)
    result = time_block.update(path, time(9, 15), time(9, 30), plan="x")
    assert result.written == ["9:15am", "9:30am"]
    assert "| x " in lines_of(path)[9]


def test_time_block_update_nonempty_without_expect_fails(tmp_path):
    path = make_note(tmp_path)
    before = Path(path).read_text()
    with pytest.raises(time_block.TimeBlockError) as e:
        time_block.update(path, time(9, 0), time(9, 0), plan="new")
    assert e.value.current == [
        {"time": "9:00am", "column": "plan", "text": "mtg: standup"}]
    assert "mtg: standup" in str(e.value)
    assert Path(path).read_text() == before


def test_time_block_update_expect_matches(tmp_path):
    path = make_note(tmp_path)
    time_block.update(path, time(9, 0), time(9, 0), plan="new",
                      expect=" mtg: standup ")
    assert "| new " in lines_of(path)[7]


def test_time_block_update_range_mismatch_writes_nothing(tmp_path):
    path = make_note(tmp_path)
    before = Path(path).read_text()
    with pytest.raises(time_block.TimeBlockError) as e:
        time_block.update(path, time(8, 45), time(9, 15), plan="x")
    assert [m["time"] for m in e.value.current] == ["9:00am"]
    assert Path(path).read_text() == before


def test_time_block_update_missing_slot(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_block.TimeBlockError, match="time slot not found"):
        time_block.update(path, time(9, 45), time(9, 45), plan="x")


def test_time_block_update_missing_through_slot(tmp_path):
    path = make_note(tmp_path)
    before = Path(path).read_text()
    with pytest.raises(time_block.TimeBlockError, match="time slot not found"):
        time_block.update(path, time(9, 15), time(9, 45), plan="x")
    assert Path(path).read_text() == before


def test_time_block_update_no_time_block(tmp_path):
    path = make_note(tmp_path, "# Note\n")
    with pytest.raises(time_block.TimeBlockError, match="no Time Block"):
        time_block.update(path, time(9, 0), time(9, 0), plan="x")


def test_time_block_update_ragged_table(tmp_path):
    ragged = NOTE.replace("|  9:15am |                      |",
                          "|  9:15am |                       |")
    path = make_note(tmp_path, ragged)
    with pytest.raises(time_block.TimeBlockError, match="ragged.*9:15am"):
        time_block.update(path, time(9, 30), time(9, 30), plan="x")
    assert Path(path).read_text() == ragged


def test_time_block_update_text_too_wide(tmp_path):
    path = make_note(tmp_path)
    before = Path(path).read_text()
    with pytest.raises(time_block.TimeBlockError, match="20 .*21|21.*20"):
        time_block.update(path, time(9, 15), time(9, 15), plan="x" * 21)
    assert Path(path).read_text() == before


def test_time_block_update_text_fills_column(tmp_path):
    path = make_note(tmp_path)
    time_block.update(path, time(9, 15), time(9, 15), plan="x" * 20)
    assert lines_of(path)[8] == f"|  9:15am | {'x' * 20} |                 |"


def test_time_block_update_wide_actual_writes_nothing(tmp_path):
    path = make_note(tmp_path)
    before = Path(path).read_text()
    with pytest.raises(time_block.TimeBlockError):
        time_block.update(path, time(9, 15), time(9, 15), plan="ok",
                          actual="y" * 40)
    assert Path(path).read_text() == before


def test_time_block_update_requires_plan_or_actual(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_block.TimeBlockError, match="--plan or --actual"):
        time_block.update(path, time(9, 0), time(9, 0))


# Tests for create

def test_time_block_update_create_inserts_in_order(tmp_path):
    path = make_note(tmp_path)
    result = time_block.update(path, time(9, 45), time(9, 45), plan="new",
                               create=True)
    assert result.created == ["9:45am"]
    assert lines_of(path)[10] == "|  9:45am | new                  |                 |"
    assert "10:00am" in lines_of(path)[11]


def test_time_block_update_create_before_first_and_after_last(tmp_path):
    path = make_note(tmp_path)
    time_block.update(path, time(7, 0), time(7, 0), plan="flight", create=True)
    time_block.update(path, time(10, 15), time(10, 15), plan="end", create=True)
    out = lines_of(path)
    assert out[6] == "|  7:00am | flight               |                 |"
    assert out[12].startswith("| 10:15am | end ")
    assert out[13] == ""


def test_time_block_update_create_existing_row_is_noop(tmp_path):
    path = make_note(tmp_path)
    result = time_block.update(path, time(9, 15), time(9, 15), plan="x",
                               create=True)
    assert result.created == []
    assert len(lines_of(path)) == len(NOTE.splitlines())


def test_time_block_update_create_with_through_rejected(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_block.TimeBlockError, match="--create"):
        time_block.update(path, time(9, 0), time(9, 15), plan="x",
                          create=True)


def test_time_block_update_create_failure_writes_nothing(tmp_path):
    path = make_note(tmp_path)
    before = Path(path).read_text()
    with pytest.raises(time_block.TimeBlockError):
        time_block.update(path, time(7, 0), time(7, 0), plan="x" * 30,
                          create=True)
    assert Path(path).read_text() == before


# Tests for the command

def run_cli(tmp_path, capsys, *argv):
    code = cli.main(["--root", str(tmp_path), "--json", "time-block",
                     "update", *argv])
    return code, json.loads(capsys.readouterr().out)


def test_time_block_cli_update_json(tmp_path, capsys):
    make_note(tmp_path)
    code, out = run_cli(tmp_path, capsys, "daily.md", "--time", "9:15am",
                        "--plan", "go")
    assert code == 0
    assert out["written"] == ["9:15am"]
    assert "| go " in lines_of(tmp_path / "daily.md")[8]


def test_time_block_cli_mismatch_json_has_current(tmp_path, capsys):
    make_note(tmp_path)
    code, out = run_cli(tmp_path, capsys, "daily.md", "--time", "09:00",
                        "--plan", "go")
    assert code == 1
    assert out["ok"] is False
    assert out["current"][0]["text"] == "mtg: standup"


def test_time_block_cli_no_text_is_error(tmp_path, capsys):
    make_note(tmp_path)
    code, out = run_cli(tmp_path, capsys, "daily.md", "--time", "09:00")
    assert code != 0
    assert out["ok"] is False


# Tests for replace

OLD_ROWS = """| 9:00am | mtg: standup | |
| 9:15am | | |
| 9:30am | | |"""


def replace(path, new, expect=OLD_ROWS, first=time(9, 0), last=time(9, 30)):
    return time_block.replace(path, first, last, expect, new)


def test_time_block_replace_reorder_adds_row(tmp_path):
    path = make_note(tmp_path)
    result = replace(path, "| 9:00am | write | |\n| 9:10am | call | |\n"
                           "| 9:15am | mtg: standup | |\n| 9:30am | | |")
    assert result.written == ["9:00am", "9:10am", "9:15am", "9:30am"]
    assert result.created == ["9:10am"]
    lines = lines_of(path)
    assert lines[7] == "|  9:00am | write                |                 |"
    assert lines[8].startswith("|  9:10am | call ")
    assert lines[9].startswith("|  9:15am | mtg: standup ")
    assert len(lines) == len(NOTE.splitlines()) + 1
    assert len({len(x) for x in lines[5:12]}) == 1


def test_time_block_replace_expect_ignores_padding(tmp_path):
    path = make_note(tmp_path)
    replace(path, OLD_ROWS.replace("standup", "review"),
            expect="|  9:00am |   mtg: standup  |  |\n|9:15am| | |\n"
                   "| 09:30 | | |")
    assert "review" in lines_of(path)[7]


def test_time_block_replace_stale_expect_writes_nothing(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_block.TimeBlockError) as e:
        replace(path, OLD_ROWS,
                expect=OLD_ROWS.replace("standup", "other"))
    assert e.value.current == [{"time": "9:00am", "column": "plan",
                                "text": "mtg: standup"}]
    assert lines_of(path) == NOTE.splitlines()


def test_time_block_replace_too_wide_writes_nothing(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_block.TimeBlockError, match="too wide"):
        replace(path, OLD_ROWS.replace("standup", "x" * 30))
    assert lines_of(path) == NOTE.splitlines()


def test_time_block_replace_wrong_cell_count(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_block.TimeBlockError, match="2 cells"):
        replace(path, OLD_ROWS.replace("| 9:15am | | |", "| 9:15am | |"))
    assert lines_of(path) == NOTE.splitlines()


def test_time_block_replace_deleted_row(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_block.TimeBlockError, match="9:15am"):
        replace(path, "| 9:00am | a | |\n| 9:30am | | |")
    assert lines_of(path) == NOTE.splitlines()


def test_time_block_replace_time_outside_range(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_block.TimeBlockError, match="outside"):
        replace(path, OLD_ROWS + "\n| 10:00am | | |")
    assert lines_of(path) == NOTE.splitlines()


def test_time_block_replace_duplicate_time(tmp_path):
    path = make_note(tmp_path)
    with pytest.raises(time_block.TimeBlockError, match="duplicate"):
        replace(path, OLD_ROWS + "\n| 9:30am | | |")


# Tests for header-found columns

SWAPPED = """### Time Block

| Time  | Actual   | Notes | PLAN        |
| ----- | -------- | ----- | ----------- |
| 9:00am |          |       | standup     |
| 9:15am |          |       |             |
"""


def test_time_block_update_columns_from_header(tmp_path):
    path = make_note(tmp_path, SWAPPED)
    time_block.update(path, time(9, 15), time(9, 15), plan="go",
                      actual="did")
    row = lines_of(path)[5].split("|")
    assert row[2].strip() == "did" and row[4].strip() == "go"
    assert len(row[4]) == len(" standup     ")


def test_time_block_replace_columns_from_header(tmp_path):
    path = make_note(tmp_path, SWAPPED)
    time_block.replace(path, time(9, 0), time(9, 15),
                       "| 9:00am | | | standup |\n| 9:15am | | | |",
                       "| 9:00am | done | n | a |\n| 9:15am | | | standup |")
    rows = lines_of(path)
    assert rows[4].split("|")[4].strip() == "a"
    assert rows[4].split("|")[2].strip() == "done"
    assert rows[5].split("|")[4].strip() == "standup"


def test_time_block_update_header_without_actual_fails(tmp_path):
    path = make_note(tmp_path, NOTE.replace("Actual ", "Result "))
    with pytest.raises(ValueError, match="Time, Plan, Result"):
        time_block.update(path, time(9, 15), time(9, 15), plan="x")


def test_time_block_cli_replace_json(tmp_path, capsys):
    make_note(tmp_path)
    code = cli.main(["--root", str(tmp_path), "--json", "time-block",
                     "replace", "daily.md", "--time", "9:00", "--through",
                     "9:30", "--expect", OLD_ROWS, "--text",
                     OLD_ROWS.replace("standup", "go")])
    out = json.loads(capsys.readouterr().out)
    assert code == 0 and out["written"][0] == "9:00am"
