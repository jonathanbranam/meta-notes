"""
Unit tests for scripts/meta_notes/init.py and the `init` subcommand

Tests folders, templates, the sentinel, skill install, re-runs, nesting, the
cache folder, .gitignore entries, and the virtualenv. Interpreter and pip
calls are stubbed (the `commands` fixture); no test builds a real virtualenv.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Add scripts directory to path to import the modules
repo_dir = Path(__file__).parent.parent.parent
scripts_dir = repo_dir / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import cli, init

FIXTURES = repo_dir / 'test' / 'fixtures' / 'init_templates'
TEMPLATE_NAMES = ('daily.md', 'weekly.md', 'quarterly.md', 'yearly.md')

# The env fixture stubs init.cli_on_path; keep the real one for its own test
REAL_CLI_ON_PATH = init.cli_on_path


class FakeCommands:
    """
    Stands in for init.run_command. Records each argv and answers like a
    working Python 3.11 with venv and pip, unless told otherwise: `version`
    is what the version check prints, `missing` is a set of executables
    that don't exist, and `fail` maps 'venv' or 'pip' to output for a
    failing run.
    """

    def __init__(self):
        self.calls = []
        self.version = '3.11'
        self.missing = set()
        self.fail = {}

    def __call__(self, argv):
        self.calls.append(argv)
        if argv[0] in self.missing:
            raise FileNotFoundError(2, 'No such file or directory', argv[0])
        if argv[1] == '-c':
            return subprocess.CompletedProcess(argv, 0, self.version + '\n')
        step = 'venv' if argv[1:3] == ['-m', 'venv'] else 'pip'
        if step == 'venv':
            python = Path(argv[-1]) / 'bin' / 'python3'
            python.parent.mkdir(parents=True, exist_ok=True)
            python.write_text(f'python from {argv[0]}\n')
        if step in self.fail:
            return subprocess.CompletedProcess(argv, 1, self.fail[step])
        return subprocess.CompletedProcess(argv, 0, '')


@pytest.fixture(autouse=True)
def env(tmp_path, monkeypatch):
    """Isolate HOME and META_NOTES_ROOT, restore the cwd, and stub the PATH check."""
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(init, 'cli_on_path', lambda: True)


@pytest.fixture(autouse=True)
def commands(monkeypatch):
    """Stub the interpreter and pip calls init makes."""
    fake = FakeCommands()
    monkeypatch.setattr(init, 'run_command', fake)
    return fake


@pytest.fixture
def skills(tmp_path, monkeypatch):
    """A plugin skills/ directory with one skill, `review`."""
    skills_dir = tmp_path / 'plugin' / 'skills'
    (skills_dir / 'review').mkdir(parents=True)
    (skills_dir / 'review' / 'SKILL.md').write_text('v1\n')
    (skills_dir / 'not-a-skill').mkdir()
    monkeypatch.setattr(init, 'SKILLS_DIR', skills_dir)
    return skills_dir


def statuses(result):
    return {(i.kind, i.path): i.status for i in result.items}


def without_gitignore(items):
    """Statuses of every item but .gitignore entries (skipped with no file)."""
    return {s for (kind, _), s in items.items() if kind != 'gitignore'}


def run_json(capsys, argv):
    code = cli.main(argv + ['--json'])
    captured = capsys.readouterr()
    return code, json.loads(captured.out), captured.err


# Tests for shipped templates

@pytest.mark.parametrize('name', TEMPLATE_NAMES)
def test_templates_match_vim_output(name):
    """
    Shipped templates are byte-identical to what :MetaNotesInit wrote, with
    the ceremony markers and sections since added to daily and weekly.
    """
    shipped = (init.TEMPLATES_DIR / name).read_bytes()
    assert shipped == (FIXTURES / name).read_bytes()


# Tests for init function: structure

def test_init_empty_directory(tmp_path, skills):
    """Every folder, template, the sentinel, and each skill are created."""
    root = tmp_path / 'notes'
    root.mkdir()

    result = init.init(str(root))

    for folder in init.FOLDERS:
        assert (root / folder).is_dir()
    for name in TEMPLATE_NAMES:
        assert (root / 'resource' / 'template' / name).read_bytes() == \
            (FIXTURES / name).read_bytes()
    assert (root / '.meta-notes').is_file()
    assert (root / '.meta-notes-cache' / 'README.md').read_bytes() == \
        (init.TEMPLATES_DIR / 'cache-README.md').read_bytes()
    assert (root / '.venv' / 'bin' / 'python3').is_file()
    assert (root / '.claude' / 'skills' / 'review').is_symlink()
    assert not (root / '.claude' / 'skills' / 'not-a-skill').exists()
    assert without_gitignore(statuses(result)) == {'created'}


def test_init_creates_missing_target_with_parents(tmp_path, skills):
    """A missing target is created, including parents."""
    root = tmp_path / 'notes' / 'personal'

    init.init(str(root))

    assert (root / '.meta-notes').is_file()


def test_init_sentinel_content(tmp_path, skills):
    """The sentinel holds the marker comment."""
    init.init(str(tmp_path / 'n'))
    assert (tmp_path / 'n' / '.meta-notes').read_text() == init.SENTINEL_CONTENT


def test_init_sentinel_that_is_a_directory(tmp_path, skills):
    """A directory named .meta-notes is an error."""
    (tmp_path / 'n' / '.meta-notes').mkdir(parents=True)
    with pytest.raises(init.InitError, match='not a file'):
        init.init(str(tmp_path / 'n'))


# Tests for init function: re-runs

def test_init_rerun_is_all_exists(tmp_path, skills):
    """A second run creates nothing and reports everything as existing."""
    init.init(str(tmp_path / 'n'))
    result = init.init(str(tmp_path / 'n'))
    assert without_gitignore(statuses(result)) == {'exists'}


def test_init_existing_root_without_sentinel_unchanged(tmp_path, skills):
    """A populated pre-sentinel root gains the sentinel; files are unchanged."""
    root = tmp_path / 'n'
    notes = {
        'project/foo.md': '# project/foo\n- [ ] task\n',
        'area/home.md': '# area/home\n',
        'resource/template/daily.md': 'my daily\n',
        'plan/daily/26-Q3/2026-09-25 Fri.md': '# today\n',
    }
    for path, text in notes.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text)

    result = init.init(str(root))

    for path, text in notes.items():
        assert (root / path).read_text() == text
    assert statuses(result)[('sentinel', '.meta-notes')] == 'created'
    assert statuses(result)[('template', 'resource/template/daily.md')] == 'exists'
    assert statuses(result)[('template', 'resource/template/weekly.md')] == 'created'


def test_init_modified_template_kept(tmp_path, skills):
    """Without --force an edited template is kept."""
    root = tmp_path / 'n'
    init.init(str(root))
    daily = root / 'resource' / 'template' / 'daily.md'
    daily.write_text('edited\n')

    init.init(str(root))

    assert daily.read_text() == 'edited\n'


def test_init_force_restores_templates_only(tmp_path, skills):
    """--force restores templates and leaves notes and the sentinel alone."""
    root = tmp_path / 'n'
    init.init(str(root))
    daily = root / 'resource' / 'template' / 'daily.md'
    daily.write_text('edited\n')
    (root / 'project' / 'foo.md').write_text('# note\n')
    (root / '.meta-notes').write_text('custom\n')

    result = init.init(str(root), force=True)

    assert daily.read_bytes() == (FIXTURES / 'daily.md').read_bytes()
    assert (root / 'project' / 'foo.md').read_text() == '# note\n'
    assert (root / '.meta-notes').read_text() == 'custom\n'
    assert statuses(result)[('template', 'resource/template/daily.md')] == 'overwritten'


# Tests for init function: nesting

def test_init_inside_existing_root_fails(tmp_path, skills):
    """Init in a subfolder of a root fails and changes nothing."""
    root = tmp_path / 'n'
    init.init(str(root))

    with pytest.raises(init.InitError, match='inside existing notes root'):
        init.init(str(root / 'project' / 'foo'))

    assert not (root / 'project' / 'foo').exists()


def test_init_force_does_not_allow_nesting(tmp_path, skills):
    """--force doesn't override the nesting check."""
    root = tmp_path / 'n'
    init.init(str(root))
    (root / 'project' / 'foo').mkdir()

    with pytest.raises(init.InitError, match='inside existing notes root'):
        init.init(str(root / 'project' / 'foo'), force=True)

    assert list((root / 'project' / 'foo').iterdir()) == []


