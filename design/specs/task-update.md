## Purpose

Specifies `meta-notes task update`, which edits one checkbox line's status, tags, and dates in place, guarded against stale line numbers, so agents, Vim, and the dashboard make task edits the same way.

## Requirements

### Requirement: Update targets one checkbox line  {#r-c0ba}
`meta-notes task update <file>:<line> --expect <text>` SHALL edit line `<line>` (counting from 1) of `<file>`. `<file>` SHALL be relative to the notes root, or an absolute path inside it. The target SHALL be split at its last `:`. The line SHALL be a checkbox line: optional indentation, `-`, `*`, or `+`, whitespace, then `[<char>]`. A checkbox line SHALL be editable whether or not queries count it as a task. The command SHALL fail without writing when the file doesn't exist, the line number is out of range, or the line is not a checkbox line. At least one edit option SHALL be given, or the command SHALL fail with a usage error.

#### Scenario: Plain checkbox becomes a task  {#s-2770}
*Verification*: **non-executable**
- **WHEN** line 4 of `project/foo.md` is `- [ ] buy milk` and the user runs `meta-notes task update project/foo.md:4 --expect '- [ ] buy milk' --due undated`
- **THEN** line 4 SHALL become `- [ ] buy milk 📅`

#### Scenario: Not a checkbox  {#s-5a28}
*Verification*: **non-executable**
- **WHEN** line 1 of `project/foo.md` is `# project/foo` and the user runs `meta-notes task update project/foo.md:1 --expect '# project/foo' --status x`
- **THEN** the command SHALL exit non-zero with an error saying the line is not a checkbox, and the file SHALL be unchanged

#### Scenario: Line out of range  {#s-18b9}
*Verification*: **non-executable**
- **WHEN** `project/foo.md` has 10 lines and the user runs `meta-notes task update project/foo.md:11 --expect '- [ ] a 📅' --status x`
- **THEN** the command SHALL exit non-zero, and the file SHALL be unchanged

#### Scenario: No edit option  {#s-d246}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes task update project/foo.md:3 --expect '- [ ] a 📅'`
- **THEN** the command SHALL exit non-zero with a usage error

### Requirement: Stale-line guard  {#r-93b5}
`--expect` SHALL be required. Before writing, the command SHALL compare the current line with `--expect`, ignoring trailing whitespace on both. If they differ, the command SHALL write nothing, exit non-zero, and report the current line text: in the error message, and with `--json` also in a `current` field.

#### Scenario: Line changed since it was read  {#s-e196}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-02` and the user runs `meta-notes task update project/foo.md:3 --expect '- [ ] call Sam 📅 2026-10-01' --status x --json`
- **THEN** the command SHALL exit non-zero, the file SHALL be unchanged, and the JSON SHALL have `ok` false and `current` set to `- [ ] call Sam 📅 2026-10-02`

#### Scenario: Trailing whitespace ignored  {#s-d2d9}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-01  ` and `--expect` is `- [ ] call Sam 📅 2026-10-01`
- **THEN** the lines SHALL match and the edit SHALL proceed

### Requirement: Set status  {#r-7e2b}
`--status <char>` SHALL set the character between the brackets. It SHALL accept space, `x`, `X`, `>`, `-`, `.`, `o`, and `O`, and reject any other value with a usage error. `x` and `X` SHALL both mean done. `--status '>'` SHALL only set the character; the command SHALL NOT copy the task anywhere.

#### Scenario: Cancel a task  {#s-4f94}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-01` and the user runs `--status -`
- **THEN** line 3 SHALL become `- [-] call Sam 📅 2026-10-01`

#### Scenario: Reschedule a daily-note copy  {#s-e56c}
*Verification*: **non-executable**
- **WHEN** line 12 of a daily note is `- [ ] draft outline 📅 2026-09-25` and the user runs `--status '>'`
- **THEN** line 12 SHALL become `- [>] draft outline 📅 2026-09-25`, and no other file SHALL change

#### Scenario: Invalid status  {#s-9ba3}
*Verification*: **non-executable**
- **WHEN** the user runs `--status done`
- **THEN** the command SHALL exit non-zero with a usage error

