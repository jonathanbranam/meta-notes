"""
Unit tests for scripts/meta_notes/template.py

Tests variables, template discovery, frontmatter, and command blocks. Cases
are ported from the removed CreateContext, ProcessVariables, FindTemplate,
ExecuteCommand, and ProcessTemplate vader tests.
"""

import locale
import os
import shlex
import sys
from datetime import date
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
repo_dir = Path(__file__).parent.parent.parent
scripts_dir = repo_dir / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import note, template

FIXTURES = repo_dir / 'test' / 'fixtures' / 'templates'
TEMPLATES = repo_dir / 'templates'


@pytest.fixture
def notes_root(tmp_path, monkeypatch):
    """An empty notes root as the current directory."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def context(**values):
    """A context with the given date variables as dates."""
    return {k: date.fromisoformat(v) if k in template.DATE_VARIABLES else v
            for k, v in values.items()}


def write(path, lines):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(line + '\n' for line in lines))
    return str(path)


# Tests for build_context function

def test_build_context_all_variables():
    """Every variable is present, with week and quarter derived from the date."""
    ctx = template.build_context(date(2026, 2, 14), 'test/note.md',
                                 today=date(2026, 3, 1))
    assert ctx == {
        'date': date(2026, 2, 14),
        'today': date(2026, 3, 1),
        'week_start': date(2026, 2, 9),
        'week_end': date(2026, 2, 15),
        'quarter': 'Q1',
        'week_quarter': 'Q1',
        'filepath': 'test/note.md',
        'note_path': 'test/note',
        'note_name': 'note',
        'filename': 'note.md',
        'project_name': '',
    }


def test_build_context_today_defaults_to_today():
    ctx = template.build_context(date(2026, 2, 14), 'test/note.md')
    assert ctx['today'] == date.today()


def test_build_context_quarters():
    for month, expected in ((1, 'Q1'), (4, 'Q2'), (7, 'Q3'), (10, 'Q4')):
        ctx = template.build_context(date(2026, month, 15), 'test.md')
        assert ctx['quarter'] == expected


def test_build_context_week_start_and_end():
    """Monday to Sunday, including on the boundary days."""
    for day in (9, 10, 13, 15):
        ctx = template.build_context(date(2026, 2, day), 'test.md')
        assert ctx['week_start'] == date(2026, 2, 9)
        assert ctx['week_end'] == date(2026, 2, 15)


def test_build_context_week_quarter_monday_in_previous_quarter():
    """Thursday 2026-04-02 is in Q2; its Monday, 2026-03-30, is in Q1."""
    ctx = template.build_context(date(2026, 4, 2), 'test.md')
    assert template.render_line('{{quarter}} {{week_quarter}}', ctx) == 'Q2 Q1'


def test_build_context_week_quarter_monday_in_previous_year():
    """Thursday 2026-01-01's Monday, 2025-12-29, is in Q4."""
    ctx = template.build_context(date(2026, 1, 1), 'test.md')
    assert template.render_line('{{week_quarter}}', ctx) == 'Q4'


def test_build_context_week_quarter_week_within_one_quarter():
    ctx = template.build_context(date(2026, 2, 13), 'test.md')
    assert template.render_line('{{week_quarter}}', ctx) == 'Q1'


def test_build_context_project_name():
    ctx = template.build_context(date(2026, 6, 19), 'project/lunch/Lunch Ideas.md')
    assert template.render_line('{{project_name}}', ctx) == 'lunch'


def test_build_context_project_name_nested():
    ctx = template.build_context(date(2026, 6, 19),
                                 'project/my-project/subfolder/Note.md')
    assert template.render_line('Project: {{project_name}}', ctx) == 'Project: my-project'


def test_build_context_project_name_empty_outside_project():
    ctx = template.build_context(date(2026, 6, 19), 'area/health/Goals.md')
    assert template.render_line('Project: {{project_name}}', ctx) == 'Project: '


def test_build_context_path_variables():
    ctx = template.build_context(date(2026, 6, 19), 'project/lunch/Lunch Ideas.md')
    assert template.render_line('{{note_path}}', ctx) == 'project/lunch/Lunch Ideas'
    assert template.render_line('{{note_name}}', ctx) == 'Lunch Ideas'
    assert template.render_line('{{filepath}}', ctx) == 'project/lunch/Lunch Ideas.md'
    assert template.render_line('{{filename}}', ctx) == 'Lunch Ideas.md'


