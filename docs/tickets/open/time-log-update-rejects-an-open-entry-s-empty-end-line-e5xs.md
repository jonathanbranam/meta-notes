---
id: e5xs
title: time-log update rejects an open entry's empty end line
kind: bug
opened: 2026-10-08
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: []
---

## The ask

## The bug

`meta-notes time-log update` refuses replacement text whose last entry has an empty `* end:` line:

    Error: '- Next2' has an invalid end: ''

But the note itself holds that line (the daily template's placeholder, or a hand-written open entry), so `--expect` must include it while `--text` can't. Reproduced 2026-10-08 on a dated daily note:

    - Next
      * start: 10:00
      * end:

`time-log update --expect $'- Next\n  * start: 10:00\n  * end:' --text $'- Next2\n  * start: 10:00\n  * end:'` fails with the error above.

Found by the meta-notes-ui worker on mu-xng2 (Time Log edits from the UI); the UI works around it by dropping an empty end line from the replacement (`dropEmptyEnd`), which silently rewrites the entry's shape.

## Fix

In `scripts/meta_notes/time_log.py` `_check_new`, treat an empty `end:` like a missing one: an open entry, allowed only for the log's last entry (same rule as today). Keep the empty line as written. Add a test in `test/unit/test_time_log.py`.

Small; Haiku or Sonnet.
