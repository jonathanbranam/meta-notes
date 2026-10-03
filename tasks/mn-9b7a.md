+++
id = "mn-9b7a"
title = "Vim: GitGutter off for the session in a notes root (ticket tzac)"
kind = "feature"
state = "open"
created_at = "2026-10-03T17:53:50.909Z"
updated_at = "2026-10-03T17:53:50.909Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
+++

---
id: tzac
title: "Vim: GitGutter off for the whole session when Vim starts in a notes root"
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [bawv]
tasks: []
---

## The ask


# Vim: GitGutter off for the session when Vim starts in a notes root

## The ask

Correction to bawv (v2.14.0, per-buffer disable), from the human
2026-10-03 (relayed by the notes advisor, m-0275): "when I'm running Vim,
I'm only editing my notes or I'm programming somewhere else. So I don't
want to turn it off per file... all that I really need to happen is that
when Vim opens a meta notes, a repo that has meta notes installed in it,
that Git Gutter is turned off."

## Shape

At startup (VimEnter), if Vim's working directory is inside a notes root
(a `.meta-notes` found walking up, the same root search the plugin
already uses), run `:GitGutterDisable` once, globally, for the session.
Guarded by `exists(':GitGutterDisable')`, so nothing happens without
GitGutter. Replace bawv's per-buffer disable with this; keep the
`g:meta_notes_disable_gitgutter` option (default on). Update `:help`, the
spec and tests. Patch or minor per the versioning rule.
