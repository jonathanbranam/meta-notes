## MODIFIED Requirements

### Requirement: Conventions content
The conventions SHALL cover:

- the task model: checkbox lines, `📅` (dated and bare), `🛫`, `✅`, the rule that a line is a task only with `📅` or a `🛫` date, and the 80-column line limit; `📅` SHALL be the only due emoji named
- status characters and their meanings, as one sentence rather than a table
- tags: syntax, case-insensitive matching, aliases (as one sentence rather than a table), and the tags skills use (`#next`, `#later`, `#wait`, `#review`, `#deadline`)
- the project model: note and folder projects, the `Home.md` home note, the `status`, `tag`, and `archived` fields, and project tasks
- task edits: take `file`, `line`, and `text` from `meta-notes tasks --json`, edit with `meta-notes task update <file>:<line> --expect <text>`, and re-query when the line has changed; never rewrite a task line directly
- where new markers go: tags before dates (`... #next 📅 <date>`)
- carrying a task forward: mark the old line `>` with `task update` and write the new copy
- ceremony markers and checking them with `task update --status x`
- structural changes only through `meta-notes move`, `rename`, and `archive`, after the user confirms the command

The conventions SHALL contain no markdown tables, and every line SHALL fit in 80 columns.

#### Scenario: Task edit rule present
- **WHEN** the user runs `meta-notes conventions`
- **THEN** the output SHALL include the `meta-notes task update <file>:<line> --expect <text>` rule

#### Scenario: No tables
- **WHEN** the user runs `meta-notes conventions`
- **THEN** no line of the output SHALL start with `|`

### Requirement: Code-defined values are generated
The status characters and the tag aliases in the conventions SHALL be generated from the definitions the CLI uses for task queries and task updates, not written by hand, so the printed conventions always match the installed CLI. Status characters with the same meaning SHALL be listed together (`x`/`X` done).

#### Scenario: Alias shown
- **WHEN** the CLI reads `#waiting` as `wait`
- **THEN** the conventions SHALL list `#waiting` as an alias of `#wait`

#### Scenario: Status characters grouped
- **WHEN** the user runs `meta-notes conventions`
- **THEN** the output SHALL list `x`/`X` together as done, and every status character the CLI defines

#### Scenario: Due emoji shown
- **WHEN** the user runs `meta-notes conventions`
- **THEN** the output SHALL name 📅 as the due emoji to write and SHALL NOT list 📆 or 🗓, which the CLI still reads