def test_build_context_date_named_note_name_is_not_a_date():
    """note_name of a date-named file is its stem, not a formatted date."""
    ctx = template.build_context(date(2026, 6, 19), 'plan/daily/26-Q2/2026-06-19.md')
    assert template.render_line('{{note_name}}', ctx) == '2026-06-19'


# Tests for render_line function

def test_render_line_date_default_format():
    ctx = context(date='2026-02-14', today='2026-02-14')
    assert template.render_line('Today is {{date}}', ctx) == 'Today is 2026-02-14 Sat'


def test_render_line_date_format():
    ctx = context(date='2026-02-14')
    assert (template.render_line('{{date:%A, %B %d, %Y}}', ctx)
            == 'Saturday, February 14, 2026')


def test_render_line_date_arithmetic():
    ctx = context(today='2026-02-14')
    assert (template.render_line('Tomorrow: {{today+1:%Y-%m-%d}}', ctx)
            == 'Tomorrow: 2026-02-15')
    assert (template.render_line('Yesterday: {{today-1:%Y-%m-%d}}', ctx)
            == 'Yesterday: 2026-02-13')


def test_render_line_date_arithmetic_default_format():
    ctx = template.build_context(date(2026, 6, 19), 'project/foo/note.md')
    assert template.render_line('{{date+7}}', ctx) == '2026-06-26 Fri'


def test_render_line_date_arithmetic_across_dst():
    """Calendar days, not 86400-second steps (US fall back is 2026-11-01)."""
    ctx = context(date='2026-10-31')
    assert template.render_line('{{date+1:%Y-%m-%d}}', ctx) == '2026-11-01'
    assert template.render_line('{{date+2:%Y-%m-%d}}', ctx) == '2026-11-02'


def test_render_line_week_variables():
    ctx = context(week_start='2026-02-09', week_end='2026-02-15')
    assert (template.render_line('Week: {{week_start}} to {{week_end:%Y-%m-%d}}', ctx)
            == 'Week: 2026-02-09 Mon to 2026-02-15')


def test_render_line_quarter():
    ctx = context(date='2026-02-14', quarter='Q1')
    assert (template.render_line('Quarterly Plan: {{date:%Y}}-{{quarter}}', ctx)
            == 'Quarterly Plan: 2026-Q1')


def test_render_line_unknown_variable():
    ctx = context(date='2026-02-14')
    assert (template.render_line('Date: {{date}}, Name: {{name}}', ctx)
            == 'Date: 2026-02-14 Sat, Name: <!-- ERROR: Unknown variable "name" -->')


def test_render_line_unknown_variable_with_arithmetic():
    ctx = context(date='2026-02-14')
    assert (template.render_line('{{nope+1}}', ctx)
            == '<!-- ERROR: Unknown variable "nope" -->')


def test_render_line_single_pass():
    """A value containing {{...}} is not expanded again."""
    ctx = {'project_name': '{{secret}}', 'secret': 'x'}
    assert template.render_line('{{project_name}}', ctx) == '{{secret}}'


@pytest.fixture
def german_locale():
    """LC_TIME set to German, restored afterwards; skips if unavailable."""
    saved = locale.setlocale(locale.LC_TIME)
    for name in ('de_DE.UTF-8', 'de_DE.utf8', 'de_DE'):
        try:
            locale.setlocale(locale.LC_TIME, name)
            break
        except locale.Error:
            continue
    else:
        pytest.skip('no German locale installed')
    yield
    locale.setlocale(locale.LC_TIME, saved)


def test_render_line_english_names():
    ctx = context(date='2026-03-02')
    assert (template.render_line('{{date:%a %A %b %B %h}}', ctx)
            == 'Mon Monday Mar March Mar')


def test_render_line_english_names_regardless_of_locale(german_locale):
    ctx = context(date='2026-03-02')
    assert template.render_line('{{date}} {{date:%A %B}}', ctx) == '2026-03-02 Mon Monday March'


def test_render_line_percent_escape():
    ctx = context(date='2026-03-02')
    assert template.render_line('{{date:100%% %a}}', ctx) == '100% Mon'


# Tests for find_template function

def test_find_template_folder_template(notes_root):
    write('test_folder/subfolder/template.md', ['# Folder Template', ''])
    assert (template.find_template('test_folder/subfolder/note.md')
            == 'test_folder/subfolder/template.md')


def test_find_template_folder_template_wins_over_standard(notes_root):
    write('resource/template/daily.md', ['# Daily Template'])
    write('plan/daily/26-Q1/template.md', ['# Folder'])
    assert (template.find_template('plan/daily/26-Q1/2026-02-14 Sat.md')
            == 'plan/daily/26-Q1/template.md')


