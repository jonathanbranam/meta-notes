---
id: sur9
title: task update finds the line by --expect; the line number is optional
kind: feature
opened: 2026-10-06
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: [mn-2dyd]
---

## The ask


## The ask

The human, 2026-10-05 about 11:26 PM (relayed by the notes advisor, notes
m-0093). `meta-notes task update FILE:LINE --expect <line>` makes agents grep
for the line number first; that night a grep on `$40` failed (regex `$`) and
broke a chain of commands. The human: "let's try to simplify that so you
don't have to write those big, scary grep statements."

## Decision (the human's design)

`meta-notes task update <file> --expect '<full first line>' [changes]`, with
no line number, finds the line whose text equals `--expect` (the same
comparison as today):

- no match: fail;
- one match: update it;
- more than one: fail and list the matching line numbers, so the caller
  runs it again with `FILE:LINE`.

`--expect` stays as the safety catch. Their words: "The header line text
should still match. That's a safety catch. ... If it matches twice, it'll
fail and say it matched 3 times on these line numbers, and then you can call
it again and specify the line number." `FILE:LINE` keeps working as now.

The advisor suggested the same for the other `FILE:LINE` commands (ceremony
markers already go through `task update`). Not yet: `task update` is what
the agents trip on; the others follow if they turn out to need it.
