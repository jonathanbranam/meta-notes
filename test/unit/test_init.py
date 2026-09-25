"""
Unit tests for scripts/meta_notes/init.py and the `init` subcommand

Tests folders, templates, the sentinel, skill install, re-runs, and nesting.
"""

import json
import os
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


@pytest.fixture(autouse=True)
def env(tmp_path, monkeypatch):
    """Isolate HOME and META_NOTES_ROOT, and restore the cwd init changes."""
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.chdir(tmp_path)


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


def run_json(capsys, argv):
    code = cli.main(argv + ['--json'])
    captured = capsys.readouterr()
    return code, json.loads(captured.out), captured.err


# Tests for shipped templates

@pytest.mark.parametrize('name', TEMPLATE_NAMES)
def test_templates_match_vim_output(name):
    """Shipped templates are byte-identical to what :MetaNotesInit wrote."""
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
    assert (root / '.claude' / 'skills' / 'review').is_symlink()
    assert not (root / '.claude' / 'skills' / 'not-a-skill').exists()
    assert set(statuses(result).values()) == {'created'}


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
    assert set(statuses(result).values()) == {'exists'}


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


def test_init_shipped_skills_includes_project_review():
    """The real plugin ships project-review."""
    assert 'project-review' in init.shipped_skills()


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
    assert all(i['status'] == 'created' for i in out['items'])
    assert out['warnings'] == []


def test_cli_init_skipped_skill_is_warning(tmp_path, skills, capsys):
    """A skipped skill is a warning, and the command succeeds."""
    (tmp_path / 'n' / '.claude' / 'skills' / 'review').mkdir(parents=True)

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
    assert out[-1] == 'Meta-notes initialization complete!'


def test_cli_other_commands_find_initialized_root(tmp_path, skills, monkeypatch, capsys):
    """After init, other commands find the root from a subfolder."""
    init.init(str(tmp_path / 'n'))
    monkeypatch.chdir(tmp_path / 'n' / 'project')

    code, out, _ = run_json(capsys, ['tasks'])

    assert code == 0
    assert out['ok'] is True
