# conventions Specification

## Purpose
Specifies `meta-notes conventions`, which prints the shared note syntax and editing conventions that every skill and agent follows, so the rules are defined once and always match the installed CLI.

## Requirements

### Requirement: Conventions command
`meta-notes conventions` SHALL print the conventions as markdown to stdout. With `--json`, the result SHALL have `version` (the CLI version) and `text` (the same markdown). The command SHALL work outside a notes root and SHALL NOT read or write notes.

#### Scenario: Outside a notes root
- **WHEN** the user runs `meta-notes conventions` in a directory with no `.meta-notes` above it
- **THEN** the command SHALL succeed and print the conventions

#### Scenario: JSON result
- **WHEN** the user runs `meta-notes conventions --json`
- **THEN** the result SHALL have `ok` true, `version`, and `text`

### Requirement: Conventions content
The conventions SHALL cover:

- the task model: checkbox lines, due emoji (dated and bare), `🛫`, `✅`, the rule that a line is a task only with a due emoji or a `🛫` date, and the 80-column line limit
- status characters and their meanings
- tags: syntax, case-insensitive matching, aliases, and the tags skills use (`#next`, `#later`, `#wait`, `#review`, `#deadline`)
- the project model: note and folder projects, the `Home.md` home note, the `status`, `tag`, and `archived` fields, and project tasks
- task edits: take `file`, `line`, and `text` from `meta-notes tasks --json`, edit with `meta-notes task update <file>:<line> --expect <text>`, and re-query when the line has changed; never rewrite a task line directly
- where new markers go: tags before dates (`... #next 📅 <date>`)
- carrying a task forward: mark the old line `>` with `task update` and write the new copy
- ceremony markers and checking them with `task update --status x`
- structural changes only through `meta-notes move`, `rename`, and `archive`, after the user confirms the command

#### Scenario: Task edit rule present
- **WHEN** the user runs `meta-notes conventions`
- **THEN** the output SHALL include the `meta-notes task update <file>:<line> --expect <text>` rule

### Requirement: Code-defined values are generated
The status characters, the due emoji, and the tag aliases in the conventions SHALL be generated from the definitions the CLI uses for task queries and task updates, not written by hand, so the printed conventions always match the installed CLI.

#### Scenario: Alias shown
- **WHEN** the CLI reads `#waiting` as `wait`
- **THEN** the conventions SHALL list `#waiting` as an alias of `#wait`

#### Scenario: Due emoji shown
- **WHEN** the user runs `meta-notes conventions`
- **THEN** the output SHALL list 📅, 📆, and 🗓 as due emoji, with 📅 as the one to write
