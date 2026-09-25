## ADDED Requirements

### Requirement: Task query matches find_tasks
`meta-notes tasks` SHALL accept the options of `scripts/find_tasks.py` (`--folder`, `--due-on`, `--due-by`, `--due-between`, `--status`, `--format`, `--condensed`) and SHALL print the same output that `find_tasks.py` prints for the same options and notes root.

#### Scenario: Default report
- **WHEN** the user runs `meta-notes tasks` with no filters
- **THEN** the output SHALL equal `python3 scripts/find_tasks.py` run in the notes root

#### Scenario: Filtered query
- **WHEN** the user runs `meta-notes tasks --folder project --status all`
- **THEN** the output SHALL equal `find_tasks.py --folder project --status all` run in the notes root

### Requirement: Task query JSON
With `--json`, `meta-notes tasks` SHALL return the same tasks as the text output, each with its file, line number, line text, status, and start, due, and completed dates.

#### Scenario: JSON task fields
- **WHEN** `project/foo.md` line 3 is `- [ ] Call Sam 📆 2026-10-01` and the user runs `meta-notes tasks --folder project --json`
- **THEN** the result SHALL include a task with file `project/foo.md`, line 3, status `incomplete`, and due date `2026-10-01`

### Requirement: Standalone script still works
`scripts/find_tasks.py` SHALL remain runnable directly with unchanged options and output.

#### Scenario: Template command
- **WHEN** a daily-note template runs `python scripts/find_tasks.py --due-on <date> --status incomplete --condensed`
- **THEN** it SHALL produce the same output as before this change
