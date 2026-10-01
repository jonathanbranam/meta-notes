## Purpose

Specifies `meta-notes time-log append` and `meta-notes time-log update`, which add and replace entries under a daily note's `### Log` and refuse when the log no longer holds what the caller expects, so an agent can't overwrite a change the user made in Vim.

## Requirements

### Requirement: Append one entry  {#r-6bf7}
`meta-notes time-log append <file> --text <line>` SHALL add one entry after the last entry of `### Log`: the `- ` header `--text`, a `* start:` line at `--start` (`HH:MM` or `9:30am`, default now), an `* end:` line only with `--end`, then one `* <note>` line per `--note`, in order. Times SHALL be written as `HH:MM`. The command SHALL fail without writing when `--text` isn't one line starting with `- `, a `--note` has a newline, `--end` is before `--start`, or the note has no `### Log`.

#### Scenario: Append with notes  {#s-b994}
*Verification*: **non-executable**
- **WHEN** the last entry is `- Work` open since 09:45 and the user appends `- Packed #trip` with `--start 13:00 --end 14:00 --note 'big suitcase'`
- **THEN** the log SHALL end with `- Packed #trip`, `  * start: 13:00`, `  * end:   14:00` and `  * big suitcase`

### Requirement: Append guard  {#r-b60c}
`append` SHALL require `--prev` equal to the last entry's header line and `--prev-start` equal to its start time, and SHALL require the last entry to have no end with `--prev-open` and to have one without it. For an empty log, `--first` SHALL replace the `--prev` options and SHALL fail when the log has entries. On any mismatch the command SHALL write nothing, exit non-zero, and show the last entry (`current` with `--json`).

#### Scenario: Stale last entry  {#s-740a}
*Verification*: **non-executable**
- **WHEN** the user appends with `--prev '- Work'` but the last entry is `- Review`
- **THEN** the command SHALL exit non-zero, the file SHALL be unchanged, and the error and `current` SHALL show the `- Review` entry

### Requirement: Close the previous entry  {#r-335e}
`--close-prev`, which needs `--prev-open`, SHALL write the last entry's `end:` as the new `--start` in the same write, replacing an existing placeholder `end:` line or adding one after the `start:` line.

#### Scenario: Switch activity  {#s-edf7}
*Verification*: **non-executable**
- **WHEN** the last entry is open since 13:30 and the user appends with `--prev-open --close-prev --start 14:00`
- **THEN** the last entry SHALL gain `  * end:   14:00` and the new entry SHALL follow it

### Requirement: Replace whole entries  {#r-10ff}
`meta-notes time-log update <file> --expect <text> --text <text>` SHALL find the one contiguous run of whole entries in `### Log` whose lines equal `--expect` exactly, where `--expect` starts at a header line and ends at an entry's last line, and SHALL replace it with `--text`, zero or more entries; an empty `--text` SHALL delete the run. Zero matches SHALL fail and show the entries with the same headers or start times, marking the lines that differ with `~` (`current` with `--json`); two or more matches SHALL fail. Nothing SHALL be written on failure.

#### Scenario: Split an entry  {#s-53c7}
*Verification*: **non-executable**
- **WHEN** `--expect` is the `- Work` entry from 09:45 to 13:00 and `--text` is two entries covering 09:45-11:00 and 11:00-13:00
- **THEN** those two entries SHALL replace it and no other line SHALL change

#### Scenario: Entry changed meanwhile  {#s-d4a8}
*Verification*: **non-executable**
- **WHEN** `--expect` ends at 12:00 but the entry ends at 13:00
- **THEN** the command SHALL fail, leave the file unchanged, and show the entry with the `end:` line marked `~`

### Requirement: Validate new entries  {#r-3e0c}
Each entry in `update`'s `--text` SHALL have a `- ` header, a valid `start:`, and an `end:` that is valid when present and not before its own start. Only the log's last entry MAY lack an `end:`. Lines of `--text` outside an entry, and blank lines, SHALL be errors. Any failure SHALL reject the whole update.

#### Scenario: Open entry in the middle  {#s-34ff}
*Verification*: **non-executable**
- **WHEN** `--text` has an entry with no `end:` and an entry after it in the log
- **THEN** the command SHALL fail and write nothing

### Requirement: Gaps and overlaps warn  {#r-6fd4}
A gap or overlap between neighbouring entries touched by an edit, including the entries before and after the replaced run, SHALL be written anyway and reported as a warning, `*Gap of N min*` or `*Overlap of N min*`, and in `--json` as `warnings`. With `--json`, both commands SHALL return `ok`, `file` and `written` (`line` and `text`).

#### Scenario: Overlap  {#s-1422}
*Verification*: **non-executable**
- **WHEN** an update makes an entry end at 13:10 and the next starts at 13:00
- **THEN** the edit SHALL be written and the warning SHALL read `*Overlap of 10 min*`
