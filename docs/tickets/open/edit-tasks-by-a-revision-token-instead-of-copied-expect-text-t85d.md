---
id: t85d
title: Edit tasks by a revision token instead of copied --expect text
kind: question
opened: 2026-10-08
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [zk5p]
tasks: []
---

## The ask

For discussion, not approved. From the human, via the notes advisor
(2026-10-08), after the expect-guard incident (see the guard hook ticket):
"--expect is working against the natural way agents write these", and
"this wouldn't happen as easily in a database". They are considering
blocking agents' read access to notes so every edit goes through the CLI,
but that is a lot of work.

The advisor's suggestion: optimistic concurrency like an ETag. `tasks
--json` (and `task show`) returns a per-task revision token (a hash of the
line and the file's revision); `task update` takes `--rev <token>` instead
of copied text. A token can't be produced by sed at write time, and a stale
one is refused. Possibly stable task ids too.

Questions for the human:
1. Revision tokens alongside `--expect`, or replacing it?
2. Stable task ids (written into the line) now, or later?
3. Is blocking read access still on the table, or does a token make it
   unnecessary?
