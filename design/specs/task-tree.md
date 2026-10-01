## Purpose

Specifies how meta-notes reads a task as a tree: a checkbox line with its notes and its subtasks, to any depth, in `meta-notes tasks --json` and `meta-notes task show`, so agents can read a whole task, or one subtask, as one thing.

## Requirements

### Requirement: Notes and subtasks  {#r-bf95}
A checkbox line SHALL own its **notes**: the following lines that are not checkbox lines and are indented deeper than it, up to the next line indented no deeper than the checkbox line. A deeper line SHALL belong to the nearest checkbox line above it with a smaller indent, so a subtask's notes are its own and not its parent's. A **subtask** SHALL be a checkbox line indented under another checkbox line, nested to any depth, and notes SHALL be allowed after the subtasks. A blank line SHALL end every task before it. Every checkbox line SHALL be a node of the tree, dated or not; a tab SHALL count as up to the next multiple of 4 columns. Dates SHALL NOT be inherited.

#### Scenario: Notes then subtasks  {#s-96f3}
*Verification*: **non-executable**
- **WHEN** a note has `- [o] main 📅 2026-10-08`, then `  * a note`, `  - [x] first`, `    * first's note`, and `  - [ ] second`
- **THEN** `main` SHALL own `  * a note` only, `first` SHALL own `    * first's note`, and `first` and `second` SHALL be subtasks of `main`

#### Scenario: Note after the subtasks  {#s-9c31}
*Verification*: **non-executable**
- **WHEN** an indented non-checkbox line follows the last subtask of `main`, at the indent of `main`'s notes
- **THEN** it SHALL be one of `main`'s notes

#### Scenario: Deeper nesting  {#s-e29e}
*Verification*: **non-executable**
- **WHEN** a subtask has a subtask of its own, with a note
- **THEN** that note SHALL belong to the innermost subtask and the innermost SHALL have the first subtask as its parent

### Requirement: Tree fields in the task query  {#r-80b4}
Each task of `meta-notes tasks --json` SHALL also have `notes` (its note lines as written, without line endings, in order), `parent` (the checkbox line it is nested under as `file`, `line`, `text` and `status`, or null) and `subtasks` (its direct subtasks, each as `file`, `line`, `text` and `status`). The parent and subtasks SHALL be reported whether or not they are tasks of their own. Which tasks are listed, their order and every other field SHALL be unchanged: each line is matched on its own dates.

#### Scenario: Dated subtask of an undated parent  {#s-1b59}
*Verification*: **non-executable**
- **WHEN** `- [ ] plan trip` has the subtask `  - [ ] book flights 📅 2026-10-06` and the user runs `meta-notes tasks --all --json`
- **THEN** only the subtask SHALL be listed, with `parent` naming `plan trip`

### Requirement: Show one task  {#r-7d17}
`meta-notes task show <file>:<line>` SHALL read the checkbox line at `<file>:<line>` (the target split at its last `:`; `<file>` relative to the notes root or an absolute path inside it) and print its node alone: the line and its notes. With `--tree` it SHALL print the node and every descendant: all lines through the last line of its last descendant or note. The text output SHALL be `<file>:<first>-<last>` followed by those lines. With `--json` the result SHALL have `file`, `line`, `end_line` (the last line read), `text`, `status`, `notes`, and `parent` (as in the task query, or null); with `--tree` it SHALL also have `subtasks`, each of the same shape without `parent`, nested to any depth. A line that is not a checkbox line, a missing file, or a line out of range SHALL be an error. Nothing SHALL be written.

#### Scenario: Node alone  {#s-16d1}
*Verification*: **non-executable**
- **WHEN** line 1 is a task with one note and a subtask, and the user runs `meta-notes task show project/foo.md:1`
- **THEN** the output SHALL be the task line and its note, with `end_line` 2

#### Scenario: Whole subtree  {#s-2cf7}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes task show project/foo.md:1 --tree --json`
- **THEN** `subtasks` SHALL list the subtasks with their own notes and subtasks, and `end_line` SHALL be the last line of the tree

#### Scenario: Not a checkbox line  {#s-efd9}
*Verification*: **non-executable**
- **WHEN** the line is a note or out of range
- **THEN** the command SHALL exit non-zero
