+++
id = "mn-hsxc"
title = "Snapshot skip hides real tasks under Tasks Due Today (rg3v)"
kind = "bug"
state = "planned"
created_at = "2026-10-05T23:20:11.721Z"
updated_at = "2026-10-05T23:20:16.349122609Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
size = "S"
+++

Ticket: docs/tickets/open/snapshot-skip-hides-real-tasks-written-under-tasks-due-today-rg3v.md (read it; it has the evidence and the snapshot format).

## Goal
Fix the cru4 regression: under a daily note's `## Tasks Due Today` / `## Overdue Tasks`, skip only the snapshot copies (the subtree of a top-level `- [[link]]` bullet), not top-level hand-written `- [ ] ...` tasks and their subtrees.

## Files
scripts/tasks.py (`_snapshot_lines`), test/unit/test_tasks.py, design/specs/task-query.md (update the cru4 requirement's statement/scenario; `bridle spec id` for any new heading), doc/meta-notes.txt and scripts/meta_notes/conventions.md where they describe the skip. PATCH bump (2.25.1).

## Check
Tests: a snapshot section with both a `- [[link]]` group of copies (skipped, including deeper nesting from a copied-forward snapshot) and a top-level task with an indented note (found). Then on the notes root (read-only): `cd /srv/shared/work/notes-work/notes && <worktree>/bin/meta-notes tasks --agenda` lists "Order school photos" and "Print Zeal's orchestra music" under 2026-10-06. Normal project check green.

## Out of scope
Template changes; editing any notes. Model: Sonnet. Size: s.
