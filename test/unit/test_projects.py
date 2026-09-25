"""
Unit tests for scripts/meta_notes/projects.py
"""

import sys
from datetime import date
from pathlib import Path

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import projects

TODAY = date(2026, 9, 25)


def write_notes(root, notes):
    for path, text in notes.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)


def run(root, monkeypatch, **kwargs):
    monkeypatch.chdir(root)
    _, entries = projects.run('.', today=TODAY, **kwargs)
    return {e['path']: e for e in entries}


# Tests for list_projects function

def test_list_projects_note_and_folder(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'project/make-bread.md': '# Make Bread\n',
        'project/kitchen/Home.md': '# Kitchen\n',
        'project/kitchen/notes.md': 'notes\n',
    })
    monkeypatch.chdir(tmp_path)

    found = projects.list_projects('.')

    assert [(p.path, p.home) for p in found] == [
        ('project/kitchen/', 'project/kitchen/Home.md'),
        ('project/make-bread.md', 'project/make-bread.md'),
    ]


def test_list_projects_folder_without_home_note(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/trip/Packing.md': '# Packing\n'})
    monkeypatch.chdir(tmp_path)

    found = projects.list_projects('.')

    assert len(found) == 1
    assert found[0].path == 'project/trip/'
    assert found[0].home is None
    assert found[0].status == 'active'
    assert found[0].warnings == ['no-home-note']


def test_list_projects_excludes_archive(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'project/live.md': '# Live\n',
        'archive/project/old.md': '# Old\n',
    })
    monkeypatch.chdir(tmp_path)

    assert [p.path for p in projects.list_projects('.')] == ['project/live.md']


def test_list_projects_skips_non_markdown_files(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/picture.png': 'x', 'project/a.md': '# A\n'})
    monkeypatch.chdir(tmp_path)

    assert [p.path for p in projects.list_projects('.')] == ['project/a.md']


def test_list_projects_no_project_folder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert projects.list_projects('.') == []


def test_list_projects_fields_read(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/make-bread.md':
                           '# Make Bread\n\n- status: paused\n- tag: make-bread\n'})
    monkeypatch.chdir(tmp_path)

    p = projects.list_projects('.')[0]

    assert (p.status, p.tag) == ('paused', 'make-bread')


def test_list_projects_field_keys_ignore_case(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': '# A\n\n- Status: paused\n- TAG: #a\n'})
    monkeypatch.chdir(tmp_path)

    p = projects.list_projects('.')[0]

    assert (p.status, p.tag) == ('paused', 'a')


def test_list_projects_no_fields(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': '# A\n\nSome text.\n'})
    monkeypatch.chdir(tmp_path)

    p = projects.list_projects('.')[0]

    assert (p.status, p.tag) == ('active', None)


def test_list_projects_ignores_frontmatter(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '---\nstatus: paused\n---\n# A\n'})
    monkeypatch.chdir(tmp_path)

    assert projects.list_projects('.')[0].status == 'active'


# Tests for load_project function

def test_load_project_archived_folder(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'archive/project/kitchen/Home.md': '# Kitchen\n\n- status: archived\n',
        'archive/project/kitchen/plan.pdf': 'x',
    })
    monkeypatch.chdir(tmp_path)

    p = projects.load_project('archive/project/kitchen', '.')

    assert p.path == 'archive/project/kitchen/'
    assert p.home == 'archive/project/kitchen/Home.md'
    assert p.status == 'archived'
    assert p.fields == {'status': 'archived'}
    assert p.files == ['archive/project/kitchen/Home.md',
                       'archive/project/kitchen/plan.pdf']


def test_load_project_not_a_project(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/picture.png': 'x'})
    monkeypatch.chdir(tmp_path)

    assert projects.load_project('project/picture.png', '.') is None
    assert projects.load_project('project/missing', '.') is None


# Tests for latest_date function

def test_latest_date_archived_project_own_dates_only(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'archive/project/2026-03-01-trip/Home.md': '# Trip\n',
        'archive/project/2026-03-01-trip/notes.md': '## Notes 2026-04-02\n',
    })
    monkeypatch.chdir(tmp_path)
    p = projects.load_project('archive/project/2026-03-01-trip/', '.')

    assert projects.latest_date(p, TODAY, '.') == date(2026, 4, 2)


