"""
Unit tests for scripts/meta_notes/brief.py
"""

import os
import sys
import time
from datetime import date
from pathlib import Path

import pytest

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import brief, projects

TODAY = date(2026, 9, 25)


def write_notes(root, notes):
    for path, text in notes.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)


def build(root, monkeypatch, path, **kwargs):
    monkeypatch.chdir(root)
    return brief.build('.', path, today=TODAY, **kwargs)


def texts(tasks):
    return [t['text'] for t in tasks]


# Tests for resolve function

def test_resolve_note_project_without_extension(tmp_path):
    write_notes(tmp_path, {'project/make-bread.md': '# Make Bread\n'})

    assert brief.resolve(str(tmp_path), 'project/make-bread') == 'project/make-bread.md'


def test_resolve_folder_project(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/kitchen/Home.md': '# Kitchen\n'})

    b = build(tmp_path, monkeypatch, 'project/kitchen/')

    assert b['path'] == 'project/kitchen/'
    assert b['home'] == 'project/kitchen/Home.md'


def test_resolve_absolute_path_inside_root(tmp_path):
    write_notes(tmp_path, {'archive/project/old.md': '# Old\n'})

    assert (brief.resolve(str(tmp_path), str(tmp_path / 'archive/project/old.md'))
            == 'archive/project/old.md')


def test_resolve_area_rejected(tmp_path):
    write_notes(tmp_path, {'area/health.md': '# Health\n'})

    with pytest.raises(ValueError, match='area/health is not a project'):
        brief.resolve(str(tmp_path), 'area/health')


def test_resolve_nested_note_rejected(tmp_path):
    write_notes(tmp_path, {'project/kitchen/Home.md': '# Kitchen\n',
                           'project/kitchen/Tasks.md': '# Tasks\n'})

    with pytest.raises(ValueError, match='project/kitchen/Tasks.md is not a project'):
        brief.resolve(str(tmp_path), 'project/kitchen/Tasks.md')


def test_resolve_missing_path_rejected(tmp_path):
    (tmp_path / 'project').mkdir()

    with pytest.raises(ValueError, match='project/nope is not a project'):
        brief.resolve(str(tmp_path), 'project/nope')


def test_resolve_path_outside_root_rejected(tmp_path):
    root = tmp_path / 'notes'
    write_notes(tmp_path, {'project/a.md': '# A\n'})
    root.mkdir()

    with pytest.raises(ValueError, match='is not a project'):
        brief.resolve(str(root), str(tmp_path / 'project/a.md'))


# Tests for home note, fields, dates, and warnings

def test_build_fields_reported(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/make-bread.md':
                           '# Make Bread\n\n- status: paused\n- tag: make-bread\n'
                           '- owner: me\n'})

    b = build(tmp_path, monkeypatch, 'project/make-bread')

    assert (b['status'], b['tag'], b['home']) == ('paused', 'make-bread',
                                                  'project/make-bread.md')
    assert b['fields'] == {'status': 'paused', 'tag': 'make-bread', 'owner': 'me'}


def test_build_folder_without_home_note(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/trip/Packing.md': '# Packing\n'})

    b = build(tmp_path, monkeypatch, 'project/trip')

    assert b['home'] is None
    assert b['status'] == 'active'
    assert b['tag'] is None
    assert b['fields'] == {}
    assert 'no-home-note' in b['warnings']


def test_build_same_answers_as_project_list(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'project/make-bread.md': '# Make Bread\n\n- tag: make-bread\n\n'
                                 '## Notes 2026-08-01\n'
                                 '- [x] project #review 📅 ✅ 2026-08-10\n',
        'project/kitchen/Home.md': '# Kitchen\n\n- [ ] #next call 📅 2026-09-30\n',
        'project/kitchen/2026-09-18.md': '# Meeting\n',
        'plan/daily/26-Q3/2026-09-20 Sun.md':
            '- [x] #make-bread buy flour 📅 2026-09-20\n',
    })
    monkeypatch.chdir(tmp_path)
    _, entries = projects.run('.', today=TODAY)

    for entry in entries:
        b = brief.build('.', entry['path'], today=TODAY)
        assert (b['latest_date'], b['last_review'], b['warnings']) == (
            entry['latest_date'], entry['last_review'], entry['warnings'])


def test_build_review_does_not_count_as_activity(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n## Notes 2026-04-01\n\n'
                           '- [x] project #review 📅 ✅ 2026-09-20\n'})

    b = build(tmp_path, monkeypatch, 'project/a')

    assert b['latest_date'] == '2026-04-01'
    assert b['last_review'] == '2026-09-20'


