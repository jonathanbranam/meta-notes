+++
id = "mn-v2f5"
title = "Add the meta-notes-ui bridle project on the NUC (config, daemon, token)"
kind = "chore"
state = "claimed"
created_at = "2026-10-05T02:10:58.259Z"
updated_at = "2026-10-05T02:10:58.672524151Z"
created_by = "external:orchestrator"
watchers = [
    "external:orchestrator",
    "human",
]
+++

The repo is created and scaffolded: github.com/jonathanbranam/meta-notes-ui, cloned at /srv/shared/work/meta-notes-ui-work/meta-notes-ui (commit 4e62e88: .bridle/config.toml with the typescript pack, roles, rules writes-through-the-cli, light-on-resources, works-without-bridle, access, versioning; README; v1 tickets 83ya, wfbc, eqqv, 35z9). Review it on GitHub if you like.

1. Register it in ~/.bridle/config.toml on the NUC under [projects] (and dalek's, as before):
   meta-notes-ui = { machine = "nuc", port = 7405 }

2. Start its daemon. With systemd (br-jkas) set up:
   cd /srv/shared/work/meta-notes-ui-work/meta-notes-ui && bridle daemon systemd install && systemctl --user daemon-reload && systemctl --user enable --now bridle-meta-notes-ui
   Otherwise, in a new tmux window: cd /srv/shared/work/meta-notes-ui-work/meta-notes-ui && bridle serve

3. Create the orchestrator's token (only you can):
   cd /srv/shared/work/meta-notes-ui-work/meta-notes-ui && bridle token create orchestrator --project meta-notes-ui

Then tell the orchestrator. It verifies, files the v1.1 task and starts a manager there. Meanwhile meta-notes builds note write (mn-5qab) and meta-notes ui (mn-g8wz). Finish with bridle task done <this id>.

## Thread

### note · external:orchestrator · 2026-10-05T02:10:58.626Z
created for the human, priority normal

### note · external:orchestrator · 2026-10-05T02:10:58.672Z
To-do for you (normal priority): Add the meta-notes-ui bridle project on the NUC (config, daemon, token). Finish it with `bridle task done mn-v2f5`.
