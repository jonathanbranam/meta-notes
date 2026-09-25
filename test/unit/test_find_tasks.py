"""
Unit tests for scripts/find_tasks.py

Tests selection, filtering, report layout, and the command line.
"""

import os
import sys
from pathlib import Path
from datetime import date

import pytest

# Add scripts directory to path to import the modules
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

import find_tasks
from tasks import Task, TaskStatus, find_tasks_in_file

TODAY = date(2026, 9, 25)


def make_task(text, due=None, start=None, completed=None, undated=False, tags=None,
              status=TaskStatus.INCOMPLETE, filename="file.md", line_no=1):
    return Task(text, status, filename, line_no, start_date=start, due_date=due,
                completed_date=completed, undated=undated, tags=tags or [])


def texts(selected):
    return [task.text for _section, task in selected]


def write_notes(root, files):
    for path, content in files.items():
        p = root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)


def run_main(monkeypatch, capsys, *args):
    monkeypatch.setattr(sys, "argv", ["find_tasks.py", *args])
    find_tasks.main()
    return capsys.readouterr().out


# Tests for resolve_modes function

def test_resolve_modes_default_is_ready():
    assert find_tasks.resolve_modes(None) == ['ready']
    assert find_tasks.resolve_modes([]) == ['ready']


def test_resolve_modes_all_expands():
    assert find_tasks.resolve_modes(['all']) == ['ready', 'future', 'undated']


def test_resolve_modes_section_order_and_duplicates():
    assert find_tasks.resolve_modes(['undated', 'due', 'overdue', 'due']) == \
        ['overdue', 'due', 'undated']


# Tests for select function: selection modes

def test_select_default_is_ready_as_of_today():
    a = make_task("A", due=date(2026, 9, 20))
    b = make_task("B", start=date(2026, 9, 25), due=date(2026, 10, 30))
    c = make_task("C", due=date(2026, 10, 1))

    selected = find_tasks.select([a, b, c], None, TODAY, TODAY)

    assert texts(selected) == ["A", "B"]
    assert all(section == 'ready' for section, _ in selected)


def test_select_ready_by_sunday():
    c = make_task("C", due=date(2026, 9, 26))
    sunday = date(2026, 9, 27)

    assert texts(find_tasks.select([c], ['ready'], sunday, sunday)) == ["C"]


def test_select_overdue():
    a = make_task("A", due=date(2026, 9, 24))
    d = make_task("D", due=date(2026, 9, 25))
    e = make_task("E", start=date(2026, 9, 1))

    assert texts(find_tasks.select([a, d, e], ['overdue'], TODAY, TODAY)) == ["A"]


def test_select_due_today_ignores_start_dates():
    d = make_task("D", due=date(2026, 9, 25))
    f = make_task("F", start=date(2026, 9, 25), due=date(2026, 10, 10))

    assert texts(find_tasks.select([d, f], ['due'], TODAY, TODAY)) == ["D"]


def test_select_scheduled_in_a_month():
    tasks = [
        make_task("due Oct 15", due=date(2026, 10, 15)),
        make_task("due Nov 12", due=date(2026, 11, 12)),
        make_task("starts Nov 3", start=date(2026, 11, 3)),
        make_task("spans", start=date(2026, 10, 1), due=date(2026, 12, 15)),
    ]

    selected = find_tasks.select(tasks, ['scheduled'], date(2026, 11, 1), date(2026, 11, 30))

    assert texts(selected) == ["due Nov 12", "starts Nov 3"]


def test_select_future_and_undated():
    c = make_task("C", due=date(2026, 10, 1))
    u = make_task("U", undated=True)

    selected = find_tasks.select([c, u], ['future', 'undated'], TODAY, TODAY)

    assert selected == [('future', c), ('undated', u)]


def test_select_undated_requires_no_start_date():
    u = make_task("U", undated=True, start=date(2026, 10, 5))

    assert find_tasks.select([u], ['undated'], TODAY, TODAY) == []
    assert find_tasks.select([u], ['future'], TODAY, TODAY) == [('future', u)]


