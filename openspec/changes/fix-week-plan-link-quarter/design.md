## Context

After `note-create`, template variables come from
`template.build_context(note_date, filepath, today)` in
`scripts/meta_notes/template.py`, and weekly note paths from
`note.periodic_note("weekly", d)`, which uses the Monday's two-digit year
and quarter for the `YY-QN` folder. The daily template gets its year from
`{{week_start:%y}}`, which is right, and its quarter from `{{quarter}}`,
which is the daily date's quarter, which is wrong. See proposal.md for the
failure cases.

Two shipped fixtures record the current output: `daily-2026-04-02.md`
contains the wrong link, and `daily-2025-12-31.md` is unaffected.

## Goals / Non-Goals

**Goals:**
- A daily note's week link always matches `meta-notes note weekly` for the
  same date.

**Non-Goals:**
- Repairing links in daily notes already created. They can be found with
  a grep for `Week Plan: [[plan/week/` and fixed by hand. A migration
  command isn't worth it for a handful of notes a year.
- Updating the templates in existing notes roots automatically. `init`
  never overwrites templates without `--force`.
- Changing `{{quarter}}`. Other templates, including the weekly and
  quarterly ones, rely on it meaning the note date's quarter.

## Decisions

### 1. A `week_quarter` string variable

`build_context` adds `"week_quarter": quarter(week_start)`, next to
`week_start` and `week_end`. Like `quarter` it is a plain string, so the
"date features apply only to named date variables" rule is unchanged.

Alternatives considered:
- **A `%q` quarter directive for date variables** (`{{week_start:%q}}`).
  More general, since any date variable could give its quarter, but it
  invents a strftime directive that exists nowhere else and would surprise
  anyone who knows strftime. Can be added later if another need appears.
- **A `{{week_plan}}` path variable** (`plan/week/26-Q1/2026-03-30`). Makes
  the template shortest and can't drift from `periodic_note`, but it puts
  plan-folder layout knowledge into the template renderer, which is
  deliberately kind-agnostic (`note-create` design, Decision 1), and it only
  serves this one link. The quarter variable keeps the path visible in the
  template, where users can see and change it.
- **Change `{{quarter}}` to use the Monday in daily notes.** Makes the
  meaning of a variable depend on the note kind. Rejected.

### 2. Tie the template to the path rule with a test

The requirement is that the link equals the weekly path, which a fixed
fixture can't check for every date. `test_note.py` gets a test that renders
the shipped daily template for every day of 2025 and 2026 (730 dates, with
command blocks stubbed) and asserts the `Week Plan:` link plus `.md` equals
`note.periodic_note("weekly", d)[0]`. That covers every quarter and year
boundary and the week-53 year.

### 3. Fixture update

`daily-2026-04-02.md` is edited to `26-Q1`, and the docstring of the
fixture test records the edit, as with the day-name change.

## Risks / Trade-offs

- [Existing notes roots keep the old daily template] → the proposal and
  `:help` say how to update it; the bug only shows in weeks that span two
  quarters, so a stale template fails no worse than today.
- [Users with their own week links in custom templates keep using
  `{{quarter}}`] → the docs for `week_quarter` say to use it for week plan
  paths.

## Migration Plan

Ship the variable and template together. Existing daily notes are
untouched. Rollback is reverting the change; a template using
`{{week_quarter}}` would then render an unknown-variable comment, so revert
the template with the code.