def test_init_nested_check_ignores_root_above_home(tmp_path, skills):
    """A root above $HOME doesn't block init below it."""
    init.init(str(tmp_path / 'outer'))
    home = tmp_path / 'outer' / 'home'
    home.mkdir()

    init.init(str(home / 'notes'), home=str(home))

    assert (home / 'notes' / '.meta-notes').is_file()


# Tests for init function: skills

def test_init_skill_link_target(tmp_path, skills):
    """The skill link resolves to the plugin's copy."""
    init.init(str(tmp_path / 'n'))
    link = tmp_path / 'n' / '.claude' / 'skills' / 'review'
    assert os.path.realpath(link) == os.path.realpath(skills / 'review')


def test_init_skill_plugin_edit_visible(tmp_path, skills):
    """Changing the plugin's skill is visible through the link."""
    init.init(str(tmp_path / 'n'))
    (skills / 'review' / 'SKILL.md').write_text('v2\n')
    link = tmp_path / 'n' / '.claude' / 'skills' / 'review'
    assert (link / 'SKILL.md').read_text() == 'v2\n'


def test_init_skill_stale_link_repointed(tmp_path, skills):
    """A broken link is repointed."""
    target = tmp_path / 'n' / '.claude' / 'skills'
    target.mkdir(parents=True)
    (target / 'review').symlink_to(tmp_path / 'gone')

    result = init.init(str(tmp_path / 'n'))

    assert os.path.realpath(target / 'review') == os.path.realpath(skills / 'review')
    assert statuses(result)[('skill', '.claude/skills/review')] == 'repointed'


