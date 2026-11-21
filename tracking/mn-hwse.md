+++
id = "mn-hwse"
title = "task update: --text with dates doubles them; the no-done-date-when-due-today rule is undocumented"
kind = "fix"
state = "open"
created_at = "2026-11-21T18:47:01.666Z"
updated_at = "2026-11-21T18:49:31.447759285Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
ticket = "hwse"
+++

## The ask

Reported by aide (notes), 2026-11-21: `meta-notes task update ... --text <description with dates>` added a second 📅 instead of replacing the first. Aide fixed the note by hand.

`_set_text` in `scripts/meta_notes/task_update.py` replaces only the words before the first date emoji and keeps the rest of the line, so a value that has its own 📅/⏳/🛫/⏰/🔁/✅ ends up with two. Fix: refuse a --text value that contains a date or marker emoji, with an error that names the flag to use instead (--due, --start, --time, --recur). Rejected: parsing the value's dates and merging them, which is more code and guesses at intent.

Dropped (2026-11-21): the report's other half, no ✅ date on a task done on its due day. Aide withdrew it: that's the meta-notes convention, documented there.

## Check

Unit test: --text with a date emoji raises TaskUpdateError and leaves the file unchanged. The project's usual test run is green.

Model: Haiku (small, mechanical).

## Thread

### note · external:orchestrator · 2026-11-21T18:47:07.252Z
readied by external:orchestrator

### note · agent:manager · 2026-11-21T18:47:11.762Z
Manager: open, not planned, not in bridle queue. Please plan and queue it; I will spawn a worker once startable.
