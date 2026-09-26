# calendar-skill Specification

## Purpose
Specifies the `calendar` skill, which answers the user's questions about their meetings (with whom, about what, when, and whether they're free) by reading `meta-notes calendar --json`.

## Requirements

### Requirement: The calendar skill ships with the plugin
The plugin SHALL ship a `calendar` skill as `skills/calendar/SKILL.md`, installed into a notes root by `meta-notes init` like the other skills. Its description SHALL say it answers questions about the user's calendar and meetings: who they meet, meetings about a topic, when a meeting is, and free time. It SHALL NOT trigger on planning a day or week, which `daily-plan` and `weekly-plan` do. When `meta-notes` is not on `PATH`, the skill SHALL stop and tell the user how to install it.

#### Scenario: Installed by init
- **WHEN** the user runs `meta-notes init`
- **THEN** `.claude/skills/calendar` SHALL link to the plugin's `skills/calendar`

### Requirement: Read-only lookups with JSON
The skill SHALL read the calendar only with `meta-notes calendar --json`, using `--with` for people and `--search` for topics, and SHALL NOT read the export or cache files directly. It SHALL NOT edit notes, tasks, or the calendar.

#### Scenario: Meetings with a person
- **WHEN** the user asks "find any meetings with Loan Bui next week" on Friday 2026-09-25
- **THEN** the skill SHALL run `meta-notes calendar --date 2026-09-28..2026-10-02 --with "Loan Bui" --json`

#### Scenario: Meetings about a topic
- **WHEN** the user asks "find all meetings about EFP" on 2026-09-25
- **THEN** the skill SHALL run `meta-notes calendar --date 2026-09-25..2026-10-22 --search EFP --json`

### Requirement: Periods from the question
The skill SHALL turn the question's time words into a `--date` period: `today`, `tomorrow`, a weekday name (its next occurrence, today included), `this week` and `next week` (Monday to Friday), `this month` and `next month`, and explicit dates or ranges. With no time words, the period SHALL be today and the 27 days after it. The skill SHALL state the period it searched.

#### Scenario: No period given
- **WHEN** the user asks about meetings with Sapna on 2026-09-25 without naming a time
- **THEN** the skill SHALL search 2026-09-25..2026-10-22 and say so

### Requirement: Finding people and topics
The skill SHALL pass names and topics as the user gave them. When a `--with` search finds nothing, it SHALL retry once with the first name alone and, when that matches, SHALL say whom it matched. When one name matches different people (by `matches.with[].people`), it SHALL list them and ask which one the user meant, or answer for each. When a `--search` finds nothing, it SHALL say so and MAY retry once with a close variant (such as the expanded form of an acronym) it names.

#### Scenario: Two people match
- **WHEN** `--with zach` matches `Zachary Kim` in one meeting and `Zach Ortiz` in another
- **THEN** the skill SHALL list both people and their meetings, or ask which one the user meant

### Requirement: 1-1 meetings
The skill SHALL treat an event as a 1-1 with a person when it matches `--with` for that person and either has `attendee_count` 2, or has a title containing `1:1`, `1-1`, `1on1`, `1 on 1`, or `one on one` (ignoring case) and no more than 3 attendees.

#### Scenario: 1-1 next week
- **WHEN** the user asks "do I have a 1-1 with Zach next week" and next week has a meeting with the user and Zachary Kim as its only two attendees
- **THEN** the skill SHALL answer yes with that meeting's day, time, and title

#### Scenario: Group meeting is not a 1-1
- **WHEN** the only meeting with Zach next week has 8 attendees and the title `Platform sync`
- **THEN** the skill SHALL answer that there's no 1-1 and mention the group meeting

### Requirement: Reporting
The skill SHALL answer the question first, then list the matching events one per line with day, time, and title, noting the user's response when it is `maybe` or `no-reply` and, for `--search`, where the text matched when it wasn't the title. It SHALL say how old the export is and pass on the command's warnings. When the command fails, it SHALL offer exporting from Google Calendar into the `ics/` folder the error names or, when calendar support is not installed, running `meta-notes init`, as the planning skills do.

#### Scenario: Stale export
- **WHEN** the command succeeds with a warning that the export is 6 days old
- **THEN** the answer SHALL say the export is 6 days old and may miss recent changes
