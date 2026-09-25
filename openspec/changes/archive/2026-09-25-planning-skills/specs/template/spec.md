## ADDED Requirements

### Requirement: Shipped daily template ceremony sections
The shipped daily template SHALL include a `## Follow Up` section and the ceremony marker lines `- [ ] plan complete` and `- [ ] shutdown complete`, each once. The marker lines SHALL have no date markers, so task queries don't list them.

#### Scenario: New daily note
- **WHEN** a daily note is created from the shipped template for 2026-09-25
- **THEN** it SHALL contain a `## Follow Up` heading, one `- [ ] plan complete` line, and one `- [ ] shutdown complete` line

#### Scenario: Markers are not tasks
- **WHEN** the user runs `meta-notes tasks --all --status all` in a notes root with that daily note
- **THEN** neither marker line SHALL be listed

### Requirement: Shipped weekly template ceremony sections
The shipped weekly template SHALL include `## Review` and `## Plan` sections and the ceremony marker lines `- [ ] review complete` and `- [ ] plan complete`, each once, with no date markers.

#### Scenario: New weekly note
- **WHEN** a weekly note is created from the shipped template for the week of 2026-09-21
- **THEN** it SHALL contain `## Review` and `## Plan` headings, one `- [ ] review complete` line, and one `- [ ] plan complete` line
