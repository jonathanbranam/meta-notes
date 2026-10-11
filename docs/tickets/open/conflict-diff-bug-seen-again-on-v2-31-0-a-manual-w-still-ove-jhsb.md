---
id: jhsb
title: "Conflict diff bug seen again on v2.31.0: a manual :w still overwrote a newer disk write"
kind: bug
opened: 2026-10-11
filed_by: external:orchestrator
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [7tfg]
tasks: []
---

## The ask

## The ask

From the human, by email 2026-10-11 8:40 AM ET (forwarded by the dalek orchestrator, m-0816), subject "Ticket for meta-notes project": "The following issue (see attachment) was found for the meta-notes project; currently on the NUC without mail configured; please forward to that project's aide or orchestrator."

Asked whether this was before the mn-7tfg fix, the human said, verbatim (via the bridle aide, m-0819, 2026-10-11 ~5:20 PM ET): "Meta notes plugin was latest at the time it was filed". The latest release at 8:40 AM ET was v2.31.0 (f17ad50, merged 2026-10-09 5:30 PM ET), which carries the mn-7tfg fix. The human's instruction, relayed: "file it and look into it."

## What we know

- The attached report is word for word the report already filed as mn-7tfg (closed 2026-10-09): the same sequence, and line numbers in `autoload/meta_notes/autosave.vim` (354-390, 405-414, 318-350) from before the fix. Read mn-7tfg (`bridle task show mn-7tfg`) for the full text.
- The mn-7tfg fix (9e37673): a BufWritePre guard on notes buffers refuses a manual :w with a diff when the disk changed since read or since the diff was shown; an open diff is refreshed, and the user is told when the disk changes again. Its own summary notes a known gap: "Vim's own overwrite prompt remains on a second :w." So after the guard refuses once, a second :w reaches Vim's W12 "write anyway?" prompt, and `y` still overwrites the newer disk write.

## Open questions

1. Did the human's Vim actually run v2.31.0 at the time (the Mac's plugin checkout pulled, Vim restarted or `:MetaNotesReload`)? `:MetaNotesVersion` shows it.
2. Did they see the meta-notes refusal and diff before Vim's prompt, or only Vim's prompt?

## Likely fix direction

Close the second-:w gap: a write of a notes buffer whose disk stamp moved since the last diff shown should never reach Vim's bare W12 prompt without a current diff (for example, handle FileChangedShell / the W12 path for notes buffers, or keep refusing until the user has seen the latest disk contents). Also check the sequence in the report (a second agent write while the diff is open, then :w) against v2.31.0 in a vader test.