def test_init_skill_foreign_link_repointed(tmp_path, skills):
    """A link to another existing directory is repointed."""
    other = tmp_path / 'other-checkout'
    other.mkdir()
    target = tmp_path / 'n' / '.claude' / 'skills'
    target.mkdir(parents=True)
    (target / 'review').symlink_to(other)

    result = init.init(str(tmp_path / 'n'))

    assert os.path.realpath(target / 'review') == os.path.realpath(skills / 'review')
    assert other.is_dir()
    assert statuses(result)[('skill', '.claude/skills/review')] == 'repointed'


def test_init_skill_relative_link_counts_as_exists(tmp_path, skills):
    """A relative link that reaches the plugin's copy is left alone."""
    target = tmp_path / 'n' / '.claude' / 'skills'
    target.mkdir(parents=True)
    rel = os.path.relpath(skills / 'review', target)
    (target / 'review').symlink_to(rel)

    result = init.init(str(tmp_path / 'n'))

    assert os.readlink(target / 'review') == rel
    assert statuses(result)[('skill', '.claude/skills/review')] == 'exists'


def test_init_skill_real_directory_skipped(tmp_path, skills):
    """A real directory is kept, with a warning."""
    target = tmp_path / 'n' / '.claude' / 'skills' / 'review'
    target.mkdir(parents=True)
    (target / 'SKILL.md').write_text('mine\n')

    result = init.init(str(tmp_path / 'n'))

    assert not target.is_symlink()
    assert (target / 'SKILL.md').read_text() == 'mine\n'
    assert statuses(result)[('skill', '.claude/skills/review')] == 'skipped'
    assert any('.claude/skills/review' in w for w in result.warnings)


def test_init_skill_force_replaces_real_directory(tmp_path, skills):
    """--force replaces a real directory with the link."""
    target = tmp_path / 'n' / '.claude' / 'skills' / 'review'
    target.mkdir(parents=True)
    (target / 'SKILL.md').write_text('mine\n')

    result = init.init(str(tmp_path / 'n'), force=True)

    assert target.is_symlink()
    assert statuses(result)[('skill', '.claude/skills/review')] == 'replaced'


