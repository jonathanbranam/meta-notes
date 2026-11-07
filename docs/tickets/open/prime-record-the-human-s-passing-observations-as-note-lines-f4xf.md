---
id: mn-f4xf
title: "prime: record the human's passing observations as '* note:' lines under the current Time Log entry"
kind: feature
created: 2026-11-07
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## The ask

From the notes aide (external:aide on the notes project, the human's personal root), message m-0257, 2026-11-07 ~10:55 AM ET, "at Jonathan's request". Relayed second-hand: the human has not said it to the meta-notes aide directly. Their request, verbatim:

> Please add this to the global aide instructions (the meta-notes guide / aide role, not just one root's CLAUDE.md), so it applies in every root, including his work root and its workplace agent:
>
> When the human mentions small observations as they go (who's awake or home, the dogs, the weather, what they ate or drank, small things they noticed or checked), record each one as a short `* note:` line under the current time-log entry in the daily note, with the time when it helps. That's why they mention them: they like having a log of what happens, and it gives the aide context. It isn't small talk, so don't just acknowledge it in chat.
>
> Example (personal root, Sat 11/7):
> - laundry: clean laundry upstairs; start a load
>   * start: 10:47
>   * note: Washer started; changed for the bike; made a Propel drink for the ride.
>   * note: 10:51: Esther not awake, as far as I know; Tiffany still not home.
>
> I've also put it in the personal root's CLAUDE.md for now (he's fine with it in both). Please confirm when the instructions are updated.

Notes from aide:
- "The meta-notes guide" is what `meta-notes prime` prints (scripts/meta_notes/prime.md), which every root's agent loads at session start. conventions.md has no `* note:` time-log line today; the Time Log section may need the line format too, so time-log append/update and the skills agree.
- Applies to work roots as well, per the request ("including his work root and its workplace agent").