def test_find_template_immediate_parent_only(notes_root):
    write('project/big/template.md', ['# Project Note'])
    write('project/big/sub/template.md', ['# Submodule Note'])
    assert template.find_template('project/big/sub/x.md') == 'project/big/sub/template.md'
    Path('project/big/sub/template.md').unlink()
    assert template.find_template('project/big/sub/x.md') is None


def test_find_template_none(notes_root):
    Path('test_folder/no_template').mkdir(parents=True)
    assert template.find_template('test_folder/no_template/note.md') is None


def test_find_template_plan_standard_templates(notes_root):
    for kind in ('daily', 'weekly', 'quarterly', 'yearly'):
        write(f'resource/template/{kind}.md', [f'# {kind}'])
    assert template.find_template('plan/daily/26-Q1/2026-02-14.md') == 'resource/template/daily.md'
    assert template.find_template('plan/week/26-Q1/2026-02-09.md') == 'resource/template/weekly.md'
    assert template.find_template('plan/quarter/2026-Q1.md') == 'resource/template/quarterly.md'
    assert template.find_template('plan/year/2026.md') == 'resource/template/yearly.md'


def test_find_template_plan_standard_template_missing(notes_root):
    assert template.find_template('plan/year/2026.md') is None


def test_find_template_top_level_note(notes_root):
    write('template.md', ['# Top'])
    assert template.find_template('note.md') == 'template.md'


# Tests for strip_frontmatter and render functions

def test_render_skips_frontmatter(notes_root):
    path = write('t.md', ['---', 'filename_pattern: "test"', '---',
                          '# Test Template', 'Date: {{date}}'])
    result = template.render(path, context(date='2026-02-14'))
    assert result.lines == ['# Test Template', 'Date: 2026-02-14 Sat']


def test_render_keeps_rule_not_at_top(notes_root):
    """Only a block starting on the first line is frontmatter."""
    path = write('t.md', ['# Title', '---', 'kept', '---', 'end'])
    assert template.render(path, {}).lines == ['# Title', '---', 'kept', '---', 'end']


def test_render_keeps_later_rules_after_frontmatter(notes_root):
    path = write('t.md', ['---', 'a: b', '---', '# T', '---', 'x'])
    assert template.render(path, {}).lines == ['# T', '---', 'x']


def test_render_crlf_and_bom(notes_root):
    Path('t.md').write_bytes('﻿# T\r\n{{quarter}}\r\n'.encode('utf-8'))
    assert template.render('t.md', {'quarter': 'Q1'}).lines == ['# T', 'Q1']


def test_render_shell_command_end_to_end(notes_root):
    path = write('t.md', ['# Tasks for {{date}}', '',
                          '{{% shell echo "- Task from shell" %}}', '', 'End'])
    result = template.render(path, context(date='2026-02-14'))
    # Output ending in a newline leaves an empty line, as in Vim
    assert result.lines == ['# Tasks for 2026-02-14 Sat', '', '- Task from shell',
                            '', '', 'End']
    assert result.warnings == []
    assert not result.has_vim_blocks


def test_render_command_replaces_whole_line(notes_root):
    path = write('t.md', ['before {{% shell printf x %}} after'])
    assert template.render(path, {}).lines == ['x']


def test_render_unmatched_command_line_kept_verbatim(notes_root):
    """A `{{%` line that isn't a command block is kept, unsubstituted."""
    path = write('t.md', ['{{% nope {{date}}'])
    assert template.render(path, context(date='2026-02-14')).lines == ['{{% nope {{date}}']


def test_render_commands_run_from_current_directory(notes_root):
    Path('marker.txt').write_text('here\n')
    path = write('sub/t.md', ['{{% shell cat marker.txt %}}'])
    assert template.render(path, {}).lines == ['here', '']


# Tests for run_command_block function

def test_run_command_block_shell():
    output, warning, is_vim = template.run_command_block(
        '{{% shell echo "Hello from shell" %}}', context(date='2026-02-14'))
    assert (output, warning, is_vim) == ('Hello from shell\n', None, False)


def test_run_command_block_python():
    output, warning, _ = template.run_command_block(
        '{{% python -c "print(2 + 2)" %}}', context(date='2026-02-14'))
    assert (output, warning) == ('4\n', None)


def test_run_command_block_python_uses_running_interpreter():
    output, _, _ = template.run_command_block(
        '{{% python -c "import sys; print(sys.executable)" %}}', {})
    assert output == sys.executable + '\n'