def test_select_all_lists_every_task():
    tasks = [
        make_task("overdue", due=date(2026, 9, 1)),
        make_task("future", due=date(2026, 12, 1)),
        make_task("start only", start=date(2026, 12, 1)),
        make_task("undated", undated=True),
    ]

    selected = find_tasks.select(tasks, ['all'], TODAY, TODAY)

    assert [section for section, _ in selected] == ['ready', 'future', 'future', 'undated']


def test_select_overlap_listed_once_in_first_section():
    a = make_task("A", due=date(2026, 9, 20))

    selected = find_tasks.select([a], ['ready', 'overdue'], TODAY, TODAY)

    assert selected == [('overdue', a)]


def test_select_completed_uses_completion_date():
    done = make_task("ship it", due=date(2026, 10, 1), completed=date(2026, 10, 3),
                     status=TaskStatus.COMPLETED)
    day = date(2026, 10, 3)

    assert texts(find_tasks.select([done], ['due'], day, day)) == ["ship it"]
    assert find_tasks.select([done], ['due'], date(2026, 10, 1), date(2026, 10, 1)) == []


def test_select_completed_without_completion_date_uses_due_date():
    done = make_task("ship it", due=date(2026, 10, 1), status=TaskStatus.COMPLETED)

    selected = find_tasks.select([done], ['due'], date(2026, 10, 1), date(2026, 10, 31))

    assert texts(selected) == ["ship it"]


# Tests for select function: later tasks

def test_select_later_excluded():
    task = make_task("#later read book", due=date(2026, 9, 1), tags=['later'])

    assert find_tasks.select([task], ['overdue'], TODAY, TODAY) == []
    assert find_tasks.select([task], ['all'], TODAY, TODAY) == []


def test_select_later_excluded_any_case():
    task = make_task("#Later read book", due=date(2026, 9, 1), tags=['Later'])

    assert find_tasks.select([task], ['overdue'], TODAY, TODAY) == []


def test_select_later_included():
    task = make_task("#later read book", due=date(2026, 9, 1), tags=['later'])

    assert find_tasks.select([task], ['overdue'], TODAY, TODAY, later=True) == \
        [('overdue', task)]


# Tests for filter_tasks_by_tags function

def test_filter_tasks_by_tags_single_tag():
    admin = make_task("a", tags=['admin'])
    cd = make_task("b", tags=['cd'])

    assert find_tasks.filter_tasks_by_tags([admin, cd], ['admin']) == [admin]


def test_filter_tasks_by_tags_several_tags():
    admin = make_task("a", tags=['Admin'])
    cd = make_task("b", tags=['cd', 'x'])
    other = make_task("c", tags=['other'])
    none = make_task("d")

    assert find_tasks.filter_tasks_by_tags([admin, cd, other, none], ['admin', '#cd']) == \
        [admin, cd]


def test_filter_tasks_by_tags_alias():
    meeting = make_task("#mtg prep", tags=['meeting'])

    assert find_tasks.filter_tasks_by_tags([meeting], ['mtg']) == [meeting]
    assert find_tasks.filter_tasks_by_tags([meeting], ['meeting']) == [meeting]


# Tests for filter_tasks_by_folder function

def test_filter_tasks_by_folder_includes_subfolders(tmp_path):
    inside = make_task("in", filename=str(tmp_path / "project" / "a.md"))
    nested = make_task("nested", filename=str(tmp_path / "project" / "sub" / "b.md"))
    outside = make_task("out", filename=str(tmp_path / "area" / "c.md"))

    result = find_tasks.filter_tasks_by_folder([inside, nested, outside], "project/",
                                               str(tmp_path))

    assert result == [inside, nested]


# Tests for format_file_tasks function

