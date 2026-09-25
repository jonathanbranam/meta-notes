## Purpose

Specifies `meta-notes task update`, which edits one checkbox line's status, tags, and dates in place, guarded against stale line numbers, so agents, Vim, and the dashboard make task edits the same way.

## ADDED Requirements

### Requirement: Update targets one checkbox line
`meta-notes task update <file>:<line> --expect <text>` SHALL edit line `<line>` (counting from 1) of `<file>`. `<file>` SHALL be relative to the notes root, or an absolute path inside it. The target SHALL be split at its last `:`. The line SHALL be a checkbox line: optional indentation, `-`, `*`, or `+`, whitespace, then `[<char>]`. A checkbox line SHALL be editable whether or not queries count it as a task. The command SHALL fail without writing when the file doesn't exist, the line number is out of range, or the line is not a checkbox line. At least one edit option SHALL be given, or the command SHALL fail with a usage error.

#### Scenario: Plain checkbox becomes a task
- **WHEN** line 4 of `project/foo.md` is `- [ ] buy milk` and the user runs `meta-notes task update project/foo.md:4 --expect '- [ ] buy milk' --due undated`
- **THEN** line 4 SHALL become `- [ ] buy milk 📅`

#### Scenario: Not a checkbox
- **WHEN** line 1 of `project/foo.md` is `# project/foo` and the user runs `meta-notes task update project/foo.md:1 --expect '# project/foo' --status x`
- **THEN** the command SHALL exit non-zero with an error saying the line is not a checkbox, and the file SHALL be unchanged

#### Scenario: Line out of range
- **WHEN** `project/foo.md` has 10 lines and the user runs `meta-notes task update project/foo.md:11 --expect '- [ ] a 📅' --status x`
- **THEN** the command SHALL exit non-zero, and the file SHALL be unchanged

#### Scenario: No edit option
- **WHEN** the user runs `meta-notes task update project/foo.md:3 --expect '- [ ] a 📅'`
- **THEN** the command SHALL exit non-zero with a usage error

### Requirement: Stale-line guard
`--expect` SHALL be required. Before writing, the command SHALL compare the current line with `--expect`, ignoring trailing whitespace on both. If they differ, the command SHALL write nothing, exit non-zero, and report the current line text: in the error message, and with `--json` also in a `current` field.

#### Scenario: Line changed since it was read
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-02` and the user runs `meta-notes task update project/foo.md:3 --expect '- [ ] call Sam 📅 2026-10-01' --status x --json`
- **THEN** the command SHALL exit non-zero, the file SHALL be unchanged, and the JSON SHALL have `ok` false and `current` set to `- [ ] call Sam 📅 2026-10-02`

#### Scenario: Trailing whitespace ignored
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-01  ` and `--expect` is `- [ ] call Sam 📅 2026-10-01`
- **THEN** the lines SHALL match and the edit SHALL proceed

### Requirement: Set status
`--status <char>` SHALL set the character between the brackets. It SHALL accept space, `x`, `X`, `>`, `-`, `.`, `o`, and `O`, and reject any other value with a usage error. `x` and `X` SHALL both mean done. `--status '>'` SHALL only set the character; the command SHALL NOT copy the task anywhere.

