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
The skill SHALL replan only rows that haven't happened; leave Actual blank when the plan happened; for a past row whose plan didn't happen, keep the Plan, wrap it in `~~ ~~` and write a short Actual; treat the Time Log as the literal truth. It SHALL keep meetings (`mtg:`) in place, keep `[brackets]`, `(parens)` and other prefixes as written without inventing any, write lowercase except proper names, and use no Markdown emphasis in the table other than the tildes.

#### Scenario: Plan didn't happen  {#s-7b12}
*Verification*: **non-executable**
- **WHEN** a past row's plan was not what the user did
- **THEN** the skill SHALL wrap its Plan in `~~ ~~` and put a short summary in Actual, without rewriting the Plan