def test_format_file_tasks_with_tasks(tmp_path):
    """Test formatting tasks from a file."""
    filepath = str(tmp_path / "test.md")
    tasks = [
        Task("- [ ] Task 1", TaskStatus.INCOMPLETE, filepath, 1),
        Task("- [ ] Task 2", TaskStatus.INCOMPLETE, filepath, 2),
    ]

    lines = find_tasks.format_file_tasks(filepath, tasks, str(tmp_path))

    assert lines == ["## [[test]]", "", "- [ ] Task 1", "- [ ] Task 2"]


def test_format_file_tasks_level(tmp_path):
    filepath = str(tmp_path / "test.md")
    tasks = [Task("- [ ] Task", TaskStatus.INCOMPLETE, filepath, 1)]

    lines = find_tasks.format_file_tasks(filepath, tasks, str(tmp_path), level=3)

    assert lines[0] == "### [[test]]"


def test_format_file_tasks_empty_list(tmp_path):
    """Test formatting with no tasks."""
    filepath = str(tmp_path / "test.md")

    assert find_tasks.format_file_tasks(filepath, [], str(tmp_path)) == []


def test_format_file_tasks_nested_file(tmp_path):
    """Test formatting with nested file path."""
    filepath = str(tmp_path / "notes" / "work" / "tasks.md")
    tasks = [Task("- [ ] Task", TaskStatus.INCOMPLETE, filepath, 1)]

    lines = find_tasks.format_file_tasks(filepath, tasks, str(tmp_path))

    assert lines[0] == "## [[notes/work/tasks]]"


# Tests for format_file_tasks_condensed function

def test_format_file_tasks_condensed_with_tasks(tmp_path):
    """Test condensed format with tasks."""
    filepath = str(tmp_path / "test.md")
    tasks = [
        Task("- [ ] Task 1", TaskStatus.INCOMPLETE, filepath, 1),
        Task("  * [ ] Subtask 1.1", TaskStatus.INCOMPLETE, filepath, 2),
        Task("- [ ] Task 2", TaskStatus.INCOMPLETE, filepath, 3),
    ]

    lines = find_tasks.format_file_tasks_condensed(filepath, tasks, str(tmp_path))

    assert lines == ["- [[test]]", "  - [ ] Task 1", "    * [ ] Subtask 1.1", "  - [ ] Task 2"]


def test_format_file_tasks_condensed_empty_list(tmp_path):
    """Test condensed format with no tasks."""
    filepath = str(tmp_path / "test.md")

    assert find_tasks.format_file_tasks_condensed(filepath, [], str(tmp_path)) == []


# Tests for run_query function: report layout

def test_run_query_single_mode_condensed(tmp_path):
    write_notes(tmp_path, {'project/foo.md': "# foo\n- [ ] Call Sam 📅 2026-09-25\n"})

    lines, _ = find_tasks.run_query(str(tmp_path), modes=['due'], condensed=True,
                                    today=TODAY)

    assert lines == ["- [[project/foo]]", "  - [ ] Call Sam 📅 2026-09-25"]


def test_run_query_single_mode_standard(tmp_path):
    write_notes(tmp_path, {
        'b.md': "- [ ] B1 📅 2026-09-20\n  - [ ] B2 📅 2026-09-21\n",
        'a.md': "- [ ] A1 📅 2026-09-22\n",
    })

    lines, _ = find_tasks.run_query(str(tmp_path), today=TODAY)

    assert lines == [
        "## [[a]]", "", "- [ ] A1 📅 2026-09-22", "",
        "## [[b]]", "", "- [ ] B1 📅 2026-09-20", "  - [ ] B2 📅 2026-09-21", "",
        "", "Summary: Found 3 tasks in 2 files",
    ]


