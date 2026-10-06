# time-block-skill Specification

## Purpose
Specifies the `time-block` skill, which edits the daily note's Time Block and Time Log for the user through the CLI, in the user's style.

## Requirements

### Requirement: The time-block skill ships with the plugin  {#r-7b01}
The plugin SHALL ship a `time-block` skill as `skills/time-block/SKILL.md`, installed into a notes root by `meta-notes init` like the other skills. Its description SHALL say it applies when the user asks to plan, replan, fix or fill the Time Block or to record what they did instead. It SHALL start from `meta-notes conventions` and the notes root's `CLAUDE.md`, and SHALL edit the table and the log only through `time-block update`, `time-block replace`, `checkin actual`, `time-log append` and `time-log update`, reading first and passing `--expect`.

#### Scenario: Installed by init  {#s-7b11}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes init`
- **THEN** `.claude/skills/time-block` SHALL link to the plugin's `skills/time-block`

### Requirement: Time Block content rules  {#r-7b02}
The skill SHALL replan only rows that haven't happened; leave Actual blank when the plan happened; for a past row whose plan (made or approved by the human) didn't happen, keep the Plan, wrap it in `~ ~` and write a short Actual; for a past row with an agent-filled plan the human never approved that didn't happen, replace the Plan with `~no plan~` and write a short Actual; for a past row with an empty Plan, set the Plan to `~no plan~` and write a short Actual; treat the Time Log as the literal truth. It SHALL keep meetings (`mtg:`) in place, keep `[brackets]`, `(parens)` and other prefixes as written without inventing any, write lowercase except proper names (project names stay lowercase), and use no Markdown emphasis in the table other than the tildes. It SHALL fill the Plan of every row an event (meeting, concert, appointment, errand) spans, not just its first, write travel to and from the event as its own run of rows before and after the event's rows, and, when the end is unknown, use a typical length and tell the user or ask. When replanning, it SHALL check what the change pushes out: deadlines, pickups, leave-by times.

#### Scenario: Human-made or approved plan didn't happen  {#s-7b12}
*Verification*: **non-executable**
- **WHEN** a past row's plan was made or approved by the human and was not what the user did
- **THEN** the skill SHALL wrap its Plan in `~ ~` and put a short summary in Actual, without rewriting the Plan

#### Scenario: Agent-filled unapproved plan didn't happen  {#s-7b12b}
*Verification*: **non-executable**
- **WHEN** a past row's plan was filled by an agent and the human never approved it, and it did not happen
- **THEN** the skill SHALL replace the Plan with `~no plan~` and put a short summary in Actual

#### Scenario: No plan was made  {#s-7b13}
*Verification*: **non-executable**
- **WHEN** a past row has an empty Plan
- **THEN** the skill SHALL set the Plan to `~no plan~` and put a short summary in Actual
