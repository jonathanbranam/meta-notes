## Purpose

Specifies how meta-notes reads and writes a task as a tree: a checkbox line with its notes and its subtasks, to any depth. It reads them in `meta-notes tasks --json` and `meta-notes task show`, and writes them with `task notes`, `task replace`, `task add --under` and the partial status that `task update` gives a subtask's ancestors, so agents can handle a whole task, or one subtask, as one thing.

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
`meta-notes task show <file>:<line>` SHALL read the checkbox line at `<file>:<line>` (the target split at its last `:`; `<file>` relative to the notes root or an absolute path inside it) and print its node alone: the line and its notes. With `--tree` it SHALL print the node and every descendant: all lines through the last line of its last descendant or note. The text output SHALL be `<file>:<ranges>` followed by the lines read, where `<ranges>` lists each run of consecutive lines as `<first>-<last>`, comma-separated. The node alone SHALL print only the task line and the task's own notes, never a subtask or a subtask's note, so when a note follows the subtasks the run of the task line and the notes before them and the run of that note SHALL be separate (`1-2,4-4`). The subtree is one run. With `--json` the result SHALL have `file`, `line`, `end_line` (the last line read), `text`, `status`, `notes`, and `parent` (as in the task query, or null); with `--tree` it SHALL also have `subtasks`, each of the same shape without `parent`, nested to any depth. A line that is not a checkbox line, a missing file, or a line out of range SHALL be an error. Nothing SHALL be written.

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

#### Scenario: Note after the subtasks, node alone  {#s-6857}
*Verification*: **non-executable**
- **WHEN** line 1 is `- [o] main`, line 2 is `  * note`, line 3 is `  - [x] sub` and line 4 is `  * note after`, and the user runs `meta-notes task show project/foo.md:1`
- **THEN** the output SHALL be the header `project/foo.md:1-2,4-4` and lines 1, 2 and 4, and `end_line` SHALL be 4

### Requirement: Guarded tree writes  {#r-9e63}
Every command that writes a task's notes, a node or a subtree SHALL take `--expect`, SHALL compare it with the lines it replaces as last read (each line ignoring trailing whitespace, lines joined by a newline; `-` reads it from standard input), and SHALL write nothing, exit non-zero and report the lines as they are now (`current` in `--json`) when they differ. It SHALL write the file once, keep the file's line endings, and change no other line, except the ancestors' status characters (see "Status of ancestors"). `--text` SHALL give the new lines, one per line as written, or `-` to read them from standard input.

#### Scenario: Stale expect  {#s-0d86}
*Verification*: **non-executable**
- **WHEN** another edit changed a task's notes after the agent read them and the agent runs `task notes` with the old notes as `--expect`
- **THEN** the file SHALL be unchanged and the output SHALL report the current notes

### Requirement: Replace a task's notes  {#r-3adf}
`meta-notes task notes <file>:<line> --expect <notes> --text <notes>` SHALL replace every note the checkbox line owns, including notes after its subtasks, with the new notes written directly under the task line, before its subtasks. `--expect` SHALL be the current notes (empty for none) and an empty `--text` SHALL remove the notes. Each new note SHALL be non-blank, not a checkbox line, and indented deeper than the task; otherwise the command SHALL fail and write nothing. A subtask's own notes SHALL NOT change. The output SHALL be `<file>:<line>` with the old lines after `- ` and the new after `+ `, or `<file>:<line> unchanged` without a write; `--json` SHALL have `file`, `line` and `end_line` (of the new notes), `old`, `new` (lists of lines), `changed` and `ancestors`.

#### Scenario: Replace notes  {#s-03d5}
*Verification*: **non-executable**
- **WHEN** a task has two notes and a subtask and the user replaces its notes with one
- **THEN** the task SHALL have the one note directly under it, followed by the subtask unchanged

### Requirement: Add a subtask  {#r-7b2b}
`meta-notes task add <file> <text> --under <line> --expect <parent line>` SHALL add an open subtask line after the last line of the parent's subtree (its notes, subtasks and their notes), in the same form as `task add` with its `--due`, `--start`, `--time`, `--recur` and `--tag` options. The subtask SHALL be indented like the parent's first subtask, else two columns deeper than the parent (a tab when the parent's indent has a tab). `--expect` SHALL be the parent line as last read, and `--under` SHALL NOT be combined with `--line`. The parent's status SHALL NOT change. The output SHALL be `<file>:<line> added` and the line after `+ `.

#### Scenario: Add after the subtasks  {#s-1205}
*Verification*: **non-executable**
- **WHEN** a task has a note, two subtasks and a note after them, and the user adds a subtask under it
- **THEN** the new line SHALL come after the note that follows the subtasks, indented like the first subtask

### Requirement: Replace a node or a subtree  {#r-66b2}
`meta-notes task replace <file>:<line> --expect <lines> --text <lines> [--tree]` SHALL replace the checkbox line and its own notes, or with `--tree` its whole subtree, with the new lines. `--expect` SHALL be what `task show` prints for the same target. The first new line SHALL be a checkbox line at the task's indent, every other new line SHALL be indented deeper, and none SHALL be blank; otherwise the command SHALL fail and write nothing. Without `--tree` the task's subtasks SHALL stay where they are, below the new lines. The output and `--json` SHALL be as for `task notes`.

#### Scenario: Replace a subtree  {#s-0515}
*Verification*: **non-executable**
- **WHEN** the user runs `task replace project/foo.md:3 --tree` with the output of `task show project/foo.md:3 --tree` as `--expect`
- **THEN** every line of the subtree SHALL be replaced by the new lines in one write

### Requirement: Status of ancestors  {#r-7c52}
When `task update --status` changes a task's status character, or `task replace` changes the status character of the first line, the command SHALL set the status of each ancestor, nearest first, to the character at index `ceil(4 * checked / subtasks)` of ` .oOX`, where `checked` counts the ancestor's direct subtasks whose status is `x` or `X`, as bullets.vim does, in the same write. Only the status character SHALL change: no `✅` date, no next occurrence, no date inheritance; an ancestor that is `x` and computes `X` SHALL stay `x`. When the update adds the next occurrence of a recurring subtask, it SHALL count as a subtask of the parent. `task update` and `task replace` output SHALL list each changed ancestor with `ancestors` (`line`, `old`, `new`) in `--json`.

#### Scenario: Thresholds  {#s-2402}
*Verification*: **non-executable**
- **WHEN** a parent has four open subtasks and the user marks them done one at a time
- **THEN** the parent's status SHALL be `.`, `o`, `O` and `X` in turn

#### Scenario: Two levels  {#s-6fdf}
*Verification*: **non-executable**
- **WHEN** a subtask's only subtask is marked done
- **THEN** the subtask SHALL become `X` and its parent SHALL be set from it in the same write
