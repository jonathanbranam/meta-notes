---
id: mn-m9qv
title: "lists: note format, meta-notes list commands and the agent's list guide"
kind: feature
created: 2026-11-07
created_by: external:orchestrator
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: [mn-yznt, mu-5tju]
---

## The ask

From the human, via aide (meta-notes-ui, m-0184), 2026-11-07, verbatim: "Yeah, start the work on the shopping list between all of meta-notes, the UI, and everything." The design is on meta-notes-ui epic mu-5tju (every decision quoted there) and summarised in mn-yznt's resolution. Read both before planning.

## Goal

Agent-first shopping lists. The notes aide hears "I'm going to Walmart, make me a list", reads the human's tasks, and builds the list with `meta-notes list` commands. The meta-notes-ui Lists tab (mu, later ticket) reads and checks lists through the same commands.

## What to build

1. **Spec the list note format** (with the other note-format specs/docs):
   - Path `resource/lists/<YY-Qn>/<YYYY-MM-DD> <name>.md`, quarter folders like daily notes.
   - Ordered groups (headings, e.g. store sections) holding ordered items; a list with no groups is a flat list. File order is display order.
   - An item is a plain checkbox line with NO 📅 or 🛫 (so it is a checklist item, never a task; `meta-notes conventions`). The commands must never write either on an item line.
   - Optional source: one indented plain bullet under the item with `[[note link]]`, a line hint, and the source task's text copied exactly.
   - Item states: open, done, canceled (use the existing checkbox status markers).
2. **`meta-notes list` commands** (names are yours; keep the set small): create a list (empty); show a list (human text and `--json` with groups, items, states, sources, for the UI); list all lists; add/rename/reorder groups; add/edit/move/reorder items within and between groups, with an optional source task; check, uncheck, cancel an item. Checking an item that has a source closes the task through the same path as `task update --expect` (exact text match; on mismatch refuse with a clear error and leave both files untouched). Unchecking reopens the task if the list closed it. Set the current list: a link line in today's daily note (and a way to read the current list back).
3. **Agent instructions in the prime guide** (`meta-notes prime`), so every root's agent knows how to make and run a list: find candidate tasks, keep items very brief ("3 soups for work", not the task's wording), add a guessed or unclear item anyway with a trailing `?` and ask the human, group and order by the store's layout when the root has one (the notes root keeps layouts in `resource/locations/`), record the source on every item that comes from a task, set the list current, and at trip end mark every item done or canceled (tasks not got stay open).

## Acceptance

- Specs and tests for the format and every command, including: an item never becomes a task (`meta-notes tasks --status all --all` never lists list items), checking a sourced item closes exactly that task, an `--expect` mismatch refuses and changes nothing, file order round-trips.
- `meta-notes prime` shows the list guide.
- `just check` (or the repo's check) green once.

## Model

Sonnet: format design and parser/writer code.

## Out of scope (not yet, until a trip has been run with this)

Manual sorting from the UI, aisle numbers, prices, sharing, tap-to-talk (all "later" per the human). A separate master-list file (tasks are the master list). Block IDs on source tasks (rejected on mu-5tju: edits task lines).
