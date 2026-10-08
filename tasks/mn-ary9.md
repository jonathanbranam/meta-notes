+++
id = "mn-ary9"
title = "NUC: add bridle-ui to [projects] (and optionally an aide token) so the aide can reach it on dalek"
kind = "chore"
state = "claimed"
created_at = "2026-10-08T11:51:06.096Z"
updated_at = "2026-10-08T11:51:06.444345196Z"
created_by = "external:aide"
watchers = [
    "external:aide",
    "human",
]
priority_at = "2026-10-08T11:51:06.387467651Z"
+++

The human, 2026-10-08: "Can you create a task for me and a to-do to remind me that that token needs to be created?"

Context: the meta-notes aide couldn't message bridle-ui's aide on dalek ('no daemon known for project bridle-ui'), because ~/.bridle/config.toml on the NUC has no [projects] entry for bridle-ui. The message about viewing and commenting on documents in bridle-ui went via bridle's aide instead (o-0032).

To do:
1. On dalek, get bridle-ui's daemon port: bridle daemons.
2. On the NUC, add under [projects] in ~/.bridle/config.toml:
   bridle-ui = { machine = "dalek", port = <port> }
3. The [peer] token for bridle-ui is already in ~/.bridle/credentials.toml on the NUC, which is enough for sending messages. Optional, so the aide can also read bridle-ui's tasks: on dalek, bridle token create aide --project bridle-ui, and put it under [aide.dalek] as bridle-ui = "..." on the NUC.
4. Check: from the NUC, bridle --project bridle-ui status.

## Thread

### note · external:aide · 2026-10-08T11:51:06.387Z
created for the human, priority normal

### note · external:aide · 2026-10-08T11:51:06.444Z
To-do for you (normal priority): NUC: add bridle-ui to [projects] (and optionally an aide token) so the aide can reach it on dalek. Finish it with `bridle task done mn-ary9`.
