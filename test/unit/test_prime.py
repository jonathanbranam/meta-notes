"""
Unit tests for scripts/meta_notes/prime.py and `meta-notes prime`
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

import pytest

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import cli, conventions, init, prime
from time_tracking import TAG_GROUPS

SATURDAY = date(2026, 9, 26)


@pytest.fixture
def notes_root(tmp_path, monkeypatch):
    """A notes root with its sentinel and the shipped templates, as the cwd."""
    template_dir = tmp_path / 'resource' / 'template'
    template_dir.mkdir(parents=True)
    for name in init.TEMPLATES:
        (template_dir / name).write_bytes((init.TEMPLATES_DIR / name).read_bytes())
    (tmp_path / '.meta-notes').write_text('# meta-notes notes root\n')
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def outside(tmp_path, monkeypatch):
    """A directory with no notes root above it, as the cwd."""
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.chdir(tmp_path)
    return tmp_path


def run_json(capsys, argv):
    code = cli.main(argv + ['--json'])
    captured = capsys.readouterr()
    return code, json.loads(captured.out)


# Tests for run function: generated parts

def test_run_replaces_every_marker(notes_root):
    source = prime.PRIME_FILE.read_text(encoding='utf-8')
    markers = prime.conventions.MARKER_PATTERN.findall(source)

    text = prime.run(str(notes_root), SATURDAY)

    assert sorted(markers) == sorted(prime.GENERATORS)
    assert '<!-- generated' not in text


def test_run_today_paths(notes_root):
    text = prime.run(str(notes_root), SATURDAY)

    assert '`plan/daily/26-Q3/2026-09-26 Sat.md`' in text
    assert '`plan/week/26-Q3/2026-09-21.md`' in text
    assert '`plan/quarter/2026-Q3.md`' in text
    assert '`plan/year/2026.md`' in text


def test_run_daily_sections_from_shipped_template(notes_root):
    text = prime.run(str(notes_root), SATURDAY)

    assert '- Follow Up\n- Time Tracking\n  - Log\n  - Time Block\n' in text


def test_run_edited_template(notes_root):
    daily = notes_root / 'resource' / 'template' / 'daily.md'
    daily.write_text(daily.read_text() + '\n## Wins\n')

    text = prime.run(str(notes_root), SATURDAY)

    assert '- Wins\n' in text


def test_run_missing_root_template_uses_shipped(notes_root):
    (notes_root / 'resource' / 'template' / 'weekly.md').unlink()

    text = prime.run(str(notes_root), SATURDAY)

    assert '- Review\n- Plan\n' in text


def test_run_lists_tag_groups():
    text = prime.run(None, SATURDAY)

    for group, tags in TAG_GROUPS.items():
        line = f"- {group}: " + ", ".join(f"`{t}`" for t in sorted(tags))
        assert line in text


def test_run_lists_shipped_skills(monkeypatch, tmp_path):
    skills_dir = tmp_path / 'skills'
    for name in ('calendar', 'daily-plan'):
        (skills_dir / name).mkdir(parents=True)
        (skills_dir / name / 'SKILL.md').write_text('x\n')
    monkeypatch.setattr(init, 'SKILLS_DIR', skills_dir)

    text = prime.run(None, SATURDAY)

    assert '- `calendar`\n- `daily-plan`\n' in text


def test_run_includes_conventions(notes_root):
    text = prime.run(str(notes_root), SATURDAY)

    assert conventions.run() in text + '\n'


def test_render_unknown_marker_raises():
    with pytest.raises(KeyError):
        prime.render('<!-- generated: nope -->', None, SATURDAY)


# Tests for template_sections function

def test_template_sections_skips_front_matter_and_title():
    text = '---\nfilename_pattern: "# x"\n---\n# Title\n## A\n### B\n'

    assert prime.template_sections(text) == [(2, 'A'), (3, 'B')]


# Tests for run function: content

def test_run_covers_required_topics(notes_root):
    text = prime.run(str(notes_root), SATURDAY)

    for phrase in ('`plan/`', '`project/`', '`area/`', '`resource/`',
                   '`archive/`', '`resource/template/`',
                   'lowercase, with dashes', 'Title Case',
                   '`Home.md`', '`Tasks.md`', '`Meetings & Notes.md`',
                   'newest first', '`meta-notes projects`',
                   '`meta-notes project brief',
                   'meta-notes move project/<name> area/<name>',
                   'meta-notes note daily|weekly|quarterly|yearly',
                   '`archive/project/kitchen-remodel/`',
                   '`status: archived`', 'meta-notes archive <path>',
                   '08:00 to 17:00, Monday to Friday', '18:00',
                   '### Log', 'start:', 'end:', '### Time Block',
                   "root's `CLAUDE.md`"):
        assert phrase in text, phrase


@pytest.mark.parametrize('command', [
    'tasks', 'projects', 'project brief', 'changes', 'calendar',
    'ceremony status', 'time'])
def test_run_lists_finding_command(notes_root, command):
    text = prime.run(str(notes_root), SATURDAY)

    assert f"| `{command}` | `meta-notes {command}" in text


def test_run_inside_root_has_no_no_root_line(notes_root):
    assert not prime.run(str(notes_root), SATURDAY).startswith('>')


def test_run_size_budget(notes_root):
    assert len(prime.run(str(notes_root), SATURDAY)) <= 20_000


# Tests for the prime command

def test_prime_inside_notes_root(notes_root, capsys):
    (notes_root / 'project' / 'kitchen').mkdir(parents=True)
    os.chdir(notes_root / 'project' / 'kitchen')

    code = cli.main(['prime'])
    out = capsys.readouterr().out

    assert code == 0
    assert out.startswith('# meta-notes guide')
    assert len(out) <= 20_000


def test_prime_json(notes_root, capsys):
    code, data = run_json(capsys, ['prime'])

    assert code == 0
    assert data['ok'] is True
    assert data['version'] == cli.__version__
    assert data['root'] == str(notes_root.resolve())
    assert data['text'].startswith('# meta-notes guide')


def test_prime_no_notes_root(outside, capsys):
    code, data = run_json(capsys, ['prime'])

    assert code == 0
    assert data['ok'] is True
    assert data['root'] is None
    assert data['text'].startswith('> No notes root found')
    assert 'meta-notes init' in data['text'].split('\n')[0]


def test_prime_explicit_root_must_exist(outside, capsys):
    code, data = run_json(capsys, ['prime', '--root', str(outside / 'nope')])

    assert code == 1
    assert data['ok'] is False
