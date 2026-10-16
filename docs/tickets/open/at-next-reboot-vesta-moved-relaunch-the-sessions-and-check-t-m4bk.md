---
id: mn-m4bk
title: "[at next reboot] vesta moved: relaunch the sessions and check the system"
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

The human is moving vesta (2026-10-15, ~7:45 PM ET): a shutdown and a restart at a new spot.

Starts by itself at boot (lingering is on): the four bridle daemons, bridle-gateway, the four mail bridges, meta-notes-ui and its update path, tailscaled with `serve` (https://vesta.tailbc91f5.ts.net), and tmux. tmux-continuum restores the windows and panes as shells.

Doesn't come back by itself: the Claude sessions. After boot:
1. `bridle status --project <p>` for meta-notes, notes, meta-notes-ui and dotfiles-local: no incidents, and tickets present (`bridle ticket list --project <p>`). If a daemon comes back empty, as on Oct 14: `bridle daemon rebuild --project <p>`. If tokens are refused: `bridle token pair`.
2. The orchestrator, pane 0:1.3 (meta-notes-br): check it came back. If not, start it there.
3. The aides: `bridle session aide` in 0:1.4 (meta-notes), 0:2.3 (notes) and 0:3.3 (dotfiles-local). Tell each to read its latest handover (`bridle handover list --project <p>`).
4. Check that the phone loads the UI and that mail arrives (send a test email). The mail bridges' logs are in ~/.bridle/mail-<project>.log (br-mfcj: a bridge can hang silently).
5. If the Wi-Fi changed, vesta has to join it first (keyboard and screen, or Ethernet).

Finish with `bridle task done <this id>`.
