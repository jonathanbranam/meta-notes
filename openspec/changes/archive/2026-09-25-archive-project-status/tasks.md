## 1. Project field module

- [x] 1.1 Add `scripts/meta_notes/project.py` with `project_for(path)` (top-level note or folder of `project/` or `archive/project/`) and `home_note(project)` (`Home.md` for folders, None if missing); verify with `test/unit/test_project.py` cases for note, folder, nested note, and missing `Home.md`
- [x] 1.2 Add `read_fields(path)`: title, first field list before the next heading, no-title fallback, lowercase keys, checkboxes and plain lists skipped; verify with unit tests for each `Field list` spec scenario
- [x] 1.3 Add `set_fields(path, fields)`: replace first matching key in place, drop later duplicates, append missing keys, insert a new list after the title (or at the top) with blank-line separation, preserve line endings and trailing newline; verify with unit tests for each `Setting fields` scenario, including a CRLF note

## 2. Archive integration

- [x] 2.1 Add `today` parameter to `ops.archive_item` and `ops.archive`, and `fields_written` and `home` to `ArchiveItem`; before the move, set `status: archived` and `archived: <today>` on a project's home note; verify with `test_ops.py` tests for note and folder projects
- [x] 2.2 Keep fields when the move fails and add "marked archived but not moved" to the error, single and batch; verify with `test_ops.py` tests where `archive/project/<name>.md` already exists
- [x] 2.3 Warn (without failing) for a folder project with no `Home.md` and for a failed field write, still moving the project; write nothing for areas, resources, and notes nested in a project; verify with `test_ops.py` tests for missing `Home.md`, a read-only home note, `area/`, and `project/kitchen/Tasks.md`
- [x] 2.4 Append ` (status: archived)` to the text message and add `fields_written` and `home` to each item in `cli.cmd_archive` JSON; verify with `test_cli.py` tests for a project, a resource, and a failed project move
- [x] 2.5 Update existing unit and vader archive tests whose project fixtures now gain fields; verify `pipenv run pytest test/unit/` and `./run_tests.sh` pass

## 3. Docs and release

- [x] 3.1 Document the archive fields under `meta-notes archive` and `:MetaNotesArchive` in `doc/meta-notes.txt`, and note that `project.py` exists in the `planning-skills` and `project-brief` artifacts that planned to create it; verify `:helptags doc` reports no errors
- [x] 3.2 Bump `__version__` MINOR in `scripts/meta_notes/__init__.py` when archiving the change; verify `meta-notes --version`
