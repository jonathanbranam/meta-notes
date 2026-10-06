+++
id = "mn-tmjz"
title = "[at restart] Run the bridle gateway on the NUC so it and dalek's gateway can reach each other"
kind = "feature"
state = "claimed"
created_at = "2026-10-06T22:42:03.164Z"
updated_at = "2026-10-06T22:42:03.439416805Z"
created_by = "external:orchestrator"
watchers = [
    "external:orchestrator",
    "human",
]
priority_at = "2026-10-06T22:42:03.393694554Z"
+++

The human, 2026-10-06: they haven't followed up on open tickets yet, partly because they need the bridle gateway running on the NUC so the main gateway (dalek's) can reach it and vice versa, which makes reviewing tickets from the phone much easier.

The NUC has no [gateway] table in ~/.bridle/config.toml yet. Steps:
1. echo -n '<password>' | bridle gateway hash-password  -> put the hash in [gateway] password_hash in ~/.bridle/config.toml (plus bind address and public_url).
2. bridle gateway install  -> prints the systemd user unit commands; run them (or bridle gateway --detach to try it first).
3. Once public_url is set, bridle link starts printing links in agents' messages.

Then the open items for review: tickets cwmr, v4ar, the ## Tasks line in the personal daily template, and the older ones in the orchestrator handover (zta7, ma6v, scpr, hd2x, gr8c, nt-22fb).

## Thread

### note · external:orchestrator · 2026-10-06T22:42:03.393Z
created for the human, priority normal

### note · external:orchestrator · 2026-10-06T22:42:03.439Z
To-do for you (normal priority): [at restart] Run the bridle gateway on the NUC so it and dalek's gateway can reach each other. Finish it with `bridle task done mn-tmjz`.
