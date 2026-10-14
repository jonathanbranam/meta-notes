---
id: mn-mdtd
title: "After the notes aide cut-over: cancel sc-bj9j (2 AM reflect) and recreate it pointed at the notes aide"
kind: chore
created: 2026-10-14
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: [nt-3enk]
---

## The ask

From the human, 2026-10-14 ~12:20 PM ET, to meta-notes' aide: "yes, remind me to cancel and recreate that scheduled message here pointed at the aide".

The daily 2 AM reflect, schedule sc-bj9j, is on the notes daemon. It was set by external:aide@dalek and targets external:advisor. Once the notes advisor becomes notes' aide (nt-3enk), it needs to target external:aide. Only the human, or whoever set it, can change it. An agent can schedule only to itself.

When: after the cut-over, once `bridle session aide` is running in notes.

How (as the human, on vesta):

    bridle schedule list --project notes          # find sc-bj9j: note its cron and message text
    bridle schedule rm sc-bj9j --project notes
    bridle schedule add --project notes --to external:aide --cron '<same cron, e.g. 0 2 * * *>' --message '<same text>'

Then check `bridle schedule list --project notes` shows it targeting external:aide. Finish with `bridle task done <this id>`.
