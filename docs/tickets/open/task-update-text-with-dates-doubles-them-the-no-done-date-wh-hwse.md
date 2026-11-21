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

Reported by aide (notes), 2026-11-21: `meta-notes task update area/home/Supplies.md:194 --expect ... --status x` marked the task done with no ✅ date, and then `--text <description with dates>` added a second 📅 instead of replacing the first. Aide fixed the note by hand.

Two things, both in `scripts/meta_notes/task_update.py`:

1. **--text doubles dates.** `_set_text` replaces only the words before the first date emoji and keeps the rest of the line, so a value that has its own 📅/⏳/🛫/⏰/🔁/✅ ends up with two. Fix: refuse a --text value that contains a date or marker emoji, with an error that names the flag to use instead (--due, --start, --time, --recur). Rejected: parsing the value's dates and merging them, which is more code and guesses at intent.
2. **No ✅ date when the task is due today.** `_set_status` deliberately adds no ✅ date when the due date is today (line ~302), but `--help` for --status/--no-completed and the docs only mention --no-completed. Fix: say so in the --no-completed help text and wherever the task update docs describe the ✅ date. No behaviour change.

## Check

Unit tests: --text with a date emoji raises TaskUpdateError and leaves the file unchanged; the help text mentions the due-today rule. `just check` (or the project's usual test run) green.

Model: Haiku (small, mechanical).