def test_run_command_block_python_scripts_resolved_to_plugin(tmp_path, monkeypatch):
    """scripts/ means the plugin's scripts/, even with a notes root's own."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'scripts').mkdir()
    (tmp_path / 'scripts' / 'notes.py').write_text('print("wrong")\n')
    output, warning, _ = template.run_command_block(
        '{{% python scripts/notes.py --help %}}', {})
    assert warning is None
    assert 'wrong' not in output


def test_run_command_block_python_script_sees_notes_root(tmp_path, monkeypatch):
    """The plugin's find_tasks.py runs from the notes root with substituted args."""
    monkeypatch.chdir(tmp_path)
    write('project/p.md', ['- [ ] Pay rent 📆 2026-02-13', '- [ ] Other 📆 2026-02-14'])
    output, warning, _ = template.run_command_block(
        '{{% python scripts/find_tasks.py --due-on {{date:%Y-%m-%d}} --condensed %}}',
        context(date='2026-02-13'))
    assert warning is None
    assert 'Pay rent' in output
    assert 'Other' not in output


def test_run_command_block_merges_stderr():
    output, _, _ = template.run_command_block('{{% shell echo oops >&2 %}}', {})
    assert output == 'oops\n'


def test_run_command_block_stdin_closed():
    """A command reading stdin gets EOF instead of blocking."""
    output, warning, _ = template.run_command_block('{{% shell cat %}}', {})
    assert (output, warning) == ('', None)


def test_run_command_block_failure():
    line = '{{% shell echo bad; exit 1 %}}'
    output, warning, _ = template.run_command_block(line, {})
    assert output == f'<!-- Command failed: {line}\nError: bad\n -->'
    assert warning == f'Command failed: {line}'


def test_run_command_block_substitutes_variables():
    output, _, _ = template.run_command_block(
        '{{% shell echo "{{date}}" %}}', context(date='2026-02-14'))
    assert output == '2026-02-14 Sat\n'


def test_run_command_block_unknown_type():
    output, warning, _ = template.run_command_block('{{% unknown some command %}}', {})
    assert (output, warning) == ('<!-- Unknown command type: unknown -->', None)


def test_render_failed_command_warns(notes_root):
    path = write('t.md', ['# T', '{{% shell exit 1 %}}', 'end'])
    result = template.render(path, {})
    assert result.lines == ['# T', '<!-- Command failed: {{% shell exit 1 %}}',
                            'Error:  -->', 'end']
    assert result.warnings == ['Command failed: {{% shell exit 1 %}}']


# Tests for vim blocks

def test_render_vim_block_passed_through(notes_root):
    path = write('t.md', ['# T', '{{% vim echo "{{date}}" %}}', 'end'])
    result = template.render(path, context(date='2026-02-14'))
    assert result.lines == ['# T', '{{% vim echo "2026-02-14 Sat" %}}', 'end']
    assert result.has_vim_blocks
    assert result.warnings == []


# Tests for compatibility with the Vim implementation

def stub_run(command):
    """Stand-in for the shell: what the fixtures' stub python3 printed."""
    argv = shlex.split(command)
    assert argv[0] == sys.executable
    return 0, f"- [ ] stub: {os.path.basename(argv[1])} {' '.join(argv[2:])}\n"


@pytest.mark.parametrize('fixture', sorted(p.name for p in FIXTURES.glob('*.md')))
def test_render_matches_vim_fixture(fixture, notes_root, monkeypatch):
    """
    Rendering the shipped templates matches the Vim implementation.

    The fixtures are `<kind>-<date>.md`: the buffer :MetaNotesDaily and
    friends produced for that date, rendered by the Vimscript before it was
    removed, with a python3 on PATH that printed `- [ ] stub: <script>
    <args>` for command blocks. They were later edited to drop the day name
    from the week plan link and heading, and to file the week plan link of
    `daily-2026-04-02.md` under the quarter of its Monday (`26-Q1`), matching
    the shipped templates.
    """
    kind, _, day = fixture.removesuffix('.md').partition('-')
    Path('resource/template').mkdir(parents=True)
    for name in ('daily', 'weekly', 'quarterly', 'yearly'):
        (notes_root / 'resource/template' / f'{name}.md').write_bytes(
            (TEMPLATES / f'{name}.md').read_bytes())
    monkeypatch.setattr(template, '_run', stub_run)

    result = note.create(kind, day, render_only=True)

    assert result.content.encode('utf-8') == (FIXTURES / fixture).read_bytes()
