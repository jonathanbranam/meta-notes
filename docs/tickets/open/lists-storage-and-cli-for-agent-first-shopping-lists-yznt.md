---
id: mn-yznt
title: "lists: storage and CLI for agent-first shopping lists"
kind: question
created: 2026-11-07
created_by: external:orchestrator
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: [mu-5tju]
---

## The ask

From the human, via aide (meta-notes-ui), 2026-11-07 (m-0179; all their words verbatim on meta-notes-ui epic mu-5tju): build shopping lists agent-first. "talk to the aide at Notes and say, 'I'm going to Walmart. Make me a list for this trip to Walmart.' That agent needs to have instructions on how to do this ... Those instructions on how to make a list should come from the meta-notes plugin ... The meta-notes CLI should have commands for creating and managing these lists." Lists are plain text in the notes repo; the storage format is "probably one of the main things we're going to have to work out". The UI (bottom tab bar, Lists tab) comes later, in meta-notes-ui.

Requirements sources: mu-5tju (master list, multi-store items, groups by store section, check off to a Got section at the bottom, uncheck, "current list" recorded in the daily note); the human's draft `area/meta-notes/UI Shopping List.md` in the notes repo (Must: checking an item closes its real task; move an item between stores; add unlisted items already checked); store layouts in `resource/locations/Muncie.md`; the 2026-10-31 trip (a `## Shopping` section in the daily note, `###` per store, section lines like "Produce (front):").

## Decision needed: where a list lives (storage not approved)

A. **Tags only, no list files** (mu-5tju's October proposal). Items stay ordinary tasks wherever they are, tagged per store (`#walmart #lowes`); a trip list is a query (store tag + due today). No new storage. But order, store sections and "current list" have nowhere natural to live, and the agent can't simply write a list.

B. **One file per list (recommended).** A `lists/` folder in the root: a standing `Shopping.md` master list (things to get, each tagged with the stores that carry it, e.g. `#walmart #lowes`) and one file per trip (`lists/2026-11-07 Walmart.md`) with `## <section>` headings in store walking order and normal `- [ ]` task lines. "Make me a Walmart list" moves the picked items from the master into the trip file (an item lives in one place; anything not got moves back). An item that is really a task elsewhere is a line that links to it, and checking it closes the source task. The daily note records the current list with one link line. Checked items stay as `- [x]` lines; the Got section is how the UI and `list show` display them.

C. **A section of the daily note** (what 2026-10-31 did). Already works and is "current" for free, but clutters the day's note, can't span days, and the master list still needs a home.

Recommendation: B. Plain markdown the human can read and edit in Vim or Obsidian, it matches the 10-31 trip's shape, and it gives the CLI and the later UI one simple file to read and write.

## Once a storage option is approved (plan, not yet scheduled)

1. meta-notes: storage spec plus `meta-notes list` commands (new, show, add, pick from master, check/uncheck, move between stores/lists, set current) and a prime guide section telling every root's agent how to make and run a list. Sonnet (design and parser code).
2. notes root: seed `lists/Shopping.md` from the scattered store-tagged tasks (agent work in the notes root, not a code ticket).
3. meta-notes-ui: the Lists tab (mu-5tju), later.

Deferred, not yet: aisle numbers, who asked, price capture, not-found state, sharing (the draft's Should/Could), until the agent-first version has been used on a trip.
