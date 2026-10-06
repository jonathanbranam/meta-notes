+++
id = "mn-mfgq"
title = "[at restart] NUC: no external:aide on the daemons, and no peer token for bridle"
kind = "bug"
state = "integrated"
created_at = "2026-10-06T22:42:51.948Z"
updated_at = "2026-10-06T23:05:02.390450514Z"
created_by = "external:orchestrator"
watchers = [
    "external:orchestrator",
    "human",
]
priority_at = "2026-10-06T22:42:52.253832499Z"
+++

The human, 2026-10-06: 'Send me an issue about that as well, and then you can just send that directly to the orchestrator.'

Issue (for bridle; for its orchestrator on dalek to file as a bridle ticket):
On the NUC, the meta-notes daemon has no external:aide principal. 'bridle send external:aide ...' fails with 'not_found: no such recipient: external:aide'. The orchestrator role says it reaches the human only through aide, so on the NUC it has no route to the human except the live session. Expected: every daemon an orchestrator runs on has an aide (or a defined fallback route to the human), and orchestrator priming says what to do when aide is missing. Related: the NUC has no bridle gateway yet (mn-tmjz).

Why it couldn't be sent: 'bridle send --project bridle external:orchestrator ...' from the NUC fails with: 'bad_request: no peer token for bridle: its human runs bridle token create --peer nuc there and pastes the token under [peer] in ~/.bridle/credentials.toml'.

To do:
1. On dalek: bridle token create --peer nuc (in the bridle project). Paste the token under [peer] as bridle = "..." in ~/.bridle/credentials.toml on the NUC.
2. Tell the NUC orchestrator; it resends the issue above to dalek's orchestrator. (dalek may also need the messaging upgrade the human mentioned.)
3. Optionally give the NUC daemons an aide.

## Thread

### note · external:orchestrator · 2026-10-06T22:42:52.253Z
created for the human, priority normal

### note · external:orchestrator · 2026-10-06T22:42:52.299Z
To-do for you (normal priority): [at restart] NUC: no external:aide on the daemons, and no peer token for bridle. Finish it with `bridle task done mn-mfgq`.

### note · external:orchestrator · 2026-10-06T22:43:21.038Z
Add to the issue for bridle (the human, 2026-10-06): 'nobody told me that I needed peer tokens across machines too ... I just asked how to set up peer tokens, and nobody mentioned that.' The peer-token setup guidance (docs, and what agents say when asked) should say that a project on another machine (e.g. bridle on dalek) needs its own peer token, created there with 'bridle token create --peer <machine>'.

### note · external:orchestrator · 2026-10-06T22:51:40.895Z
Sent to bridle's orchestrator on dalek after the human added the bridle peer token: queued as o-0005 (2026-10-06). Both issues: no aide on the NUC, and the peer-token guidance gap.

### note · external:aide · 2026-10-06T23:05:02.390Z
done
