# Spec Delta

## ADDED Requirements

### Requirement: Entries without activity text are recorded
A time log entry SHALL be recorded when its activity line has activity text or at least one tag, or when the entry has a `start:` or `end:` line. An entry whose activity line has only tags, or is empty, SHALL count toward the day's totals and its tags toward time by tag, the same as any other entry. A bare `-` line with no tags and no `start:` or `end:` line SHALL be ignored.

#### Scenario: Tag-only entry
- **WHEN** the note `2026-09-25 Fri.md` has a log entry `- #proj-01 #research` with `* start: 09:00` and `* end: 10:00`
- **THEN** an entry SHALL be recorded from 09:00 to 10:00 with tags `proj-01` and `research`

#### Scenario: Empty activity line with times
- **WHEN** a log entry is `-` with `* start: 09:30` and `* end: 10:00`
- **THEN** an entry SHALL be recorded from 09:30 to 10:00 with no tags

#### Scenario: Stray empty bullet
- **WHEN** a log contains a line `-` with no tags and no `start:` or `end:` line
- **THEN** no entry SHALL be recorded for it