# Tests for project tasks

def test_collect_tagged_task_elsewhere(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'project/make-bread.md': '# Make Bread\n\n- tag: make-bread\n',
        'plan/daily/26-Q3/2026-09-25 Fri.md':
            '- [ ] #make-bread buy flour 📅 2026-09-26\n',
    })

    e = run(tmp_path, monkeypatch)['project/make-bread.md']

    assert e['open_tasks'] == 1


def test_collect_tagged_task_counted_once(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/make-bread.md':
                           '# Make Bread\n\n- tag: make-bread\n\n'
                           '- [ ] #make-bread buy flour 📅 2026-09-26\n'
                           '- [x] knead 📅 ✅ 2026-09-20\n'
                           '- [ ] not a task\n'})

    e = run(tmp_path, monkeypatch)['project/make-bread.md']

    assert (e['open_tasks'], e['completed_tasks']) == (1, 1)


def test_collect_untagged_project_only_own_tasks(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'project/kitchen/Home.md': '# Kitchen\n',
        'project/kitchen/todo.md': '- [ ] call plumber 📅 2026-09-26\n',
        'area/home.md': '- [ ] #kitchen measure 📅 2026-09-26\n',
    })

    e = run(tmp_path, monkeypatch)['project/kitchen/']

    assert e['open_tasks'] == 1


def test_collect_tag_alias_matches(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'project/a.md': '# A\n\n- tag: meeting\n',
        'area/b.md': '- [ ] #mtg prep 📅 2026-09-26\n',
    })

    assert run(tmp_path, monkeypatch)['project/a.md']['open_tasks'] == 1


# Tests for last review

def test_collect_latest_review_wins(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n- [x] project #review 📅 ✅ 2026-06-01\n'
                           '- [x] project #review 📅 ✅ 2026-09-03\n'})

    assert run(tmp_path, monkeypatch)['project/a.md']['last_review'] == '2026-09-03'


def test_collect_scheduled_review_not_done(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n- [ ] project #review 📅 2026-11-01\n'})

    e = run(tmp_path, monkeypatch)['project/a.md']

    assert e['last_review'] is None
    assert 'review-overdue' in e['warnings']


def test_collect_review_without_completed_date_uses_due(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n- [x] project #review 📅 2026-09-10\n'})

    assert run(tmp_path, monkeypatch)['project/a.md']['last_review'] == '2026-09-10'


# Tests for latest date

def test_collect_dated_meeting_note(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'project/kitchen/Home.md': '# Kitchen\n',
        'project/kitchen/meetings/2026-09-18.md': 'met the builder\n',
    })

    e = run(tmp_path, monkeypatch)['project/kitchen/']

    assert e['latest_date'] == '2026-09-18'


def test_collect_future_due_date_ignored(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n## Notes 2026-03-02\n\n'
                           '- [ ] order tiles 📅 2026-12-01\n'})

    assert run(tmp_path, monkeypatch)['project/a.md']['latest_date'] == '2026-03-02'


def test_collect_dated_heading(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/make-bread.md':
                           '# Make Bread\n\n## Notes 2026-09-10\n\ntext\n'})

    e = run(tmp_path, monkeypatch)['project/make-bread.md']

    assert e['latest_date'] == '2026-09-10'


def test_collect_body_text_and_reviews_ignored(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n- status: active\n- started: 2026-09-15\n\n'
                           '## Notes 2026-04-01\n\n'
                           'Talked to Sam on 2026-09-01.\n\n'
                           '- [x] project #review 📅 ✅ 2026-09-20\n'})

    assert run(tmp_path, monkeypatch)['project/a.md']['latest_date'] == '2026-04-01'


def test_collect_tagged_task_elsewhere_counts(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'project/make-bread.md': '# Make Bread\n\n- tag: make-bread\n\n'
                                 '## Notes 2026-05-01\n',
        'plan/daily/26-Q3/2026-09-20 Sun.md':
            '- [x] #make-bread order flour 📅 2026-09-20\n',
    })

    e = run(tmp_path, monkeypatch)['project/make-bread.md']

    assert e['latest_date'] == '2026-09-20'


