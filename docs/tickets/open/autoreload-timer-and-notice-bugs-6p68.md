---
id: 6p68
title: Autoreload's timer never starts and its reload notice never shows
opened: 2026-10-01
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [vim-autosave-and-autoreload-egvk]
---

# Autoreload's timer never starts and its reload notice never shows

Found by the orchestrator testing v2.8.0 in a real Vim 9.1 in tmux
(a stand-in fswatch fed events). The watcher reload, undo of a reload,
autosave and the conflict diff all worked. Two bugs:

## 1. The checktime timer never starts at startup

`g:meta_notes_checktime_interval = 1000` with `g:meta_notes_autoreload = 1`
and `g:meta_notes_watch = 0`: `:MetaNotesAutoStatus` shows
`timer: 1000 ms (not running)`, `timer_info()` is `[]`, and an outside
edit is never picked up. `s:StartTimer()` is only called from
`meta_notes#autosave#Refresh()` (runtime toggles), never from
`meta_notes#autosave#Attach()`. Fix: start it (idempotently) from Attach
when autoreload is on, as Attach does for the watcher. The same applies
when the watcher is on and the interval is set (the human's work setup:
watcher plus 5000 ms).

## 2. The reload notice never appears

After a watcher-triggered reload of an unmodified buffer, no
`meta-notes: reloaded ... (u to undo)` message, not even in `:messages`.
With 'autoread' set, Vim doesn't run FileChangedShell for an unmodified
buffer (`:help FileChangedShell`: "It is not used when 'autoread' is set
and the buffer was not changed"), so `v:fcs_reason` isn't set, and
`OnChangedShellPost()` requires `v:fcs_reason ==# 'changed'`. Fix: show
the notice from FileChangedShellPost without depending on v:fcs_reason
(or compare the stored stamp). The human specifically wants this message:
"As long as something flashes in my message bar that the file has
changed".

## Done means

Both fixed, with vader tests that would have caught them (timer running
after a notes buffer is opened with the settings on; the notice in
`:messages` after a reload with autoread on). PATCH bump.
