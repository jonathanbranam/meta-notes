## ADDED Requirements

### Requirement: People filter
`meta-notes calendar` SHALL accept `--with NAME`, repeatable. A person SHALL match NAME when every word of NAME, ignoring case, is the start of a word in the person's name or email address, in any order; words are runs of letters and digits. An event SHALL match NAME when its organizer or any of its attendees who are people matches, checking every attendee, not only those listed in `attendees`. With `--with`, only events that match every NAME SHALL be included. A NAME without letters or digits SHALL be an error.

#### Scenario: First name as a prefix
- **WHEN** the user runs `meta-notes calendar --with zach` and an event has the attendee `Zachary Kim <zkim@example.com>`
- **THEN** the event SHALL be included

#### Scenario: Name found in the email address
- **WHEN** the user runs `--with "Loan Bui"` and an attendee has no name and the address `bui.loan@example.com`
- **THEN** the event SHALL be included

#### Scenario: Attendee past the list cap
- **WHEN** the user runs `--with sapna` and Sapna is the 25th of 30 attendees
- **THEN** the event SHALL be included, and its `matches` SHALL list Sapna

#### Scenario: Two names
- **WHEN** the user runs `--with zach --with sapna` and an event has Zach but not Sapna
- **THEN** the event SHALL NOT be included

#### Scenario: Word start only
- **WHEN** the user runs `--with ann` and the only attendee is `Joanna Smith <jsmith@example.com>`
- **THEN** the event SHALL NOT be included

### Requirement: Text search
`meta-notes calendar` SHALL accept `--search TEXT`, repeatable. An event SHALL match TEXT when its title, location, or description contains TEXT, ignoring case. With `--search`, only events that match every TEXT SHALL be included.

#### Scenario: Topic in the description
- **WHEN** the user runs `--search efp` and an event titled `Quarterly sync` has `EFP rollout` in its description
- **THEN** the event SHALL be included, with `description` as the matching field

#### Scenario: Filters combined
- **WHEN** the user runs `--with zach --search 1:1`
- **THEN** only events that match both SHALL be included

### Requirement: Filtered output
With `--with` or `--search`, the text and JSON output SHALL include only the days in PERIOD that have a matching event, in date order, each with only its matching events. When no event matches, the command SHALL succeed; the text output SHALL be the line `No matching events.` and the JSON `days` SHALL be empty. In the JSON, each included event SHALL have `matches`, an object with `with`, a list with one entry per `--with` NAME (`name`, and `people`: every organizer or attendee that matched, each with `name`, `email`, and `response`), and `search`, a list with one entry per `--search` TEXT (`text`, and `fields`: the matching fields among `title`, `location`, and `description`). Without a filter, the output SHALL be unchanged, and events SHALL NOT have `matches`.

#### Scenario: Only matching days
- **WHEN** the user runs `meta-notes calendar --date 2026-09-28..2026-10-02 --with zach` and Zach is only in a meeting on 2026-09-30
- **THEN** the output SHALL have only the day 2026-09-30, with only that meeting

#### Scenario: No matches
- **WHEN** no event in PERIOD matches `--with nobody`
- **THEN** the command SHALL exit 0, print `No matching events.`, and with `--json` return an empty `days`

#### Scenario: Matches in JSON
- **WHEN** the user runs `--with zach --json` and Zachary Kim accepted the meeting
- **THEN** the event's `matches.with` SHALL be `[{"name": "zach", "people": [{"name": "Zachary Kim", "email": "zkim@example.com", "response": "yes"}]}]`
