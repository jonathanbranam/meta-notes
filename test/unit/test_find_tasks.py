"""
Unit tests for scripts/find_tasks.py

Tests the CLI main function.
"""

import os
import sys
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

import find_tasks


class TestMainFunction:
    """Integration tests for main function."""

    def test_main_with_tasks(self, tmp_path, capsys, monkeypatch):
        """Test main function with files containing tasks."""
        # Create test files
        file1 = tmp_path / "tasks.md"
        file1.write_text("""# Tasks
- [ ] Task 1
- [x] Task 2
""")

        file2 = tmp_path / "notes.md"
        file2.write_text("""# Notes
* [ ] Note task
""")

        # Mock sys.argv
        monkeypatch.setattr(sys, "argv", ["find_tasks.py", str(tmp_path)])

        # Run main
        find_tasks.main()

        # Check output
        captured = capsys.readouterr()
        assert "[[tasks]]" in captured.out
        assert "[[notes]]" in captured.out
        assert "Task 1" in captured.out
        assert "Task 2" in captured.out
        assert "Note task" in captured.out
        assert "Found 3 tasks in 2 files" in captured.out

    def test_main_no_tasks(self, tmp_path, capsys, monkeypatch):
        """Test main function with no tasks."""
        file1 = tmp_path / "empty.md"
        file1.write_text("# No tasks here\n")

        monkeypatch.setattr(sys, "argv", ["find_tasks.py", str(tmp_path)])

        find_tasks.main()

        captured = capsys.readouterr()
        assert "No tasks found" in captured.out

    def test_main_no_markdown_files(self, tmp_path, capsys, monkeypatch):
        """Test main function with no markdown files."""
        monkeypatch.setattr(sys, "argv", ["find_tasks.py", str(tmp_path)])

        with pytest.raises(SystemExit) as exc_info:
            find_tasks.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "No markdown files found" in captured.err

    def test_main_default_directory(self, capsys, monkeypatch, tmp_path):
        """Test main function uses current directory by default."""
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            file1 = tmp_path / "test.md"
            file1.write_text("- [ ] Test task\n")

            monkeypatch.setattr(sys, "argv", ["find_tasks.py"])

            find_tasks.main()

            captured = capsys.readouterr()
            assert "Test task" in captured.out
        finally:
            os.chdir(original_dir)

    def test_main_invalid_directory(self, capsys, monkeypatch):
        """Test main function with invalid directory."""
        monkeypatch.setattr(sys, "argv", ["find_tasks.py", "/nonexistent/path"])

        with pytest.raises(SystemExit) as exc_info:
            find_tasks.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "not a directory" in captured.err
