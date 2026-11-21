---
id: mn-hwse
title: "task update: --text with dates in it doubles the line's dates"
kind: fix
created: 2026-11-21
created_by: external:orchestrator
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## The ask

Reported by aide (notes), 2026-11-21: `meta-notes task update ... --text <description with dates>` added a second 📅 instead of replacing the first. Aide fixed the note by hand.

`_set_text` in `scripts/meta_notes/task_update.py` replaces only the words before the first date emoji and keeps the rest of the line, so a value that has its own 📅/⏳/🛫/⏰/🔁/✅ ends up with two. Fix: refuse a --text value that contains a date or marker emoji, with an error that names the flag to use instead (--due, --start, --time, --recur). Rejected: parsing the value's dates and merging them, which is more code and guesses at intent.

Dropped (2026-11-21): the report's other half, no ✅ date on a task done on its due day. Aide withdrew it: that's the meta-notes convention.

## Check

Unit test: --text with a date emoji raises TaskUpdateError and leaves the file unchanged. The project's usual test run is green.

Model: Haiku (small, mechanical).