#### Scenario: Cancel a task
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-01` and the user runs `--status -`
- **THEN** line 3 SHALL become `- [-] call Sam 📅 2026-10-01`

#### Scenario: Reschedule a daily-note copy
- **WHEN** line 12 of a daily note is `- [ ] draft outline 📅 2026-09-25` and the user runs `--status '>'`
- **THEN** line 12 SHALL become `- [>] draft outline 📅 2026-09-25`, and no other file SHALL change

#### Scenario: Invalid status
- **WHEN** the user runs `--status done`
- **THEN** the command SHALL exit non-zero with a usage error

### Requirement: Completion date
When `--status` changes a line from a status that is not done to done, the command SHALL append `✅ <today>` at the end of the line, unless the line already has a `✅` date, the line's due date (after this call's `--due` edit, if any) is today, or `--no-completed` is given. A line that is already done and set to done again SHALL keep its completion date or lack of one. When `--status` sets any status other than done, including canceled (`-`) and rescheduled (`>`), the command SHALL remove every `✅` date from the line.

#### Scenario: Done late
- **WHEN** today is 2026-09-25, line 3 is `- [ ] call Sam 📅 2026-09-22`, and the user runs `--status x`
- **THEN** line 3 SHALL become `- [x] call Sam 📅 2026-09-22 ✅ 2026-09-25`

#### Scenario: Done on the due date
- **WHEN** today is 2026-09-25, line 3 is `- [ ] call Sam 📅 2026-09-25`, and the user runs `--status x`
- **THEN** line 3 SHALL become `- [x] call Sam 📅 2026-09-25`

#### Scenario: Undated task done
- **WHEN** today is 2026-09-25, line 3 is `- [ ] someday task 📅`, and the user runs `--status x`
- **THEN** line 3 SHALL become `- [x] someday task 📅 ✅ 2026-09-25`

#### Scenario: Skip the completion date
- **WHEN** today is 2026-09-25, line 3 is `- [ ] call Sam 📅 2026-09-22`, and the user runs `--status x --no-completed`
- **THEN** line 3 SHALL become `- [x] call Sam 📅 2026-09-22`

#### Scenario: Canceling removes the completion date
- **WHEN** line 3 is `- [x] call Sam 📅 2026-09-22 ✅ 2026-09-24` and the user runs `--status -`
- **THEN** line 3 SHALL become `- [-] call Sam 📅 2026-09-22`

#### Scenario: Reopening removes the completion date
- **WHEN** line 3 is `- [x] call Sam 📅 2026-09-22 ✅ 2026-09-24` and the user runs `--status ' '`
- **THEN** line 3 SHALL become `- [ ] call Sam 📅 2026-09-22`

### Requirement: Add and remove tags
`--add-tag <tag>` and `--remove-tag <tag>` SHALL be repeatable, and SHALL accept the tag with or without a leading `#`. A tag name SHALL be letters, digits, `_`, or `-`; any other value SHALL be a usage error. Giving the same tag to both options SHALL be a usage error. Tags SHALL be matched as the `task-query` capability matches them: ignoring case, with aliases applied (`#mtg` is `meeting`, `#pers` and `#per` are `personal`).

An added tag SHALL be written as given, with `#`, before the first `🛫`, `📅`, `📆`, `🗓`, or `✅` on the line, separated by single spaces; with none of those, at the end of the line. Adding a tag the line already has SHALL leave the line unchanged. Removing a tag SHALL remove every occurrence of it and the space before it (or after it, when the tag follows the checkbox directly). Removing a tag the line doesn't have SHALL leave the line unchanged.

#### Scenario: Tag goes before the dates
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-01` and the user runs `--add-tag later`
- **THEN** line 3 SHALL become `- [ ] call Sam #later 📅 2026-10-01`

#### Scenario: Tag without dates
- **WHEN** line 3 is `- [ ] buy milk` and the user runs `--add-tag '#errand'`
- **THEN** line 3 SHALL become `- [ ] buy milk #errand`

#### Scenario: Tag already present in another case
- **WHEN** line 3 is `- [ ] #Later read book 📅` and the user runs `--add-tag later`
- **THEN** line 3 SHALL be unchanged

#### Scenario: Remove by alias
- **WHEN** line 3 is `- [ ] #mtg prep agenda 📅 2026-10-01` and the user runs `--remove-tag meeting`
- **THEN** line 3 SHALL become `- [ ] prep agenda 📅 2026-10-01`

#### Scenario: Add and remove together
- **WHEN** line 3 is `- [ ] #later read book 📅` and the user runs `--remove-tag later --add-tag next`
- **THEN** line 3 SHALL become `- [ ] read book #next 📅`

### Requirement: Set the due date
`--due <value>` SHALL accept a `YYYY-MM-DD` date, `undated`, or `none`; any other value SHALL be a usage error. The line's due emoji is the first `📅`, `📆`, or `🗓` on it.

- A date SHALL replace the date after the line's due emoji, or add one after a bare due emoji, keeping that emoji. A line with no due emoji SHALL get `📅 <date>`.
- `undated` SHALL remove the date after the line's due emoji and keep the emoji. A line with no due emoji SHALL get a bare `📅`.
- `none` SHALL remove every due emoji on the line and the date after each.

A new due emoji SHALL be placed after any `🛫` date and before any `✅` date; with neither, at the end of the line.

#### Scenario: Change a date and keep the emoji
- **WHEN** line 3 is `- [ ] call Sam 📆 2026-10-01` and the user runs `--due 2026-10-08`
- **THEN** line 3 SHALL become `- [ ] call Sam 📆 2026-10-08`

