# Design

## Context

`_parse_time_log_lines` strips tags from the activity line to get `activity`, and `_create_time_log_entry` returns `None` when `activity` is empty. Every report (day listing, totals, by tag, period summaries) reads the parser's output, so the dropped entry disappears everywhere and `day_log_items` sees a hole between its neighbours, which it reports as a gap.

The day listing already prints each entry's line as written (`text`), so a kept tag-only entry needs no special formatting.

## Goals / Non-Goals

**Goals:**
- Count tag-only and text-less entries as logged time.

**Non-Goals:**
- Labelling or flagging entries without activity text, in the text report or JSON. The line as written (its tags) is enough, and a missing title isn't a mistake.
- Inferring a title from a previous entry with the same tags.

## Decisions

**Keep an entry when it has activity text, tags, or a time line.** The parser already tracks `start_time`/`end_time`; the decision moves to `_create_time_log_entry` after the detail lines are read. `activity` becomes `''` for a tag-only entry. Requiring *something* keeps a stray blank `-` (e.g. an unfinished bullet) out of the report. Alternative: keep every bullet — rejected because an empty bullet with no times would be listed with `*MISSING START TIME*` and `*MISSING END TIME*` for no reason.

An entry with no text and unparseable times (`-` / `* start: HH:MM`) is kept, since it has a `start:` line, and listed with `*MISSING START TIME*` — correct, as that is a mistake to fix.

**No report changes.** Considered a plain `(no title)` label (and `(untitled)`, `[missing title]`, `No details`); dropped because the line as written already shows what the entry was, and a label would need the report to re-derive the title from `text`.

## Risks / Trade-offs

- [Totals in past daily notes change when re-reported] → This is the correction; tag-only entries were silently uncounted. Called out in the proposal.
- [Code elsewhere assumes `activity` is non-empty] → Only `_create_time_log_entry` reads it today; task 1.2 checks the totals paths with a tag-only entry.