def test_run_query_several_modes_have_section_headings(tmp_path):
    write_notes(tmp_path, {'foo.md': "- [ ] today 📅 2026-09-25\n- [ ] late 📅 2026-09-01\n"})

    lines, selected = find_tasks.run_query(str(tmp_path), modes=['due', 'overdue'],
                                           today=TODAY)

    assert lines == [
        "# Overdue", "", "## [[foo]]", "", "- [ ] late 📅 2026-09-01", "",
        "# Due", "", "## [[foo]]", "", "- [ ] today 📅 2026-09-25", "",
        "", "Summary: Found 2 tasks in 1 file",
    ]
    assert [section for section, _ in selected] == ['overdue', 'due']


def test_run_query_several_modes_condensed(tmp_path):
    write_notes(tmp_path, {'foo.md': "- [ ] today 📅 2026-09-25\n- [ ] late 📅 2026-09-01\n"})

    lines, _ = find_tasks.run_query(str(tmp_path), modes=['due', 'overdue'],
                                    condensed=True, today=TODAY)

    assert lines == [
        "# Overdue", "", "- [[foo]]", "  - [ ] late 📅 2026-09-01",
        "", "# Due", "", "- [[foo]]", "  - [ ] today 📅 2026-09-25",
    ]


def test_run_query_empty_section_has_no_heading(tmp_path):
    write_notes(tmp_path, {'foo.md': "- [ ] today 📅 2026-09-25\n"})

    lines, _ = find_tasks.run_query(str(tmp_path), modes=['due', 'overdue'], today=TODAY)

    assert "# Overdue" not in lines
    assert "# Due" in lines


def test_run_query_summary_counts_unique_tasks(tmp_path):
    write_notes(tmp_path, {'foo.md': "- [ ] #a #b both 📅 2026-09-20\n"})

    lines, selected = find_tasks.run_query(str(tmp_path), group_by='tag', today=TODAY)

    assert lines[-1] == "Summary: Found 1 task in 1 file"
    assert len(selected) == 1


def test_run_query_no_tasks(tmp_path):
    write_notes(tmp_path, {'foo.md': "- [ ] plain checkbox\n"})

    lines, selected = find_tasks.run_query(str(tmp_path), modes=['all'], today=TODAY)

    assert lines == ["No tasks found matching the criteria."]
    assert selected == []


def test_run_query_no_markdown_files(tmp_path):
    lines, selected = find_tasks.run_query(str(tmp_path), today=TODAY)

    assert lines == ["No markdown files found."]
    assert selected == []


def test_run_query_invalid_period(tmp_path):
    with pytest.raises(ValueError, match='2026-W45'):
        find_tasks.run_query(str(tmp_path), period='2026-W45')


def test_run_query_period(tmp_path):
    write_notes(tmp_path, {'foo.md': "- [ ] nov 📅 2026-11-12\n- [ ] oct 📅 2026-10-12\n"})

    _, selected = find_tasks.run_query(str(tmp_path), period='2026-11', modes=['scheduled'],
                                       today=TODAY)

    assert texts(selected) == ["- [ ] nov 📅 2026-11-12"]


def test_run_query_status_folder_and_tag_filter_before_selection(tmp_path):
    write_notes(tmp_path, {
        'project/a.md': ("- [ ] #admin open 📅\n"
                         "- [x] #admin done 📅\n"
                         "- [ ] #cd other 📅\n"),
        'area/b.md': "- [ ] #admin elsewhere 📅\n",
    })

    _, selected = find_tasks.run_query(str(tmp_path), modes=['all'], folder='project',
                                       tags=['admin'], status='all', today=TODAY)

    assert texts(selected) == ["- [ ] #admin open 📅", "- [x] #admin done 📅"]


def test_run_query_later_included(tmp_path):
    write_notes(tmp_path, {'foo.md': "- [ ] #later read book 📅 2026-09-01\n"})

    _, excluded = find_tasks.run_query(str(tmp_path), modes=['overdue'], today=TODAY)
    _, included = find_tasks.run_query(str(tmp_path), modes=['overdue'], later=True,
                                       today=TODAY)

    assert excluded == []
    assert [section for section, _ in included] == ['overdue']


# Tests for run_query function: group by tag