### Requirement: Completion date  {#r-43d5}
When `--status` changes a line from a status that is not done to done, the command SHALL append `✅ <today>` at the end of the line, unless the line already has a `✅` date, the line's due date (after this call's `--due` edit, if any) is today, or `--no-completed` is given. A recurring line (see the "Complete a recurring task" requirement) SHALL always get `✅ <today>`, even when due today, and `--no-completed` on it SHALL be a usage error that writes nothing. A line that is already done and set to done again SHALL keep its completion date or lack of one. When `--status` sets any status other than done, including canceled (`-`) and rescheduled (`>`), the command SHALL remove every `✅` date from the line.

#### Scenario: Done late  {#s-473c}
*Verification*: **non-executable**
- **WHEN** today is 2026-09-25, line 3 is `- [ ] call Sam 📅 2026-09-22`, and the user runs `--status x`
- **THEN** line 3 SHALL become `- [x] call Sam 📅 2026-09-22 ✅ 2026-09-25`

#### Scenario: Done on the due date  {#s-8ce4}
*Verification*: **non-executable**
- **WHEN** today is 2026-09-25, line 3 is `- [ ] call Sam 📅 2026-09-25`, and the user runs `--status x`
- **THEN** line 3 SHALL become `- [x] call Sam 📅 2026-09-25`

#### Scenario: Undated task done  {#s-8208}
*Verification*: **non-executable**
- **WHEN** today is 2026-09-25, line 3 is `- [ ] someday task 📅`, and the user runs `--status x`
- **THEN** line 3 SHALL become `- [x] someday task 📅 ✅ 2026-09-25`

#### Scenario: Skip the completion date  {#s-cc66}
*Verification*: **non-executable**
- **WHEN** today is 2026-09-25, line 3 is `- [ ] call Sam 📅 2026-09-22`, and the user runs `--status x --no-completed`
- **THEN** line 3 SHALL become `- [x] call Sam 📅 2026-09-22`

#### Scenario: Canceling removes the completion date  {#s-59c6}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [x] call Sam 📅 2026-09-22 ✅ 2026-09-24` and the user runs `--status -`
- **THEN** line 3 SHALL become `- [-] call Sam 📅 2026-09-22`

#### Scenario: Reopening removes the completion date  {#s-fbda}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [x] call Sam 📅 2026-09-22 ✅ 2026-09-24` and the user runs `--status ' '`
- **THEN** line 3 SHALL become `- [ ] call Sam 📅 2026-09-22`

### Requirement: Add and remove tags  {#r-b6d0}
`--add-tag <tag>` and `--remove-tag <tag>` SHALL be repeatable, and SHALL accept the tag with or without a leading `#`. A tag name SHALL be letters, digits, `_`, or `-`; any other value SHALL be a usage error. Giving the same tag to both options SHALL be a usage error. Tags SHALL be matched as the `task-query` capability matches them: ignoring case, with aliases applied (`#mtg` is `meeting`, `#pers` and `#per` are `personal`).

An added tag SHALL be written as given, with `#`, before the first `🛫`, `📅`, `📆`, `🗓`, `⏰`, `🔁`, or `✅` on the line, separated by single spaces; with none of those, at the end of the line. Adding a tag the line already has SHALL leave the line unchanged. Removing a tag SHALL remove every occurrence of it and the space before it (or after it, when the tag follows the checkbox directly). Removing a tag the line doesn't have SHALL leave the line unchanged.

#### Scenario: Tag goes before the dates  {#s-e58f}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-01` and the user runs `--add-tag later`
- **THEN** line 3 SHALL become `- [ ] call Sam #later 📅 2026-10-01`

#### Scenario: Tag without dates  {#s-e3a1}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] buy milk` and the user runs `--add-tag '#errand'`
- **THEN** line 3 SHALL become `- [ ] buy milk #errand`

#### Scenario: Tag already present in another case  {#s-619f}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] #Later read book 📅` and the user runs `--add-tag later`
- **THEN** line 3 SHALL be unchanged

#### Scenario: Remove by alias  {#s-6da2}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] #mtg prep agenda 📅 2026-10-01` and the user runs `--remove-tag meeting`
- **THEN** line 3 SHALL become `- [ ] prep agenda 📅 2026-10-01`

#### Scenario: Add and remove together  {#s-f9f5}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] #later read book 📅` and the user runs `--remove-tag later --add-tag next`
- **THEN** line 3 SHALL become `- [ ] read book #next 📅`