def test_build_archived_project(tmp_path, monkeypatch):
    write_notes(tmp_path, {'archive/project/old/Home.md':
                           '# Old\n\n- status: archived\n'})

    b = build(tmp_path, monkeypatch, 'archive/project/old')

    assert b['path'] == 'archive/project/old/'
    assert b['status'] == 'archived'


# Tests for the file list

def test_build_folder_files(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'project/kitchen/Home.md': '# Kitchen\n',
        'project/kitchen/meetings/2026-09-18.md': '# Meeting\n',
        'project/kitchen/plan.pdf': 'pdf',
        'project/kitchen/.hidden': 'x',
        'project/kitchen/.git/config': 'x',
    })

    b = build(tmp_path, monkeypatch, 'project/kitchen')

    assert [f['path'] for f in b['files']] == [
        'project/kitchen/Home.md',
        'project/kitchen/meetings/2026-09-18.md',
        'project/kitchen/plan.pdf',
    ]
    assert b['files'][2]['size'] == 3
    today = date.today().isoformat()
    assert all(f['modified'] == today for f in b['files'])


def test_build_note_project_files(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/make-bread.md': '# Make Bread\n',
                           'project/other.md': '# Other\n'})

    b = build(tmp_path, monkeypatch, 'project/make-bread.md')

    assert [f['path'] for f in b['files']] == ['project/make-bread.md']


def test_build_recent_modification_not_activity(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': '# A\n\n## Notes 2026-03-02\n'})
    stamp = time.mktime((2026, 9, 25, 12, 0, 0, 0, 0, -1))
    os.utime(tmp_path / 'project/a.md', (stamp, stamp))

    b = build(tmp_path, monkeypatch, 'project/a')

    assert b['files'][0]['modified'] == '2026-09-25'
    assert b['latest_date'] == '2026-03-02'


# Tests for task lists

def test_build_tagged_task_elsewhere(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'project/make-bread.md': '# Make Bread\n\n- tag: make-bread\n',
        'plan/daily/26-Q3/2026-09-24.md':
            '- [ ] #make-bread buy flour 📅 2026-09-26\n',
    })

    b = build(tmp_path, monkeypatch, 'project/make-bread')

    assert texts(b['open']) == ['- [ ] #make-bread buy flour 📅 2026-09-26']
    assert b['open'][0]['file'] == 'plan/daily/26-Q3/2026-09-24.md'
    assert b['open'][0]['line'] == 1
    assert 'section' not in b['open'][0]


def test_build_plain_checkbox_ignored(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': '# A\n\n- [ ] buy a banneton\n'})

    b = build(tmp_path, monkeypatch, 'project/a')

    assert b['open'] == []


def test_build_canceled_task_left_out(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n- [-] rent a mixer 📅 2026-08-01\n'
                           '- [>] moved 📅 2026-08-02\n'})

    b = build(tmp_path, monkeypatch, 'project/a')

    assert b['open'] == b['completed'] == b['later'] == []
    assert b['completed_total'] == 0


def test_build_later_listed_separately(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n- [ ] #later try rye 📅\n'
                           '- [ ] buy flour 📅 2026-09-26\n'})

    b = build(tmp_path, monkeypatch, 'project/a')

    assert texts(b['later']) == ['- [ ] #later try rye 📅']
    assert texts(b['open']) == ['- [ ] buy flour 📅 2026-09-26']


def test_build_deadline_and_scheduled_review(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n- [ ] Bake for the party #deadline 📅 2026-10-30\n'
                           '- [ ] project #review 📅 2026-11-01\n'})

    b = build(tmp_path, monkeypatch, 'project/a')

    assert [(t['text'], t['due']) for t in b['deadlines']] == [
        ('- [ ] Bake for the party #deadline 📅 2026-10-30', '2026-10-30')]
    assert [(t['text'], t['due']) for t in b['scheduled_reviews']] == [
        ('- [ ] project #review 📅 2026-11-01', '2026-11-01')]
    assert len(b['open']) == 2