def test_init_skill_force_replaces_real_file(tmp_path, skills):
    """--force replaces a regular file with the link."""
    target = tmp_path / 'n' / '.claude' / 'skills'
    target.mkdir(parents=True)
    (target / 'review').write_text('file\n')

    init.init(str(tmp_path / 'n'), force=True)

    assert (target / 'review').is_symlink()


def test_init_warns_when_cli_not_on_path(tmp_path, skills, monkeypatch):
    """Init succeeds but warns, with the link command, if meta-notes isn't on PATH."""
    monkeypatch.setattr(init, 'cli_on_path', lambda: False)
    (tmp_path / 'n').mkdir()
    (tmp_path / 'n' / '.gitignore').write_text('')

    result = init.init(str(tmp_path / 'n'))

    assert len(result.warnings) == 1
    assert 'not on PATH' in result.warnings[0]
    assert str(init.CLI_PATH) in result.warnings[0]


def test_cli_on_path_finds_command(tmp_path, monkeypatch):
    """cli_on_path is true only when an executable meta-notes is on PATH."""
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    monkeypatch.setenv('PATH', str(bin_dir))
    assert not REAL_CLI_ON_PATH()

    (bin_dir / 'meta-notes').symlink_to(init.CLI_PATH)
    assert REAL_CLI_ON_PATH()


def test_init_shipped_skills_includes_project_review():
    """The real plugin ships project-review."""
    assert 'project-review' in init.shipped_skills()


def test_init_shipped_skills_includes_calendar():
    """The real plugin ships calendar."""
    assert 'calendar' in init.shipped_skills()


# Tests for init function: cache folder

def test_init_cache_folders_created(tmp_path, skills):
    """The cache folder, ics/, and calendar/ are created and reported."""
    root = tmp_path / 'n'

    result = init.init(str(root))

    for folder in ('.meta-notes-cache', '.meta-notes-cache/ics',
                   '.meta-notes-cache/calendar'):
        assert (root / folder).is_dir()
        assert statuses(result)[('folder', folder)] == 'created'
    assert statuses(result)[('cache-readme', '.meta-notes-cache/README.md')] == 'created'


def test_init_force_keeps_exports(tmp_path, skills):
    """--force leaves exports and cached calendars alone."""
    root = tmp_path / 'n'
    init.init(str(root))
    export = root / '.meta-notes-cache' / 'ics' / 'export.zip'
    export.write_bytes(b'zip data')
    cached = root / '.meta-notes-cache' / 'calendar' / 'abc.ics'
    cached.write_text('BEGIN:VCALENDAR\n')

    init.init(str(root), force=True)

    assert export.read_bytes() == b'zip data'
    assert cached.read_text() == 'BEGIN:VCALENDAR\n'


def test_init_cache_readme_edit_kept_then_restored(tmp_path, skills):
    """An edited cache README is kept without --force and restored with it."""
    root = tmp_path / 'n'
    init.init(str(root))
    readme = root / '.meta-notes-cache' / 'README.md'
    readme.write_text('mine\n')

    result = init.init(str(root))
    assert readme.read_text() == 'mine\n'
    assert statuses(result)[('cache-readme', '.meta-notes-cache/README.md')] == 'exists'

    result = init.init(str(root), force=True)
    assert readme.read_bytes() == (init.TEMPLATES_DIR / 'cache-README.md').read_bytes()
    assert statuses(result)[('cache-readme', '.meta-notes-cache/README.md')] == 'overwritten'


def test_init_force_keeps_config(tmp_path, skills):
    """--force doesn't change a .meta-notes with settings."""
    root = tmp_path / 'n'
    init.init(str(root))
    config = init.SENTINEL_CONTENT + '\n[calendar]\nemail = "me@example.com"\n'
    (root / '.meta-notes').write_text(config)

    init.init(str(root), force=True)

    assert (root / '.meta-notes').read_text() == config


# Tests for init function: virtualenv