### Requirement: Set the due date  {#r-0161}
`--due <value>` SHALL accept a `YYYY-MM-DD` date, `undated`, or `none`; any other value SHALL be a usage error. The line's due emoji is the first `📅`, `📆`, or `🗓` on it.

- A date SHALL replace the date after the line's due emoji, or add one after a bare due emoji, keeping that emoji. A line with no due emoji SHALL get `📅 <date>`.
- `undated` SHALL remove the date after the line's due emoji and keep the emoji. A line with no due emoji SHALL get a bare `📅`.
- `none` SHALL remove every due emoji on the line and the date after each.

A new due emoji SHALL be placed after any `🛫` date and before any `✅` date; with neither, at the end of the line.

#### Scenario: Change a date and keep the emoji  {#s-b33d}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] call Sam 📆 2026-10-01` and the user runs `--due 2026-10-08`
- **THEN** line 3 SHALL become `- [ ] call Sam 📆 2026-10-08`

#### Scenario: Date a bare marker  {#s-3171}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] someday task 🗓` and the user runs `--due 2026-10-08`
- **THEN** line 3 SHALL become `- [ ] someday task 🗓 2026-10-08`

#### Scenario: New due date uses 📅  {#s-1b58}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] draft outline 🛫 2026-10-05` and the user runs `--due 2026-10-10`
- **THEN** line 3 SHALL become `- [ ] draft outline 🛫 2026-10-05 📅 2026-10-10`

#### Scenario: Make undated  {#s-7bb6}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-01` and the user runs `--due undated`
- **THEN** line 3 SHALL become `- [ ] call Sam 📅`

#### Scenario: Due date before the completion date  {#s-c920}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [x] call Sam ✅ 2026-09-24` and the user runs `--due 2026-09-22`
- **THEN** line 3 SHALL become `- [x] call Sam 📅 2026-09-22 ✅ 2026-09-24`

#### Scenario: Invalid date  {#s-c51e}
*Verification*: **non-executable**
- **WHEN** the user runs `--due 2026-02-30`
- **THEN** the command SHALL exit non-zero with a usage error, and the file SHALL be unchanged

### Requirement: Set the start date  {#r-7435}
`--start <value>` SHALL accept a `YYYY-MM-DD` date or `none`; any other value SHALL be a usage error. A date SHALL replace the date after the line's first `🛫`, or, if the line has none, add `🛫 <date>` before the first due emoji or `✅` date, or at the end of the line if it has neither. `none` SHALL remove every `🛫` on the line and the date after each.

#### Scenario: Add a start date  {#s-e342}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] draft outline 📅 2026-10-10` and the user runs `--start 2026-10-05`
- **THEN** line 3 SHALL become `- [ ] draft outline 🛫 2026-10-05 📅 2026-10-10`

#### Scenario: Remove a start date  {#s-4cc2}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] draft outline 🛫 2026-10-05 📅 2026-10-10` and the user runs `--start none`
- **THEN** line 3 SHALL become `- [ ] draft outline 📅 2026-10-10`

### Requirement: Set the time of day  {#r-a684}
`--time <value>` SHALL accept a 24-hour `HH:MM` (one or two digits for the hour) or `none`; any other value SHALL be a usage error. A time SHALL be written as `⏰ HH:MM`, replacing the line's existing `⏰` marker (in any form), or else placed before the first `🛫`, due, `🔁`, or `✅` date emoji, or at the end of the line if it has none. Setting a time SHALL remove a time written after the due date (`📅 2026-10-01 15:00`). `none` SHALL remove every `⏰` marker and the time after the due date. Changing the due date with `--due` SHALL keep a time after the date; `--due none` SHALL remove it with the date.

#### Scenario: Add a time  {#s-8cf5}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-01` and the user runs `--time 15:00`
- **THEN** line 3 SHALL become `- [ ] call Sam ⏰ 15:00 📅 2026-10-01`

#### Scenario: Replace a 12-hour time  {#s-afa1}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] call Sam ⏰ 3:15pm 📅 2026-10-01` and the user runs `--time 08:00`
- **THEN** line 3 SHALL become `- [ ] call Sam ⏰ 08:00 📅 2026-10-01`

#### Scenario: Remove the time  {#s-0bcb}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] call Sam ⏰ 15:00 📅 2026-10-01` and the user runs `--time none`
- **THEN** line 3 SHALL become `- [ ] call Sam 📅 2026-10-01`

