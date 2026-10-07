## Purpose

Specifies `meta-notes task add`, which writes a new open task line into an existing note, with a due date, a time, and a recurrence rule checked by the same parsers that read them back, so agents and scripts capture tasks without hand-writing the emoji syntax.

## Requirements

### Requirement: Add a task line  {#r-80b1}
`meta-notes task add <file> <text>` SHALL insert one open task line, `- [ ] <text>` followed by the requested markers, into `<file>`, which SHALL exist and be relative to the notes root or an absolute path inside it. By default the line SHALL go at the end of the `Tasks` section when the file has a heading with that text at any level (after the section's last non-blank line, before the next heading of the same or a higher level, so a subheading stays in the section), else just below the file's first `# ` title and a blank line, with a blank line after the task too (unless the next line is already blank or the end of the file), else, with no title, at the top of the file after any frontmatter; `--line <n>` SHALL insert it before line `n` (counting from 1, up to one past the last line), moving the later lines down. The text SHALL be one non-empty line. The file's line endings SHALL be kept: the new line SHALL use the ending the file already uses (`\n` for a file with none), and a final line with no newline SHALL get one. Nothing SHALL be written when the command fails.

#### Scenario: Add to a note with no Tasks heading  {#s-e4b0}
*Verification*: **non-executable**
- **WHEN** `project/foo.md` has `# foo` and a paragraph, and the user runs `meta-notes task add project/foo.md 'call Sam' --due 2026-10-01`
- **THEN** the file SHALL become `# foo`, a blank line, then `- [ ] call Sam 📅 2026-10-01`, a blank line, then the paragraph

#### Scenario: Add under the Tasks heading  {#s-3dda}
*Verification*: **non-executable**
- **WHEN** a daily note has `## Tasks`, a task with a note line, a blank line, then `## Time Block` and the user runs `meta-notes task add` on it without `--line`
- **THEN** the new line SHALL follow the task's note line, before the blank line and `## Time Block`

#### Scenario: Insert at a line  {#s-c4ff}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes task add project/foo.md 'call Sam' --due 2026-10-01 --line 2`
- **THEN** the new line SHALL be line 2 and the former line 2 SHALL be line 3

#### Scenario: Missing file or bad line  {#s-bf32}
*Verification*: **non-executable**
- **WHEN** the file doesn't exist, or `--line` is beyond one past the last line, or the text is empty
- **THEN** the command SHALL exit non-zero and write nothing

### Requirement: Dates, time, rule and tags  {#r-18f7}
`--due` SHALL take `YYYY-MM-DD` or `undated` and write `📅 <date>` or a bare `📅` emoji, placed as `task update` places them. `--start` SHALL take `YYYY-MM-DD` and write `🛫 <date>`. `--time HH:MM` SHALL write `⏰ HH:MM` and SHALL require `--due`. `--recur <rule>` SHALL accept a rule `recurrence` supports and write `🔁 <rule>`; unless the rule is `when done`, it SHALL require `--due` or `--start` to step from. `--tag <tag>` (repeatable, with or without `#`) SHALL add a tag before the first date marker. An invalid date, time, rule or tag, or a time or rule without what it needs, SHALL be an error. A line with no `--due` or `--start` SHALL be added with a warning that queries don't list it as a task.

#### Scenario: Timed recurring task  {#s-3202}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes task add area/home.md 'change filter' --recur 'every 3 months' --time 09:00 --due 2026-10-01 --tag home`
- **THEN** the added line SHALL be `- [ ] change filter #home 🔁 every 3 months ⏰ 09:00 📅 2026-10-01`, and `meta-notes tasks --json` SHALL report its due date, time and recurrence

#### Scenario: Time without a due date  {#s-60fd}
*Verification*: **non-executable**
- **WHEN** the user runs `--time 09:00` with no `--due`
- **THEN** the command SHALL exit non-zero and write nothing

#### Scenario: Rule with nothing to step from  {#s-00dc}
*Verification*: **non-executable**
- **WHEN** the user runs `--recur 'every week'` with neither `--due` nor `--start`
- **THEN** the command SHALL exit non-zero, and `--recur 'every week when done'` alone SHALL succeed

#### Scenario: Unsupported rule  {#s-516c}
*Verification*: **non-executable**
- **WHEN** the user runs `--recur 'every other week' --due 2026-10-01`
- **THEN** the command SHALL exit non-zero with a usage error

#### Scenario: Undated task  {#s-f0f1}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes task add test.md 'example' --due undated`
- **THEN** the added line SHALL be `- [ ] example 📅`, a bare due emoji with no date

#### Scenario: No date  {#s-5a15}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes task add project/foo.md 'buy milk'`
- **THEN** the line `- [ ] buy milk` SHALL be added, with a warning that it isn't a task

### Requirement: Add result  {#r-e533}
The text output SHALL be `<file>:<line> added` and the new line prefixed with `+ `. With `--json`, the result SHALL have `ok` true, `file` (relative to the notes root), `line` (the new line's number), `text` (the line), and `warnings`.

#### Scenario: JSON result  {#s-0dc2}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes task add project/foo.md 'call Sam' --due 2026-10-01 --json` on a file of 3 lines
- **THEN** the JSON SHALL have `ok` true, `file` `project/foo.md`, `line` 4, and `text` `- [ ] call Sam 📅 2026-10-01`