def test_init_venv_first_init(tmp_path, skills, commands):
    """Without .venv, python3 builds it and pip installs requirements.txt."""
    root = tmp_path / 'n'

    result = init.init(str(root))

    assert statuses(result)[('venv', '.venv')] == 'created'
    assert commands.calls == [
        ['python3', '-c', "import sys; print('%d.%d' % sys.version_info[:2])"],
        ['python3', '-m', 'venv', '--prompt', 'meta-notes', '.venv'],
        ['.venv/bin/python3', '-m', 'pip', 'install', '-r',
         str(init.REQUIREMENTS)],
    ]
    assert (root / '.venv' / 'bin' / 'python3').is_file()
    assert not [w for w in result.warnings if 'Calendar' in w]


def test_init_venv_explicit_interpreter(tmp_path, skills, commands):
    """--python builds .venv with the given interpreter."""
    root = tmp_path / 'n'

    init.init(str(root), python='/opt/python3.12/bin/python3')

    assert commands.calls[1][0] == '/opt/python3.12/bin/python3'
    assert (root / '.venv' / 'bin' / 'python3').read_text() == \
        'python from /opt/python3.12/bin/python3\n'


def test_init_venv_existing_left_alone(tmp_path, skills, commands):
    """An existing .venv is left alone, even with --python."""
    root = tmp_path / 'n'
    (root / '.venv' / 'bin').mkdir(parents=True)
    (root / '.venv' / 'bin' / 'python3').write_text('old\n')

    result = init.init(str(root), python='/opt/python3.12/bin/python3')

    assert statuses(result)[('venv', '.venv')] == 'exists'
    assert commands.calls == []
    assert (root / '.venv' / 'bin' / 'python3').read_text() == 'old\n'


def test_init_venv_force_rebuild(tmp_path, skills, commands):
    """--force deletes .venv and builds it again."""
    root = tmp_path / 'n'
    (root / '.venv' / 'lib').mkdir(parents=True)
    (root / '.venv' / 'lib' / 'stale').write_text('stale\n')

    result = init.init(str(root), force=True)

    assert statuses(result)[('venv', '.venv')] == 'rebuilt'
    assert not (root / '.venv' / 'lib' / 'stale').exists()
    assert (root / '.venv' / 'bin' / 'python3').is_file()
    assert len(commands.calls) == 3


def test_init_venv_python_too_old(tmp_path, skills, commands):
    """Python 3.10 creates no .venv and warns that 3.11 is required."""
    commands.version = '3.10'
    root = tmp_path / 'n'

    result = init.init(str(root))

    assert not (root / '.venv').exists()
    assert statuses(result)[('venv', '.venv')] == 'skipped'
    assert (root / '.meta-notes').is_file()
    warning = [w for w in result.warnings if 'Calendar support' in w]
    assert len(warning) == 1
    assert '3.11 or newer is required' in warning[0]
    assert 'Python 3.10' in warning[0]


def test_init_venv_force_with_old_python_keeps_venv(tmp_path, skills, commands):
    """--force doesn't delete .venv when the interpreter is too old to rebuild it."""
    commands.version = '3.10'
    root = tmp_path / 'n'
    (root / '.venv' / 'bin').mkdir(parents=True)

    init.init(str(root), force=True)

    assert (root / '.venv' / 'bin').is_dir()


def test_init_venv_missing_interpreter(tmp_path, skills, commands):
    """A missing interpreter is a warning naming it, not an error."""
    commands.missing = {'/nope/python3'}
    root = tmp_path / 'n'

    result = init.init(str(root), python='/nope/python3')

    assert not (root / '.venv').exists()
    warning = [w for w in result.warnings if 'Calendar support' in w]
    assert len(warning) == 1
    assert '/nope/python3' in warning[0]


def test_init_venv_create_fails(tmp_path, skills, commands):
    """A failed venv build warns with the command and its output, and leaves no .venv."""
    commands.fail['venv'] = 'Error: ensurepip is not available\n'
    root = tmp_path / 'n'

    result = init.init(str(root))

    assert not (root / '.venv').exists()
    warning = [w for w in result.warnings if 'Calendar support' in w]
    assert '-m venv --prompt meta-notes .venv' in warning[0]
    assert 'ensurepip is not available' in warning[0]


