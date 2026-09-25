## 1. Shared project loading

- [ ] 1.1 Split the per-entry body of `projects.list_projects` into `projects.load_project(rel, root_dir)` that builds one `Project` (home note, fields, files, `no-home-note`) for a note or folder in `project/` or `archive/project/`, and have `list_projects` call it; verify `pipenv run pytest test/unit/test_projects.py` passes unchanged, plus a new test loading an `archive/project/` folder
- [ ] 1.2 Make `latest_date` strip the project's parent folder (`project/` or `archive/project/`) from file paths; verify with a `test_projects.py` test that an archived project under a dated parent path takes its latest date only from its own names, headings, and tasks

## 2. `brief.py`

- [ ] 2.1 Add `scripts/meta_notes/brief.py` with path resolution through `project.project_for` (root-relative or absolute inside the root, `.md` and trailing `/` optional) and a `ValueError` naming the path for anything else; verify with `test/unit/test_brief.py` tests for "Note project without extension", "Folder project", "Area rejected", and "Nested note rejected"
- [ ] 2.2 Build the brief from `load_project`, one `find_tasks.collect_tasks` pass, `assign_tasks`, `last_review`, `latest_date`, and `warnings`, reporting path, home, status, tag, and all fields; verify with tests for "Fields reported", "Folder without a home note", "Same answers as the project list" (compare with `projects.run` on the same fixture), and "Review doesn't count as activity"
- [ ] 2.3 Add the file list (every non-hidden file, recursive, sorted, with `size` and local `modified` date from `os.stat`); verify with tests for "Folder files", "Note project", and "Recent modification doesn't count as activity" (set an mtime with `os.utime`)
- [ ] 2.4 Split tasks into `open`, `later`, `deadlines`, `scheduled_reviews`, and windowed `completed` with `completed_total` and `since` (default today minus 90 days), dropping canceled and rescheduled tasks, sorted by file then line, as `query.task_to_dict` dicts without `section`, plus `has_next`; verify with tests for "Tagged task elsewhere", "Plain checkbox ignored", "Canceled task left out", "Later listed separately", "Deadline and scheduled review", "Unscheduled review not listed as scheduled", "No next action", "Default window", "Since", and "Due date stands in"
- [ ] 2.5 Add the text output from the design (header, warnings, then non-empty sections with `file:line  text` task lines and `Completed (N of M since <date>)`); verify with a test on a fixture project that checks the header, section order, and that empty sections are left out

## 3. CLI

- [ ] 3.1 Add the `project` subcommand group with `brief <path> [--since DAY]` in `cli.py`, using `_day_value` for `--since` and mapping `ValueError` to an error `Output`; verify with `test/unit/test_cli.py` tests for "JSON result", "Invalid since", an error with `--json` (`ok` false, one JSON object), and "Task line usable by task update" (brief then `task update` on the reported line succeeds)

## 4. Docs

- [ ] 4.1 Document `meta-notes project brief` in `doc/meta-notes.txt` under a `*meta-notes-cli-project-brief*` tag (arguments, `--since`, sections, JSON fields) and add an example to README's Command Line section; verify `:helptags doc` reports no errors and the tag resolves
- [ ] 4.2 Update the CLI list in `docs/planning-system.md` so `project-brief` matches the shipped command; verify by reading it against the spec

## 5. Integration

- [ ] 5.1 In a scratch notes root with a note project, a folder project, an archived project, tagged tasks in daily notes, and dated headings, run `meta-notes project brief` on each (text and `--json`) and `meta-notes projects --json`, and verify the dates and warnings agree and the output matches the fixtures; then run `pipenv run pytest test/unit/` and `./run_tests.sh`