def test_run_query_group_by_tag_headings(tmp_path):
    write_notes(tmp_path, {'foo.md': ("- [ ] #cd one 📅 2026-09-20\n"
                                      "- [ ] #Admin two 📅 2026-09-20\n"
                                      "- [ ] three 📅 2026-09-20\n")})

    lines, _ = find_tasks.run_query(str(tmp_path), group_by='tag', today=TODAY)

    assert lines == [
        "## Admin", "", "### [[foo]]", "", "- [ ] #Admin two 📅 2026-09-20", "",
        "## cd", "", "### [[foo]]", "", "- [ ] #cd one 📅 2026-09-20", "",
        "## Not tagged", "", "### [[foo]]", "", "- [ ] three 📅 2026-09-20", "",
        "", "Summary: Found 3 tasks in 1 file",
    ]


def test_run_query_group_by_tag_with_tag_filter(tmp_path):
    write_notes(tmp_path, {'foo.md': ("- [ ] #cd #admin both 📅 2026-09-20\n"
                                      "- [ ] #cd one 📅 2026-09-20\n"
                                      "- [ ] #other no 📅 2026-09-20\n"
                                      "- [ ] untagged 📅 2026-09-20\n")})

    lines, selected = find_tasks.run_query(str(tmp_path), group_by='tag',
                                           tags=['admin', 'cd'], condensed=True,
                                           today=TODAY)

    assert lines == [
        "## admin", "", "- [[foo]]", "  - [ ] #cd #admin both 📅 2026-09-20",
        "", "## cd", "", "- [[foo]]", "  - [ ] #cd #admin both 📅 2026-09-20",
        "  - [ ] #cd one 📅 2026-09-20",
    ]
    assert len(selected) == 2


def test_run_query_group_by_tag_inside_sections(tmp_path):
    write_notes(tmp_path, {'foo.md': ("- [ ] #x late 📅 2026-09-01\n"
                                      "- [ ] #x today 📅 2026-09-25\n")})

    lines, _ = find_tasks.run_query(str(tmp_path), modes=['overdue', 'due'],
                                    group_by='tag', condensed=True, today=TODAY)

    assert lines == [
        "# Overdue", "", "## x", "", "- [[foo]]", "  - [ ] #x late 📅 2026-09-01",
        "", "# Due", "", "## x", "", "- [[foo]]", "  - [ ] #x today 📅 2026-09-25",
    ]


# Tests for main function (integration tests)

def test_main_default_lists_ready_tasks(tmp_path, capsys, monkeypatch):
    (tmp_path / "tasks.md").write_text("# Tasks\n"
                                       "- [ ] Task 1 📅 2000-01-01\n"
                                       "- [x] Task 2 📅 2000-01-01\n"
                                       "- [ ] Task 3 🛫 2000-01-01\n"
                                       "- [ ] Task 4 📅 2999-01-01\n"
                                       "- [ ] Plain checkbox\n")

    out = run_main(monkeypatch, capsys, str(tmp_path))

    assert "## [[tasks]]" in out
    assert "Task 1" in out
    assert "Task 3" in out
    assert "Task 2" not in out
    assert "Task 4" not in out
    assert "Plain checkbox" not in out
    assert "Summary: Found 2 tasks in 1 file" in out


def test_main_invalid_directory(capsys, monkeypatch):
    """Test main function with invalid directory."""
    monkeypatch.setattr(sys, "argv", ["find_tasks.py", "/nonexistent/path"])

    with pytest.raises(SystemExit) as exc_info:
        find_tasks.main()

    assert exc_info.value.code == 1
    assert "not a directory" in capsys.readouterr().err


