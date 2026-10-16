---
id: mn-wumx
title: "[at next reboot] start vesta's orchestrator by hand in vesta-home"
kind: chore
created: 2026-10-16
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## The ask

Until br-rnhp lands, `bridle up` at boot starts the orchestrator with no project. After a reboot, in the vesta-home window (orchestrator pane), run:

    bridle session orchestrator --project vesta-home

Tell it to read its newest handover (`bridle handover list --project vesta-home`, else `--project meta-notes`).

Also pending (not reboot-bound): the vesta-home mail bridge, `bridle mail install --project vesta-home` then `systemctl --user enable --now bridle-mail-vesta-home.service`, and the test emails (mn-m4bk was closed with the mail test deferred).

Close this when br-rnhp has landed on vesta.
