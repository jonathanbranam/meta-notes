# recurrence Specification

## Purpose
Specifies the recurrence rules a task's repeat marker can hold and how the next occurrence's date is computed, in Obsidian Tasks syntax. This is the rule module only; reading the marker from task lines and spawning the next occurrence are specified with the commands that use it.

## Requirements

### Requirement: Rule grammar  {#r-d48a}
A recurrence rule SHALL be matched case-insensitively, ignoring surrounding whitespace, as `every [N] day|week|month|year` (singular or plural unit, N a positive integer defaulting to 1), `every weekday`, or `every [N] week[s] on <days>`, each optionally followed by `when done`. `<days>` SHALL be one or more full English day names (Monday to Sunday) separated by commas, or by `and`, with an optional `and` before the last one; a name may repeat. N SHALL default to 1 and be a positive integer, as for the plain week rule. Any other text, including `every other week`, a day name without `every week on`, `every week on` with no day or an unknown day, and month-day rules, SHALL NOT be a rule.

#### Scenario: Plural and singular forms  {#s-8178}
*Verification*: **non-executable**
- **WHEN** the text is `every 3 months` or `every month`
- **THEN** the rule SHALL be every 3 months or every 1 month

#### Scenario: When done  {#s-5166}
*Verification*: **non-executable**
- **WHEN** the text is `every 2 weeks when done`
- **THEN** the rule SHALL step from the completion date

#### Scenario: Unsupported text  {#s-2554}
*Verification*: **non-executable**
- **WHEN** the text is `every Monday` or `every 0 days`
- **THEN** the text SHALL NOT be a rule

#### Scenario: Weekday list  {#s-ab90}
*Verification*: **non-executable**
- **WHEN** the text is `every week on Sunday, Monday, Tuesday, Wednesday, Thursday` or `every week on Sunday and Monday, and Tuesday when done`
- **THEN** the rule SHALL be every week on those five days, or on Sunday, Monday and Tuesday, the second stepping from the completion date

#### Scenario: Invalid weekday list  {#s-fda6}
*Verification*: **non-executable**
- **WHEN** the text is `every week on Funday`, `every week on Sunday,,Monday`, or `every week on`
- **THEN** the text SHALL NOT be a rule

### Requirement: Next occurrence  {#r-60f8}
The next date SHALL be the base date plus the rule's step. The base is the due date, or the completion date for a `when done` rule, and the caller chooses it. A month or year step SHALL clamp to the last day of the target month. `every weekday` SHALL give the next Monday to Friday after the base. A weekday list SHALL give the next listed day after the base, wrapping into the following week (Thursday to Sunday, for a list of Sunday to Thursday). For `every N weeks on <days>`, weeks SHALL run Monday to Sunday: the next date SHALL be the next listed day later in the base's week, else the first listed day of the week N weeks on. The result SHALL NOT be moved past today, so a late completion can give a date already overdue.

#### Scenario: Month-end clamping  {#s-886c}
*Verification*: **non-executable**
- **WHEN** 2026-01-31 steps by one month
- **THEN** the next date SHALL be 2026-02-28

#### Scenario: Late completion  {#s-b786}
*Verification*: **non-executable**
- **WHEN** `every 3 months` has base 2026-07-01 and is completed on 2026-10-05
- **THEN** the next date SHALL be 2026-10-01

#### Scenario: Weekday over a weekend  {#s-05f3}
*Verification*: **non-executable**
- **WHEN** `every weekday` has base Friday 2026-10-02
- **THEN** the next date SHALL be Monday 2026-10-05

#### Scenario: Weekday list across the week end  {#s-e294}
*Verification*: **non-executable**
- **WHEN** `every week on Sunday, Monday, Tuesday, Wednesday, Thursday` has base Thursday 2026-10-01
- **THEN** the next date SHALL be Sunday 2026-10-04

#### Scenario: Every two weeks on days  {#s-96c7}
*Verification*: **non-executable**
- **WHEN** `every 2 weeks on Monday, Friday` has base Friday 2026-10-02
- **THEN** the next date SHALL be Monday 2026-10-12
