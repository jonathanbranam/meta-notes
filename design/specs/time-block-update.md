## Purpose

Specifies `meta-notes time-block update` and `replace`, which writes the Plan and Actual cells of a note's `### Time Block` table by row time, padded to the column and guarded against stale reads, so agents fill the table without miscounting widths or overwriting each other.

## Requirements

### Requirement: Rows are found by time  {#r-882f}
`meta-notes time-block update <file> --time <time>` SHALL edit the Time Block row whose time equals `<time>`, given as `HH:MM` or `9:30am`. `<file>` SHALL be relative to the notes root, or an absolute path inside it. At least one of `--plan` and `--actual` SHALL be given, or the command SHALL fail without writing. `--through <time>` SHALL cover every row from `--time` through it, inclusive. Cell text SHALL have `|` replaced with `/` and newlines with spaces, and SHALL be padded to the column's width.

#### Scenario: Fill one Plan cell  {#s-a865}
*Verification*: **non-executable**
- **WHEN** the `9:15am` row's Plan is empty and the user runs `meta-notes time-block update plan/daily/26-Q4/2026-10-01 Thu.md --time 9:15am --plan 'write spec'`
- **THEN** that Plan cell SHALL read `write spec`, padded so the row's line keeps its width, and no other line SHALL change

#### Scenario: Range  {#s-81ef}
*Verification*: **non-executable**
- **WHEN** the user runs the command with `--time 9:15am --through 9:45am --plan 'write spec'` and those rows' Plan cells are empty
- **THEN** the Plan cells of the 9:15am, 9:30am and 9:45am rows SHALL be written

### Requirement: Expect guard  {#r-afba}
Every target cell SHALL be compared, stripped, with `--expect` (empty when not given). If any cell differs, the command SHALL write nothing, exit non-zero, and name each mismatched row, column and its current text in the error and, with `--json`, in a `current` list of `time`, `column` and `text`. With both `--plan` and `--actual`, `--expect` SHALL apply to both cells.

#### Scenario: Cell already filled  {#s-6ce0}
*Verification*: **non-executable**
- **WHEN** the 9:00am Plan is `standup` and the user runs `--time 9:00 --plan 'review' --json` without `--expect`
- **THEN** the command SHALL exit non-zero, the file SHALL be unchanged, and the JSON SHALL have `ok` false and `current` listing the 9:00am `plan` cell with text `standup`

#### Scenario: Expectation matches  {#s-2c2b}
*Verification*: **non-executable**
- **WHEN** the 9:00am Plan is `standup` and the user runs `--time 9:00 --plan 'review' --expect standup`
- **THEN** the cell SHALL become `review`

### Requirement: Refuse unsafe tables and text  {#r-fcce}
The command SHALL write nothing and exit non-zero, saying why, when: the file has no Time Block; `--time` or `--through` isn't a row and `--create` isn't given (a "time slot not found" error); the cells of an edited column differ in width between rows (a ragged table, naming the rows); or the text is wider than its column (naming the column's width and the text's length). It SHALL NOT truncate text or widen a column.

#### Scenario: Text too wide  {#s-09e7}
*Verification*: **non-executable**
- **WHEN** the Plan column holds 20 characters and the text is 21
- **THEN** the command SHALL fail with an error giving 20 and 21, and the file SHALL be unchanged

#### Scenario: Missing slot  {#s-9527}
*Verification*: **non-executable**
- **WHEN** there's no 9:45am row and the user runs `--time 9:45am --plan x` without `--create`
- **THEN** the command SHALL fail with "time slot not found" and the file SHALL be unchanged

### Requirement: Create a missing row  {#r-6b6a}
With `--create` and no `--through`, a missing `--time` row SHALL be added in time order, padded to the table's widths, with its label right-aligned like the existing ones (` 7:00am`), and then updated. If the row exists, `--create` SHALL change nothing by itself. `--create` with `--through` SHALL fail without writing.

#### Scenario: Add an early row  {#s-6983}
*Verification*: **non-executable**
- **WHEN** the first row is `8:45am` and the user runs `--time 7:00am --plan flight --create`
- **THEN** a `7:00am` row with Plan `flight` SHALL appear before the `8:45am` row

### Requirement: Columns come from the header  {#r-77bb}
`time-block update`, `time-block replace` and `checkin` SHALL find the Plan and Actual cells by the table header's names (case-insensitive), not by position. A Time Block without both headers SHALL make them fail, writing nothing and naming the headers found.

#### Scenario: Columns in another order  {#s-4203}
*Verification*: **non-executable**
- **WHEN** the header is `Time | Actual | Notes | Plan` and the user runs `--plan go`
- **THEN** the fourth cell SHALL be written, not the third

#### Scenario: No Actual header  {#s-bb68}
*Verification*: **non-executable**
- **WHEN** the header is `Time | Plan | Result`
- **THEN** the command SHALL fail naming `Time, Plan, Result` and the file SHALL be unchanged

### Requirement: Replace a range of rows  {#r-7d26}
`meta-notes time-block replace <file> --time A --through B --expect <rows> --text <rows>` SHALL rewrite the rows from A through B. `--expect` SHALL be compared with the file's rows cell by cell, stripped, so padding need not match; any difference SHALL write nothing and list each row, column and current text (`current` with `--json`). `--text` rows SHALL have one cell per header cell and are padded to the file's widths, with times right-aligned. Every time in the range SHALL remain; new times inside A..B SHALL be added in time order. Times outside the range, a duplicate time, a wrong cell count, a deleted row or text wider than its column SHALL fail naming the row. Every check SHALL run before anything is written, so a failure writes nothing.

#### Scenario: Reorder and add a row  {#s-704b}
*Verification*: **non-executable**
- **WHEN** the user moves `mtg: standup` from 9:00am to 9:15am and adds a 9:10am row, with `--expect` the rows as read
- **THEN** the rows SHALL read in time order, padded to the table's widths, and no other line SHALL change

#### Scenario: Stale expectation  {#s-3060}
*Verification*: **non-executable**
- **WHEN** a Plan cell differs from `--expect`
- **THEN** nothing SHALL be written and the error SHALL name that row and column with its current text

#### Scenario: Text too wide  {#s-38f9}
*Verification*: **non-executable**
- **WHEN** one new cell is wider than its column
- **THEN** the command SHALL fail naming the row and the file SHALL be unchanged