def test_build_unscheduled_review_not_listed_as_scheduled(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': '# A\n\n- [ ] project #review 📅\n'})

    b = build(tmp_path, monkeypatch, 'project/a')

    assert b['scheduled_reviews'] == []
    assert len(b['open']) == 1


def test_build_no_next_action(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': '# A\n\n- [ ] buy flour 📅 2026-09-26\n'})

    b = build(tmp_path, monkeypatch, 'project/a')

    assert b['has_next'] is False
    assert 'no-next' in b['warnings']


def test_build_has_next(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': '# A\n\n- [ ] #next buy flour 📅 2026-09-26\n'})

    b = build(tmp_path, monkeypatch, 'project/a')

    assert b['has_next'] is True
    assert 'no-next' not in b['warnings']


COMPLETED_NOTE = ('# A\n\n- [x] early 📅 ✅ 2026-05-01\n'
                  '- [x] mid 📅 ✅ 2026-07-01\n')


def test_build_default_window(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': COMPLETED_NOTE})

    b = build(tmp_path, monkeypatch, 'project/a')

    assert b['since'] == '2026-06-27'
    assert texts(b['completed']) == ['- [x] mid 📅 ✅ 2026-07-01']
    assert b['completed_total'] == 2


def test_build_since(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': COMPLETED_NOTE})

    b = build(tmp_path, monkeypatch, 'project/a', since=date(2026, 1, 1))

    assert b['since'] == '2026-01-01'
    assert len(b['completed']) == 2


def test_build_due_date_stands_in(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': '# A\n\n- [x] order flour 📅 2026-09-20\n'})

    b = build(tmp_path, monkeypatch, 'project/a')

    assert [(t['text'], t['due'], t['completed']) for t in b['completed']] == [
        ('- [x] order flour 📅 2026-09-20', '2026-09-20', None)]


def test_build_undated_completed_counted_not_listed(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': '# A\n\n- [x] someday 📅\n'})

    b = build(tmp_path, monkeypatch, 'project/a')

    assert b['completed'] == []
    assert b['completed_total'] == 1


def test_build_tasks_sorted_by_file_then_line(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'project/kitchen/Home.md': '# K\n\n- tag: kitchen\n\n'
                                   '- [ ] b 📅 2026-09-30\n- [ ] a 📅 2026-09-29\n',
        'plan/daily/26-Q3/2026-09-24.md': '- [ ] #kitchen c 📅 2026-09-26\n',
    })

    b = build(tmp_path, monkeypatch, 'project/kitchen')

    assert [(t['file'], t['line']) for t in b['open']] == [
        ('plan/daily/26-Q3/2026-09-24.md', 1),
        ('project/kitchen/Home.md', 5),
        ('project/kitchen/Home.md', 6),
    ]


def test_build_writes_nothing(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': COMPLETED_NOTE})
    before = {p: p.stat().st_mtime for p in tmp_path.rglob('*')}

    build(tmp_path, monkeypatch, 'project/a')

    assert {p: p.stat().st_mtime for p in tmp_path.rglob('*')} == before


# Tests for format_brief function

def test_format_brief_sections(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/make-bread.md':
                           '# Make Bread\n\n- tag: make-bread\n\n'
                           '- [ ] #next buy flour 📅 2026-09-26\n'
                           '- [ ] Bake #deadline 📅 2026-10-30\n'
                           '- [x] order yeast 📅 ✅ 2026-09-20\n'
                           '- [x] old 📅 ✅ 2026-01-02\n'})
    stamp = time.mktime((2026, 9, 25, 12, 0, 0, 0, 0, -1))
    os.utime(tmp_path / 'project/make-bread.md', (stamp, stamp))
    monkeypatch.chdir(tmp_path)

    lines, b = brief.run('.', 'project/make-bread', today=TODAY)

    size = b['files'][0]['size']
    assert lines == [
        'project/make-bread.md  active  #make-bread',
        'latest 2026-09-20  review never',
        'warnings: review-overdue',
        '',
        'Files',
        f'  {size}  2026-09-25  project/make-bread.md',
        '',
        'Deadlines',
        '  project/make-bread.md:6  - [ ] Bake #deadline 📅 2026-10-30',
        '',
        'Open',
        '  project/make-bread.md:5  - [ ] #next buy flour 📅 2026-09-26',
        '  project/make-bread.md:6  - [ ] Bake #deadline 📅 2026-10-30',
        '',
        'Completed (1 of 2 since 2026-06-27)',
        '  project/make-bread.md:7  - [x] order yeast 📅 ✅ 2026-09-20',
    ]


def test_format_brief_no_tag_or_warnings(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': '# A\n\n- status: paused\n\n## 2026-09-20\n'
                                           '- [x] project #review 📅 ✅ 2026-09-21\n'})
    monkeypatch.chdir(tmp_path)

    lines, _ = brief.run('.', 'project/a', today=TODAY)

    assert lines[:2] == ['project/a.md  paused  no tag',
                         'latest 2026-09-20  review 2026-09-21']
    assert lines[2] == ''
    assert [l for l in lines if l and not l.startswith(' ')] == [
        'project/a.md  paused  no tag', 'latest 2026-09-20  review 2026-09-21',
        'Files', 'Completed (1 of 1 since 2026-06-27)']
