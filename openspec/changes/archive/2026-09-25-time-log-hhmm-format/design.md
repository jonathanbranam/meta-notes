## Context

The parser (`scripts/time_tracking.py`) already handles bare times. `_parse_entry_time` tries `_parse_datetime` (full date), then `_parse_bare_time_24h` and `_parse_time` (12-hour), combining a bare time with the date that `_extract_date_from_filepath` pulls from the note's filename. The only parser gap is `_parse_datetime`, whose regex requires a three-letter day abbreviation.

`{{date}}` renders as `YYYY-MM-DD Ddd` by default, so the daily template's starter entry is `* start: 2026-09-25 Fri HH:MM`. The shipped templates are pinned by two sets of byte-for-byte fixtures:

- `test/fixtures/init_templates/daily.md`: a copy of `templates/daily.md`, checked by `test/unit/test_init.py`.
- `test/fixtures/templates/daily-{2025-12-31,2026-02-13,2026-04-02}.md`: goldens rendered by the old Vimscript template engine, checked by `test/unit/test_template.py::test_render_matches_vim_fixture`. They belong to the in-progress `note-create` change and are not yet committed.

Syntax highlighting (`after/syntax/markdown.vim`) has one time pattern, `metaNotesTime`, which only matches 12-hour times. No automated test covers syntax highlighting; `test/syntax_test.md` is a sample file for checking it by eye.

## Goals / Non-Goals

**Goals:**
- Make the day abbreviation optional in full-date timestamps without changing how any currently valid timestamp parses.
- Keep the template fixtures byte-for-byte accurate after the template changes.

**Non-Goals:**
- Converting existing notes to bare times.
- Handling entries that cross midnight with bare times (an `end:` earlier than its `start:`). Writing the full date on the `end:` line still covers this.
- Checking the day abbreviation against the date.
- Changing the time block table or its `H:MMam` format.
- Adding automated syntax highlighting tests.

## Decisions

**Make the day abbreviation an optional group in the existing regex.** Change `\s+\w{3}\s+` to `(?:\s+\w{3})?\s+` in `_parse_datetime`, which keeps it as the single full-date parser. Adding a second pattern or a separate function was considered and rejected: that would duplicate the validation and the `datetime` construction for a one-token difference. The hour stays two digits (`\d{2}`), as it is today.

**Keep the parse order in `_parse_entry_time`.** Full date first, then bare 24-hour, then bare 12-hour. The formats can't overlap (a full date starts with `YYYY-`, bare 24-hour has no am/pm), so the order only matters for speed, and the existing order is already correct.

**Highlight only times on `start:` / `end:` lines.** Add a second `metaNotesTime` match that picks out an `H:MM` / `HH:MM` with an optional am/pm, using a lookbehind to require a `start:` / `end:` line:

```vim
syntax match metaNotesTime /\(^\s*\*\s*\(start\|end\):.*\)\@<=\<\d\{1,2}:\d\{2}\(\s*\(am\|pm\)\)\?/
```

A pattern anchored with `^ ... \zs` was tried first and never matched: the match then starts at column 0, where markdown's list-marker item claims the `*` first. The lookbehind makes the match start at the time itself.

A bare `\d\{1,2}:\d\{2}` pattern anywhere was rejected. It would also highlight ratios, Bible-style references and `HH:MM` inside prose or code. The existing 12-hour pattern stays as it is, so time block and prose highlighting don't change.

**Edit the golden fixtures by hand instead of regenerating them.** The Vimscript renderer that produced `test/fixtures/templates/` has been removed, so the goldens can't be regenerated. The template change only touches the two starter-entry lines, so in each `daily-*.md` golden, `* start: <date> <Ddd> HH:MM` becomes `* start: HH:MM` (and the same for `end:`). `test/fixtures/init_templates/daily.md` is replaced with a copy of the new `templates/daily.md`.

**Document the format in the help file, not the README.** Add a time log format subsection under `*meta-notes-time-tracking*` with the entry structure and the four timestamp formats, bare `HH:MM` first. The help file already owns the time tracking docs.

## Risks / Trade-offs

- [The `note-create` change owns the golden fixtures and is still in progress] → Implement this change after `note-create` lands, or edit the goldens in whichever working tree has them. The fixture tasks spell out the exact lines so either change can apply the edit.
- [Existing notes root templates] → `meta-notes init` only overwrites a notes root's existing `resource/template/daily.md` when run with `force`, so existing notes roots keep their current template. Your setup has already switched, so nothing needs to happen there.
- [Optional day abbreviation accepts a wider input] → Any three-letter word was already accepted in that position, and dropping it only widens the input to a strictly simpler form, so no timestamp that parses today will parse differently.