def test_init_venv_install_fails(tmp_path, skills, commands):
    """A failed pip install keeps .venv and says to run init --force."""
    commands.fail['pip'] = 'ERROR: No matching distribution found for icalendar\n'
    root = tmp_path / 'n'

    result = init.init(str(root))

    assert (root / '.venv' / 'bin' / 'python3').is_file()
    warning = [w for w in result.warnings if 'Calendar support' in w]
    assert len(warning) == 1
    assert 'No matching distribution found for icalendar' in warning[0]
    assert 'meta-notes init --force' in warning[0]


# Tests for init function: .gitignore

def test_init_gitignore_entries_appended(tmp_path, skills):
    """Missing entries are appended, keeping existing lines."""
    root = tmp_path / 'n'
    root.mkdir()
    (root / '.gitignore').write_text('*.swp\n')

    result = init.init(str(root))

    assert (root / '.gitignore').read_text() == '*.swp\n.venv/\n.meta-notes-cache/\n'
    assert statuses(result)[('gitignore', '.venv/')] == 'created'
    assert statuses(result)[('gitignore', '.meta-notes-cache/')] == 'created'
    assert not [w for w in result.warnings if '.gitignore' in w]


@pytest.mark.parametrize('line', ['.venv', '.venv/', '/.venv', '/.venv/',
                                  '  /.venv  '])
def test_init_gitignore_existing_entry_recognized(tmp_path, skills, line):
    """An existing .venv line in any form is recognized."""
    root = tmp_path / 'n'
    root.mkdir()
    (root / '.gitignore').write_text(f'{line}\n')

    result = init.init(str(root))

    assert (root / '.gitignore').read_text() == f'{line}\n.meta-notes-cache/\n'
    assert statuses(result)[('gitignore', '.venv/')] == 'exists'


def test_init_gitignore_rerun_adds_nothing(tmp_path, skills):
    """A second run leaves .gitignore as the first run did."""
    root = tmp_path / 'n'
    root.mkdir()
    (root / '.gitignore').write_text('*.swp\n')
    init.init(str(root))
    after_first = (root / '.gitignore').read_text()

    result = init.init(str(root))

    assert (root / '.gitignore').read_text() == after_first
    assert statuses(result)[('gitignore', '.meta-notes-cache/')] == 'exists'


def test_init_gitignore_missing(tmp_path, skills):
    """With no .gitignore, none is created and a warning names both entries."""
    root = tmp_path / 'n'

    result = init.init(str(root))

    assert not (root / '.gitignore').exists()
    warning = [w for w in result.warnings if '.gitignore' in w]
    assert len(warning) == 1
    assert '.venv/' in warning[0] and '.meta-notes-cache/' in warning[0]
    assert statuses(result)[('gitignore', '.venv/')] == 'skipped'


def test_init_gitignore_no_trailing_newline(tmp_path, skills):
    """A newline is added before the entries when the file lacks one."""
    root = tmp_path / 'n'
    root.mkdir()
    (root / '.gitignore').write_text('*.swp')

    init.init(str(root))

    assert (root / '.gitignore').read_text() == '*.swp\n.venv/\n.meta-notes-cache/\n'


# Tests for the init subcommand

def test_cli_init_current_directory(tmp_path, skills, capsys):
    """Without --root, the current directory is initialized."""
    code, out, err = run_json(capsys, ['init'])

    assert code == 0
    assert out['ok'] is True
    assert (tmp_path / '.meta-notes').is_file()
    assert err == ''


def test_cli_init_root_option(tmp_path, skills, capsys):
    """--root names the directory, creating it if missing."""
    code, out, _ = run_json(capsys, ['init', '--root', str(tmp_path / 'a' / 'b')])

    assert code == 0
    assert out['root'] == str(tmp_path / 'a' / 'b')
    assert (tmp_path / 'a' / 'b' / '.meta-notes').is_file()