def test_collect_invalid_date_skipped(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n## Notes 2026-02-30\n\n## Notes 2026-02-01\n'})

    assert run(tmp_path, monkeypatch)['project/a.md']['latest_date'] == '2026-02-01'


def test_collect_no_dates(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': '# A\n'})

    e = run(tmp_path, monkeypatch)['project/a.md']

    assert e['latest_date'] is None
    assert 'no-recent-activity' in e['warnings']


def test_collect_folder_name_date_counts(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/2026-09-01-trip/Home.md': '# Trip\n'})

    e = run(tmp_path, monkeypatch)['project/2026-09-01-trip/']

    assert e['latest_date'] == '2026-09-01'


# Tests for warnings

def test_collect_paused_project_no_warnings(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n- status: paused\n\n'
                           '- [x] project #review 📅 ✅ 2026-09-15\n'})

    assert run(tmp_path, monkeypatch)['project/a.md']['warnings'] == []


def test_collect_stalled_active_project(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n- [x] project #review 📅 ✅ 2026-07-15\n\n'
                           '## Notes 2026-08-01\n\n'
                           '- [ ] later thing #next 📅 2026-12-01\n'
                           '- [x] old thing #next 📅 ✅ 2026-08-01\n'})

    e = run(tmp_path, monkeypatch)['project/a.md']

    assert e['latest_date'] == '2026-08-01'
    assert e['warnings'] == ['no-recent-activity', 'review-overdue']


def test_collect_stalled_active_project_no_next(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n- [x] project #review 📅 ✅ 2026-07-15\n\n'
                           '## Notes 2026-08-01\n'})

    e = run(tmp_path, monkeypatch)['project/a.md']

    assert e['warnings'] == ['no-next', 'no-recent-activity', 'review-overdue']


def test_collect_healthy_active_project(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n- [x] project #review 📅 ✅ 2026-09-01\n'
                           '- [ ] step #next 📅 2026-09-24\n'})

    assert run(tmp_path, monkeypatch)['project/a.md']['warnings'] == []


def test_collect_thirty_days_is_not_overdue(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md':
                           '# A\n\n- [x] project #review 📅 ✅ 2026-08-26\n'
                           '- [ ] step #next 📅 2026-08-26\n'})

    assert run(tmp_path, monkeypatch)['project/a.md']['warnings'] == []


def test_collect_done_project_no_review_warning(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': '# A\n\n- status: done\n'})

    assert run(tmp_path, monkeypatch)['project/a.md']['warnings'] == []


# Tests for run function

def test_run_warnings_only(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'project/ok.md': '# Ok\n\n- status: done\n',
        'project/stale.md': '# Stale\n',
    })

    assert list(run(tmp_path, monkeypatch, warnings_only=True)) == ['project/stale.md']


def test_run_json_fields(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/make-bread.md':
                           '# Make Bread\n\n- tag: make-bread\n'})

    e = run(tmp_path, monkeypatch)['project/make-bread.md']

    assert e == {'path': 'project/make-bread.md', 'home': 'project/make-bread.md',
                 'status': 'active', 'tag': 'make-bread', 'last_review': None,
                 'latest_date': None, 'open_tasks': 0, 'completed_tasks': 0,
                 'warnings': ['no-next', 'no-recent-activity', 'review-overdue']}


def test_run_text_lines(tmp_path, monkeypatch):
    write_notes(tmp_path, {
        'project/a.md': '# A\n\n- status: done\n\n## Notes 2026-09-01\n',
        'project/trip/Packing.md': '',
    })
    monkeypatch.chdir(tmp_path)

    lines, _ = projects.run('.', today=TODAY)

    assert lines == [
        'project/a.md   done    latest 2026-09-01  review never',
        'project/trip/  active  latest none        review never       '
        'no-home-note, no-next, no-recent-activity, review-overdue',
    ]


def test_run_writes_nothing(tmp_path, monkeypatch):
    write_notes(tmp_path, {'project/a.md': '# A\n'})
    before = sorted((p, p.stat().st_mtime_ns) for p in tmp_path.rglob('*'))

    run(tmp_path, monkeypatch)

    assert sorted((p, p.stat().st_mtime_ns) for p in tmp_path.rglob('*')) == before
