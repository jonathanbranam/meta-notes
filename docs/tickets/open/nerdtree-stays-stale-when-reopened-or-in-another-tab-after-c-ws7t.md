---
id: ws7t
title: NERDTree stays stale when reopened or in another tab after changes
kind: bug
opened: 2026-10-04
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [rb4z]
tasks: []
---

## The ask

Found reviewing mn-rb4z (v2.20.0, 320d54d), not yet seen live.

`meta_notes#autosave#NerdQueue` returns before doing anything when no
NERDTree window is visible in the current tab, so `s:nerd_gen` only moves
when a visible tree drains. `s:NerdEnter` skips its refresh when the
root's watcher runs and `b:meta_notes_nerd_gen == s:nerd_gen`. So:

- Close the tree (`:NERDTreeToggle`), let an agent add a folder, reopen
  the tree: same NERDTree buffer, same generation, no refresh. Stale.
- A tree in another tab while the current tab has none: the event is
  dropped, the generation doesn't move, entering that tab's tree skips
  its refresh. Stale.

Fix: when the refresh is on, every watcher event that isn't a loaded
buffer bumps the generation (or marks it dirty) even when no tree is
visible, so the next `NerdEnter` refreshes. Keep the cheap path: no
queueing or timer when no tree is visible. Vader tests with the stub for
both cases (hidden tree, tree in another tab). Patch version.