def test_main_default_directory(capsys, monkeypatch, tmp_path):
    """Test main function uses current directory by default."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "test.md").write_text("- [ ] Test task 📅 2000-01-01\n")

    out = run_main(monkeypatch, capsys)

    assert "Test task" in out


def test_main_with_condensed_flag(tmp_path, capsys, monkeypatch):
    (tmp_path / "tasks.md").write_text("- [ ] Task 1 📅\n- [ ] Task 2 📅\n")

    out = run_main(monkeypatch, capsys, str(tmp_path), "--undated", "--condensed")

    assert out == "- [[tasks]]\n  - [ ] Task 1 📅\n  - [ ] Task 2 📅\n"


def test_main_with_format_condensed(tmp_path, capsys, monkeypatch):
    (tmp_path / "tasks.md").write_text("- [ ] Task 1 📅\n")

    out = run_main(monkeypatch, capsys, str(tmp_path), "--undated", "--format=condensed")

    assert out == "- [[tasks]]\n  - [ ] Task 1 📅\n"


def test_main_condensed_flag_overrides_format(tmp_path, capsys, monkeypatch):
    (tmp_path / "tasks.md").write_text("- [ ] Task 1 📅\n")

    out = run_main(monkeypatch, capsys, str(tmp_path), "--undated",
                   "--format=standard", "--condensed")

    assert "- [[tasks]]" in out
    assert "## [[" not in out


def test_main_modes_date_tag_and_folder(tmp_path, capsys, monkeypatch):
    write_notes(tmp_path, {
        'project/a.md': "- [ ] #mtg prep 📅 2026-10-01\n- [ ] other 📅 2026-10-01\n",
        'area/b.md': "- [ ] #meeting elsewhere 📅 2026-10-01\n",
    })

    out = run_main(monkeypatch, capsys, str(tmp_path), "--due", "--date", "2026-10",
                   "--tag", "meeting", "--folder", "project", "--condensed")

    assert out == "- [[project/a]]\n  - [ ] #mtg prep 📅 2026-10-01\n"


def test_main_tag_waiting_alias(tmp_path, capsys, monkeypatch):
    (tmp_path / "a.md").write_text(
        "- [ ] #waiting legal sign-off 📅 2026-10-15\n- [ ] other 📅 2026-10-15\n")

    for tag in ("wait", "waiting"):
        out = run_main(monkeypatch, capsys, str(tmp_path), "--due", "--date",
                       "2026-10", "--tag", tag, "--condensed")
        assert out == "- [[a]]\n  - [ ] #waiting legal sign-off 📅 2026-10-15\n"


def test_main_all_and_later(tmp_path, capsys, monkeypatch):
    (tmp_path / "a.md").write_text("- [ ] #later someday 📅\n- [ ] now 📅\n")

    out = run_main(monkeypatch, capsys, str(tmp_path), "--all", "--later", "--condensed")

    assert "someday" in out
    assert "now" in out


def test_main_group_by_tag(tmp_path, capsys, monkeypatch):
    (tmp_path / "a.md").write_text("- [ ] #x task 📅\n")

    out = run_main(monkeypatch, capsys, str(tmp_path), "--undated", "--group-by", "tag",
                   "--condensed")

    assert out == "## x\n\n- [[a]]\n  - [ ] #x task 📅\n"


@pytest.mark.parametrize('option', [
    ['--due-on', '2026-09-25'],
    ['--due-by', '2026-09-25'],
    ['--due-between', '2026-09-01', '2026-09-30'],
])
def test_main_removed_options_are_usage_errors(tmp_path, capsys, monkeypatch, option):
    monkeypatch.setattr(sys, "argv", ["find_tasks.py", str(tmp_path), *option])

    with pytest.raises(SystemExit) as exc_info:
        find_tasks.main()

    assert exc_info.value.code != 0
    err = capsys.readouterr().err
    assert "usage:" in err
    assert option[0] in err


def test_main_invalid_date_exits_1(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["find_tasks.py", str(tmp_path), "--date", "2026-W45"])

    with pytest.raises(SystemExit) as exc_info:
        find_tasks.main()

    assert exc_info.value.code == 1
    err = capsys.readouterr().err
    assert "Invalid date: 2026-W45" in err
    assert "YYYY-Qn" in err
