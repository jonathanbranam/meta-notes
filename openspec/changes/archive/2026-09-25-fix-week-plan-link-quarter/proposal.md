## Why

A daily note's link to its week plan points at the wrong folder in weeks
that span two quarters. The shipped daily template builds the link as
`[[plan/week/{{week_start:%y}}-{{quarter}}/{{week_start:%Y-%m-%d}}]]`, but
`{{quarter}}` is the quarter of the daily note's date, while weekly notes
are filed under the quarter of their Monday. For Thursday 2026-04-02 the
link is `[[plan/week/26-Q2/2026-03-30]]`, but `meta-notes note weekly`
puts that week at `plan/week/26-Q1/2026-03-30.md`, so following the link
creates a second, misfiled week plan. The same happens for the first days
of every quarter (for 2026-01-01 the link says `25-Q1` instead of `25-Q4`).
The year part is already right because `%y` is read from `week_start`.

No template variable gives the Monday's quarter, so a template can't build
the correct path today.

## Dependencies

- **`note-create`**: moves template rendering into
  `scripts/meta_notes/template.py` and changes the `template` spec's
  documentation requirement. This change builds on both, so `note-create`
  should be archived first.

## What Changes

- Add a `{{week_quarter}}` template variable: the quarter (`Q1` to `Q4`) of
  `week_start`, the Monday of the note's week. It is a plain string, like
  `{{quarter}}`.
- The shipped daily template links to its week plan with
  `[[plan/week/{{week_start:%y}}-{{week_quarter}}/{{week_start:%Y-%m-%d}}]]`,
  which is always the path `meta-notes note weekly` uses for that date.
- The weekly template is unchanged: its `date` is the Monday, so
  `{{quarter}}` and `{{week_quarter}}` agree there.
- Document `{{week_quarter}}` in `:help meta-notes-template-variables`.
- Existing notes are not rewritten. Existing notes roots keep their copy of
  `resource/template/daily.md` until it is updated by hand or with
  `meta-notes init --force`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities
- `template`: adds the `week_quarter` variable, a requirement that the
  shipped daily template's week plan link matches the weekly note's path,
  and `week_quarter` in the documented variables.

## Impact

- `scripts/meta_notes/template.py`: `build_context` adds `week_quarter`
- `templates/daily.md` and its snapshot `test/fixtures/init_templates/daily.md`
- `test/fixtures/templates/daily-*.md`: the `2025-12-31` fixture is
  unchanged (its Monday is in the same quarter); `2026-04-02` changes from
  `26-Q2` to `26-Q1`
- `test/unit/test_template.py`, `test/unit/test_note.py`: new cases
- `doc/meta-notes.txt`: the variable list