#### Scenario: Invalid time  {#s-46a2}
*Verification*: **non-executable**
- **WHEN** the user runs `--time 25:00`
- **THEN** the command SHALL exit non-zero with a usage error, and the file SHALL be unchanged

### Requirement: Warning for a time without a due date  {#r-de03}
When the edited line has a time but no valid due date, the command SHALL make the edit and report a warning that the time is ignored.

#### Scenario: Time on an undated line  {#s-d6b3}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] call Sam 🛫 2026-10-01` and the user runs `--time 15:00 --json`
- **THEN** the line SHALL gain `⏰ 15:00` and `warnings` SHALL include one saying the time has no due date

### Requirement: Warning when a line stops being a task  {#r-471c}
When an edit removes a line's last due emoji and last `🛫` date, so that queries no longer count it as a task, the command SHALL make the edit and report a warning that the line is no longer a task.

#### Scenario: Remove the only date marker  {#s-3e12}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-01` and the user runs `--due none --json`
- **THEN** line 3 SHALL become `- [ ] call Sam`, and `warnings` SHALL include one saying the line is no longer a task

### Requirement: Only the target line changes  {#r-021a}
The command SHALL change only the target line, and, when it completes a recurring task, the new line inserted above it. Otherwise the number of lines, every other line, the file's line endings, and whether it ends with a newline SHALL be unchanged, so line numbers from one query stay valid across several updates. A recurring completion SHALL change no other line, but the lines after it move down one. Removing text SHALL NOT leave runs of spaces or trailing whitespace where it was. When the edits produce the same line text, the command SHALL NOT write the file.

#### Scenario: Several updates from one query  {#s-19aa}
*Verification*: **non-executable**
- **WHEN** a query reports tasks on lines 3 and 7 of `project/foo.md`, and the user updates line 3 and then line 7 with the text from that query
- **THEN** both updates SHALL succeed

#### Scenario: CRLF file  {#s-f40b}
*Verification*: **non-executable**
- **WHEN** `project/foo.md` uses CRLF line endings and line 3 is updated
- **THEN** every line of the file SHALL still end with CRLF

#### Scenario: Nothing to change  {#s-82db}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [x] call Sam 📅 2026-09-25` and the user runs `--status x`
- **THEN** the command SHALL succeed with `changed` false, and the file SHALL NOT be written

