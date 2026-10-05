"""
Unit tests for scripts/meta_notes/note_write.py
"""

import json
import sys
from pathlib import Path

import pytest

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import cli, note_write


def make(tmp_path, text="a\nb\nc\nd\n"):
    path = tmp_path / "n.md"
    path.write_bytes(text.encode())
    return path


def run_cli(tmp_path, capsys, *argv):
    code = cli.main(["--root", str(tmp_path), "--json", "note", "write",
                     *argv])
    return code, json.loads(capsys.readouterr().out)


# Tests for write

def test_note_write_range_more_lines(tmp_path, monkeypatch):
    path = make(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = note_write.write("n.md", "b\nc", "x\ny\nz", 2, 3)
    assert path.read_text() == "a\nx\ny\nz\nd\n"
    assert (result.line, result.end_line, result.changed) == (2, 4, True)


def test_note_write_range_delete(tmp_path, monkeypatch):
    path = make(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = note_write.write("n.md", "b\nc", "", 2, 3)
    assert path.read_text() == "a\nd\n"
    assert result.end_line == 1


def test_note_write_whole_file(tmp_path, monkeypatch):
    path = make(tmp_path)
    monkeypatch.chdir(tmp_path)
    note_write.write("n.md", "a\nb\nc\nd\n", "new\n")
    assert path.read_text() == "new\n"


def test_note_write_mismatch_writes_nothing(tmp_path, monkeypatch):
    path = make(tmp_path)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(note_write.NoteWriteError) as e:
        note_write.write("n.md", "b\nX", "q", 2, 3)
    assert e.value.current == ["b", "c"]
    assert path.read_text() == "a\nb\nc\nd\n"


def test_note_write_range_past_end_is_a_mismatch(tmp_path, monkeypatch):
    make(tmp_path)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(note_write.NoteWriteError) as e:
        note_write.write("n.md", "d", "q", 4, 5)
    assert e.value.current == ["d"]


def test_note_write_keeps_missing_trailing_newline(tmp_path, monkeypatch):
    path = make(tmp_path, "a\nb")
    monkeypatch.chdir(tmp_path)
    note_write.write("n.md", "b", "x\ny", 2, 2)
    assert path.read_bytes() == b"a\nx\ny"


def test_note_write_keeps_crlf(tmp_path, monkeypatch):
    path = make(tmp_path, "a\r\nb\r\n")
    monkeypatch.chdir(tmp_path)
    note_write.write("n.md", "a", "x\ny", 1, 1)
    assert path.read_bytes() == b"x\r\ny\r\nb\r\n"


def test_note_write_create(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = note_write.write("sub/new.md", "", "hi\n", create=True)
    assert (tmp_path / "sub/new.md").read_text() == "hi\n"
    assert (result.line, result.end_line) == (1, 1)


def test_note_write_missing_file_without_create(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(note_write.NoteWriteError):
        note_write.write("nope.md", "", "hi")


@pytest.mark.parametrize("path", ["../x.md", "/etc/x.md"])
def test_note_write_outside_root(tmp_path, monkeypatch, path):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(note_write.NoteWriteError):
        note_write.write(path, "", "hi", create=True)


# Tests for the CLI

def test_note_write_cli_json(tmp_path, capsys):
    path = make(tmp_path)
    code, out = run_cli(tmp_path, capsys, "n.md", "--lines", "2..2",
                        "--expect", "b", "--text", "x\ny")
    assert code == 0
    assert (out["ok"], out["line"], out["end_line"]) == (True, 2, 3)
    assert path.read_text() == "a\nx\ny\nc\nd\n"


def test_note_write_cli_refuses_with_current(tmp_path, capsys):
    path = make(tmp_path)
    code, out = run_cli(tmp_path, capsys, "n.md", "--lines", "2..2",
                        "--expect", "zzz", "--text", "x")
    assert code == 1
    assert out["ok"] is False and out["current"] == ["b"]
    assert path.read_text() == "a\nb\nc\nd\n"


def test_note_write_cli_bad_range(tmp_path, capsys):
    make(tmp_path)
    code, out = run_cli(tmp_path, capsys, "n.md", "--lines", "2",
                        "--expect", "b", "--text", "x")
    assert code == 1 and out["ok"] is False