#### Scenario: Date a bare marker
- **WHEN** line 3 is `- [ ] someday task 🗓` and the user runs `--due 2026-10-08`
- **THEN** line 3 SHALL become `- [ ] someday task 🗓 2026-10-08`

#### Scenario: New due date uses 📅
- **WHEN** line 3 is `- [ ] draft outline 🛫 2026-10-05` and the user runs `--due 2026-10-10`
- **THEN** line 3 SHALL become `- [ ] draft outline 🛫 2026-10-05 📅 2026-10-10`

#### Scenario: Make undated
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-01` and the user runs `--due undated`
- **THEN** line 3 SHALL become `- [ ] call Sam 📅`

#### Scenario: Due date before the completion date
- **WHEN** line 3 is `- [x] call Sam ✅ 2026-09-24` and the user runs `--due 2026-09-22`
- **THEN** line 3 SHALL become `- [x] call Sam 📅 2026-09-22 ✅ 2026-09-24`

#### Scenario: Invalid date
- **WHEN** the user runs `--due 2026-02-30`
- **THEN** the command SHALL exit non-zero with a usage error, and the file SHALL be unchanged

### Requirement: Set the start date
`--start <value>` SHALL accept a `YYYY-MM-DD` date or `none`; any other value SHALL be a usage error. A date SHALL replace the date after the line's first `🛫`, or, if the line has none, add `🛫 <date>` before the first due emoji or `✅` date, or at the end of the line if it has neither. `none` SHALL remove every `🛫` on the line and the date after each.

#### Scenario: Add a start date
- **WHEN** line 3 is `- [ ] draft outline 📅 2026-10-10` and the user runs `--start 2026-10-05`
- **THEN** line 3 SHALL become `- [ ] draft outline 🛫 2026-10-05 📅 2026-10-10`

#### Scenario: Remove a start date
- **WHEN** line 3 is `- [ ] draft outline 🛫 2026-10-05 📅 2026-10-10` and the user runs `--start none`
- **THEN** line 3 SHALL become `- [ ] draft outline 📅 2026-10-10`

### Requirement: Warning when a line stops being a task
When an edit removes a line's last due emoji and last `🛫` date, so that queries no longer count it as a task, the command SHALL make the edit and report a warning that the line is no longer a task.

#### Scenario: Remove the only date marker
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-01` and the user runs `--due none --json`
- **THEN** line 3 SHALL become `- [ ] call Sam`, and `warnings` SHALL include one saying the line is no longer a task

### Requirement: Only the target line changes
The command SHALL change only the target line. The number of lines, every other line, the file's line endings, and whether it ends with a newline SHALL be unchanged, so line numbers from one query stay valid across several updates. Removing text SHALL NOT leave runs of spaces or trailing whitespace where it was. When the edits produce the same line text, the command SHALL NOT write the file.

#### Scenario: Several updates from one query
- **WHEN** a query reports tasks on lines 3 and 7 of `project/foo.md`, and the user updates line 3 and then line 7 with the text from that query
- **THEN** both updates SHALL succeed

#### Scenario: CRLF file
- **WHEN** `project/foo.md` uses CRLF line endings and line 3 is updated
- **THEN** every line of the file SHALL still end with CRLF

#### Scenario: Nothing to change
- **WHEN** line 3 is `- [x] call Sam 📅 2026-09-25` and the user runs `--status x`
- **THEN** the command SHALL succeed with `changed` false, and the file SHALL NOT be written

### Requirement: Update result
On success, the text output SHALL be `<file>:<line>` followed by the old line prefixed with `- ` and the new line prefixed with `+ `, or `<file>:<line> unchanged` when nothing changed. With `--json`, the result SHALL have `ok` true, `file` (relative to the notes root), `line`, `old`, `new`, `changed`, and `warnings`.

#### Scenario: JSON result
- **WHEN** today is 2026-09-25, line 3 of `project/foo.md` is `- [ ] call Sam 📅 2026-09-22`, and the user runs `meta-notes task update project/foo.md:3 --expect '- [ ] call Sam 📅 2026-09-22' --status x --json`
- **THEN** the JSON SHALL have `ok` true, `file` `project/foo.md`, `line` 3, `old` `- [ ] call Sam 📅 2026-09-22`, `new` `- [x] call Sam 📅 2026-09-22 ✅ 2026-09-25`, and `changed` true