### Requirement: Update result  {#r-265b}
On success, the text output SHALL be `<file>:<line>` followed by the old line prefixed with `- ` and the new line prefixed with `+ `, or `<file>:<line> unchanged` when nothing changed. With `--json`, the result SHALL have `ok` true, `file` (relative to the notes root), `line`, `old`, `new`, `changed`, `created`, and `warnings`. `created` SHALL be null unless a next occurrence was inserted, and then an object with `file`, `line` (the new line's number), and `text`. After an insert the text output SHALL add a `<file>:<line> created` line and the new line prefixed with `+ `.

#### Scenario: JSON result  {#s-9097}
*Verification*: **non-executable**
- **WHEN** today is 2026-09-25, line 3 of `project/foo.md` is `- [ ] call Sam 📅 2026-09-22`, and the user runs `meta-notes task update project/foo.md:3 --expect '- [ ] call Sam 📅 2026-09-22' --status x --json`
- **THEN** the JSON SHALL have `ok` true, `file` `project/foo.md`, `line` 3, `old` `- [ ] call Sam 📅 2026-09-22`, `new` `- [x] call Sam 📅 2026-09-22 ✅ 2026-09-25`, and `changed` true

### Requirement: Complete a recurring task  {#r-0b86}
A line is recurring when it has a `🔁` rule that `recurrence` supports and a date to step from: its due date, else its start date, or none for a `when done` rule. When `--status` changes a recurring line from a status that is not done to done, the command SHALL mark it done as usual (stamping `✅ <today>`), compute the next date, and insert a new line directly above the target, in the same write. The new line SHALL be the done line with `[ ]`, no `✅`, and the same indentation, bullet, tags, `🔁` rule and time (`⏰`, or a time after the due date). A rule without `when done` SHALL step from the due date after this call's edits, else the start date, even when the result is already past; a `when done` rule SHALL step from today. The new line's due date SHALL be the next date (a bare due emoji is dated); with both a due and a start date the start date SHALL move by the same number of days, and with only a start date it SHALL be the next date. Done lines SHALL stay in place, so the target moves to `<line>+1`. A line already done and set to done again, and every other status, SHALL NOT insert a line. Reopening a done line SHALL NOT remove a line inserted earlier. When the target is the last line of a file with no final newline, the inserted line SHALL take the file's line ending and the target SHALL keep having none. A line with a `🔁` rule that is unsupported, or valid but without a date to step from, SHALL complete as any other line and report a warning that no next occurrence was made.

#### Scenario: Done twice  {#s-8659}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] replace filter 🔁 every 3 months ⏰ 09:00 📅 2026-07-01`, today is 2026-09-25, and the user runs `--status x` twice, the second time on line 4 with the done line as `--expect`
- **THEN** after the first run line 3 SHALL be `- [ ] replace filter 🔁 every 3 months ⏰ 09:00 📅 2026-10-01` and line 4 `- [x] replace filter 🔁 every 3 months ⏰ 09:00 📅 2026-07-01 ✅ 2026-09-25`, and the second run SHALL change nothing

#### Scenario: Canceled  {#s-edbd}
*Verification*: **non-executable**
- **WHEN** line 3 is a recurring task and the user runs `--status -`
- **THEN** only line 3 SHALL change and no line SHALL be inserted

#### Scenario: Completed late  {#s-adbd}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] replace filter 🔁 every 3 months 📅 2026-07-01`, today is 2026-10-05, and the user runs `--status x`
- **THEN** the inserted line SHALL have `📅 2026-10-01`

#### Scenario: Due today still stamped  {#s-d46a}
*Verification*: **non-executable**
- **WHEN** today is 2026-09-25 and line 3 is `- [ ] stretch 🔁 every day 📅 2026-09-25`
- **THEN** the done line SHALL end with `✅ 2026-09-25` and the inserted line SHALL have `📅 2026-09-26`

#### Scenario: When done  {#s-a86a}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] buy salt 🔁 every month when done 📅 2026-07-24` and today is 2026-10-05
- **THEN** the inserted line SHALL have `📅 2026-11-05`

#### Scenario: Indented line in a CRLF file  {#s-4f34}
*Verification*: **non-executable**
- **WHEN** a CRLF file has `  - [ ] mow 🔁 every weekday 📅 2026-09-25` on its last line with no final newline
- **THEN** the inserted line SHALL keep the two-space indentation and end with CRLF, and the done line SHALL have no line ending

### Requirement: No next occurrence  {#r-aa0c}
`--no-recur` SHALL complete a recurring line without inserting the next occurrence; the line keeps its `🔁` rule and gets its `✅` date. It SHALL have no effect on a line that is not recurring.

#### Scenario: Finished series  {#s-4d2f}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] replace filter 🔁 every 3 months 📅 2026-07-01` and the user runs `--status x --no-recur`
- **THEN** line 3 SHALL become the done line and no line SHALL be inserted

### Requirement: Set the recurrence rule  {#r-3ea6}
`--recur <rule>` SHALL accept a rule `recurrence` supports (such as `every 3 months` or `every week when done`) or `none`; any other value SHALL be a usage error. A rule SHALL be written as `🔁 <rule>`, replacing the line's existing `🔁` marker and rule, or else placed before the first `🛫`, due, `⏰`, or `✅` date emoji, or at the end of the line if it has none. `none` SHALL remove every `🔁` marker and its rule. The rule is applied before `--status`, so `--status x --recur none` completes without inserting a line.

#### Scenario: Add a rule  {#s-fba0}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] call Sam 📅 2026-10-01` and the user runs `--recur 'every week'`
- **THEN** line 3 SHALL become `- [ ] call Sam 🔁 every week 📅 2026-10-01`

#### Scenario: Remove a rule  {#s-0e47}
*Verification*: **non-executable**
- **WHEN** line 3 is `- [ ] call Sam 🔁 every week 📅 2026-10-01` and the user runs `--recur none`
- **THEN** line 3 SHALL become `- [ ] call Sam 📅 2026-10-01`

#### Scenario: Unsupported rule  {#s-bef0}
*Verification*: **non-executable**
- **WHEN** the user runs `--recur 'every other week'`
- **THEN** the command SHALL exit non-zero with a usage error, and the file SHALL be unchanged
