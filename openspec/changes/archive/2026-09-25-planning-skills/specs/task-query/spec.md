## MODIFIED Requirements

### Requirement: Task tags
Every `#tag` on a task line SHALL be a tag of the task, wherever it appears in the line. A tag is `#` followed by letters, digits, `_`, or `-`. The tags `#mtg`, `#pers`, `#per`, and `#waiting` SHALL be read as `meeting`, `personal`, `personal`, and `wait`, the same aliases that time log entries use. Tags SHALL be compared ignoring case.

#### Scenario: Several tags
- **WHEN** a task line is `- [ ] #aftr #design follow up 📅 2026-07-08`
- **THEN** its tags SHALL be `aftr` and `design`

#### Scenario: Alias
- **WHEN** a task line is `- [ ] #mtg prep 📅 2026-10-01`
- **THEN** its tags SHALL be `meeting`, and `--tag mtg` and `--tag meeting` SHALL both select it

#### Scenario: Waiting alias
- **WHEN** a task line is `- [ ] #waiting legal sign-off 📅 2026-10-15`
- **THEN** its tags SHALL be `wait`, and `--tag wait` and `--tag waiting` SHALL both select it
