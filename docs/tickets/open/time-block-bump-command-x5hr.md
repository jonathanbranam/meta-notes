---
id: x5hr
title: Does the Time Block need a bump command to shift rows by N minutes?
kind: question
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [kkrj]
tasks: []
---

# Does the Time Block need a bump command?

Open question, the human's to decide later; don't build yet. Raised
2026-10-03 (relayed by the notes advisor), after reordering a morning by
hand. Their examples: "bump all meetings after this", "bump the time block
after this by 30 minutes", "bump all meetings from 2 p.m. to 3 p.m. by 30
minutes".

Their concerns:

- Shifting runs into the end of the day: what happens to rows pushed past
  the last slot?
- Flexible work should usually flow around fixed meetings, not move with
  them. Meetings are always marked `mtg:` (lowercase) in the Time Block, so flowing
  around them is possible, "although a little bit of extra work. Maybe it's
  unnecessary with what agents can do."
- Task reminder times (⏰) don't move when blocks move.

With `time-block replace` (kkrj) an agent can rewrite the rows in one safe
call, which may make a bump command unnecessary. Revisit once the human has
used replace for a while.
