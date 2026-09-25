# date-period Specification

## Purpose
Specifies the shared `--date` syntax that every meta-notes command taking a day or a range of days uses, so the same text names the same period in task queries, time reports, and planning commands.

## Requirements

### Requirement: Accepted period forms
A `--date` value SHALL be one of these forms, and SHALL resolve to an inclusive START and END date:

| Form | Example | START | END |
|---|---|---|---|
| `YYYY-MM-DD` | `2026-11-15` | that day | that day |
| `YYYY-MM-DD..YYYY-MM-DD` | `2026-11-02..2026-11-08` | first date | second date |
| `YYYY-MM` | `2026-11` | first day of the month | last day of the month |
| `YYYY-Qn` (n = 1–4) | `2026-Q4` | first day of the quarter | last day of the quarter |
| `YYYY` | `2026` | January 1 | December 31 |

When `--date` is omitted, the period SHALL be today (START and END both today). No other forms SHALL be accepted, including relative names and ISO week numbers.

#### Scenario: Single day
- **WHEN** `--date 2026-11-15` is given
- **THEN** START and END SHALL both be 2026-11-15

#### Scenario: Range
- **WHEN** `--date 2026-11-02..2026-11-08` is given
- **THEN** START SHALL be 2026-11-02 and END SHALL be 2026-11-08

#### Scenario: Month
- **WHEN** `--date 2026-02` is given
- **THEN** START SHALL be 2026-02-01 and END SHALL be 2026-02-28

#### Scenario: Quarter
- **WHEN** `--date 2026-Q4` is given
- **THEN** START SHALL be 2026-10-01 and END SHALL be 2026-12-31

#### Scenario: Year
- **WHEN** `--date 2026` is given
- **THEN** START SHALL be 2026-01-01 and END SHALL be 2026-12-31

#### Scenario: Default
- **WHEN** `--date` is omitted on 2026-09-25
- **THEN** START and END SHALL both be 2026-09-25

### Requirement: Invalid periods are errors
A `--date` value that matches none of the accepted forms, names a date that doesn't exist, or gives a range whose first date is after its second SHALL make the command fail with an error that names the value and lists the accepted forms. The command SHALL NOT run with a partial or guessed period.

#### Scenario: Unknown form
- **WHEN** `--date next-month` is given
- **THEN** the command SHALL exit non-zero with an error naming `next-month` and listing the accepted forms

#### Scenario: ISO week
- **WHEN** `--date 2026-W45` is given
- **THEN** the command SHALL exit non-zero with the invalid-period error

#### Scenario: Impossible date
- **WHEN** `--date 2026-02-30` is given
- **THEN** the command SHALL exit non-zero with the invalid-period error

#### Scenario: Reversed range
- **WHEN** `--date 2026-11-08..2026-11-02` is given
- **THEN** the command SHALL exit non-zero with the invalid-period error