def test_cli_init_ignores_meta_notes_root(tmp_path, skills, monkeypatch, capsys):
    """META_NOTES_ROOT doesn't change where init runs."""
    other = tmp_path / 'other'
    init.init(str(other))
    here = tmp_path / 'here'
    here.mkdir()
    monkeypatch.chdir(here)
    monkeypatch.setenv('META_NOTES_ROOT', str(other))
    before = sorted(p.name for p in other.iterdir())

    code, _, _ = run_json(capsys, ['init'])

    assert code == 0
    assert (here / '.meta-notes').is_file()
    assert sorted(p.name for p in other.iterdir()) == before


def test_cli_init_json_report(tmp_path, skills, capsys):
    """The JSON report lists every item as created."""
    code, out, _ = run_json(capsys, ['init', '--root', str(tmp_path / 'n')])

    assert code == 0
    kinds = {(i['kind'], i['path']) for i in out['items']}
    assert {('folder', f) for f in init.FOLDERS} <= kinds
    assert ('sentinel', '.meta-notes') in kinds
    assert ('skill', '.claude/skills/review') in kinds
    assert ('cache-readme', '.meta-notes-cache/README.md') in kinds
    assert ('venv', '.venv') in kinds
    assert all(i['status'] == 'created' for i in out['items']
               if i['kind'] != 'gitignore')
    # The only warning is the missing .gitignore
    assert len(out['warnings']) == 1
    assert '.gitignore' in out['warnings'][0]


def test_cli_init_skipped_skill_is_warning(tmp_path, skills, capsys):
    """A skipped skill is a warning, and the command succeeds."""
    (tmp_path / 'n' / '.claude' / 'skills' / 'review').mkdir(parents=True)
    (tmp_path / 'n' / '.gitignore').write_text('')

    code, out, _ = run_json(capsys, ['init', '--root', str(tmp_path / 'n')])

    assert code == 0
    assert len(out['warnings']) == 1


def test_cli_init_nested_error(tmp_path, skills, capsys):
    """Nesting is a JSON error with a non-zero exit."""
    init.init(str(tmp_path / 'n'))

    code, out, _ = run_json(capsys, ['init', '--root', str(tmp_path / 'n' / 'project')])

    assert code == 1
    assert 'inside existing notes root' in out['error']


def test_cli_init_text_output(tmp_path, skills, capsys):
    """Text output has one line per item and a completion line."""
    code = cli.main(['init'])
    out = capsys.readouterr().out.splitlines()

    assert code == 0
    assert 'Created directory: project' in out
    assert 'Created template: resource/template/daily.md' in out
    assert 'Created notes root marker: .meta-notes' in out
    assert 'Linked skill: .claude/skills/review' in out
    assert 'Created cache README: .meta-notes-cache/README.md' in out
    assert 'Created virtualenv: .venv' in out
    assert out[-1] == 'Meta-notes initialization complete!'


def test_cli_init_text_output_existing_venv(tmp_path, skills, capsys):
    """An existing .venv is reported as left alone, with --force to rebuild."""
    (tmp_path / '.venv').mkdir()
    (tmp_path / '.gitignore').write_text('')

    code = cli.main(['init'])
    out = capsys.readouterr().out.splitlines()

    assert code == 0
    assert ('Virtualenv already exists, left alone (--force rebuilds it): .venv'
            in out)
    assert 'Added to .gitignore: .venv/' in out


def test_cli_init_python_option(tmp_path, skills, commands, capsys):
    """--python is passed through to the virtualenv build."""
    code, _, _ = run_json(capsys, ['init', '--python', '/opt/py/bin/python3'])

    assert code == 0
    assert commands.calls[0][0] == '/opt/py/bin/python3'


def test_cli_other_commands_find_initialized_root(tmp_path, skills, monkeypatch, capsys):
    """After init, other commands find the root from a subfolder."""
    init.init(str(tmp_path / 'n'))
    monkeypatch.chdir(tmp_path / 'n' / 'project')

    code, out, _ = run_json(capsys, ['tasks'])

    assert code == 0
    assert out['ok'] is True
