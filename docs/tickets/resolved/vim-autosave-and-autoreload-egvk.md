---
id: egvk
title: Vim autosave and autoreload for notes buffers, safe against agent edits
opened: 2026-10-01
repos: [meta-notes]
changes: []
specs: [notes-autosave]
needs: []
see: [time-log-append-and-update-commands-v63j, time-block-update-command-gmqp]
---

# Vim autosave and autoreload for notes buffers

## Why

The human keeps Vim open on the notes root all day while agents edit the
same notes (the daily note most of all) through the CLI. Today an agent's
change shows up only when Vim next checks timestamps, and the human's
unsaved edits sit in the buffer where the next agent write races them.
The CLI guards cover the agent side; this covers the Vim side: save the
human's edits quickly, pick up agents' edits quickly, and never overwrite
either.

The human's setup: terminal Vim 9.1, always inside tmux, in Ghostty or
iTerm2, on macOS (work laptop fast, personal laptop already loaded by
bridle). Vanilla Vim only; no Neovim for now.

## What to build (plugin, opt-in, notes-root buffers only)

Applies only to buffers whose file is under a notes root (the nearest
`.meta-notes`, as the CLI finds it). Everything is off by default; the
human turns it on in `.vimrc`.

1. **Autoreload**: `autoread` set buffer-locally on notes buffers.
2. **Noticing changes**, any of these, each configurable:
   - **FocusGained**: `:checktime` when Vim regains focus (free). Document
     that tmux needs `set -g focus-events on`.
   - **File watcher job** (preferred; no polling): a Vim job runs
     `fswatch` (macOS) or `inotifywait` (Linux) on the notes root,
     excluding `.git/`, `.venv/` and `.meta-notes-cache/`. Its callback runs
     `:checktime` for the changed file's buffer, if loaded. One job per
     notes root, started with the first notes buffer, stopped on
     VimLeave. If no watcher binary is found, say so once and fall back to
     the timer.
   - **Timer**: `:checktime` on loaded notes buffers every N ms. Off when
     N is 0.
   No check reloads while in insert mode; the next check after leaving it
   does.
3. **Autosave**: on `TextChanged` and `InsertLeave`, after a debounce
   (ms, configurable), run `:checktime` on the buffer first, then `:update`
   only if the file on disk hasn't changed since Vim read it. Never force a
   write and never trigger Vim's "changed since reading it" prompt.
4. **Conflict** (buffer has unsaved edits and the file changed on disk),
   via `FileChangedShell`: keep the buffer, don't reload, pause autosave
   for that buffer, and show a clear message. With the diff option on
   (default), open a diff of the buffer against the file on disk (the
   `:DiffOrig` idea, a scratch split, closes cleanly). The human resolves
   and `:w`s; autosave resumes after a successful write. With the diff
   option off, only the message.
5. **Reload notice**, via `FileChangedShellPost`: a short message such as
   `meta-notes: reloaded 2026-10-01 Thu.md (changed on disk; u to undo)`.
   Reloads stay undoable (`'undoreload'`, Vim's default 10000 lines; don't
   change it, document it).

## Settings (names are a suggestion; keep them consistent)

| Variable | Default | Meaning |
|---|---|---|
| `g:meta_notes_autosave` | 0 | Autosave notes buffers |
| `g:meta_notes_autosave_delay` | 1000 | Debounce, ms |
| `g:meta_notes_autoreload` | 0 | autoread and change checks on notes buffers |
| `g:meta_notes_watch` | 1 | Use the file watcher job when available |
| `g:meta_notes_checktime_interval` | 0 | Timer, ms; 0 = off. Used as the fallback when the watcher isn't available, if set |
| `g:meta_notes_conflict_diff` | 1 | Open a diff on a conflict |

The human wants to tune these per machine: e.g. watcher plus 5000 ms
timer at work, watcher only or nothing on the personal laptop. Also a
command to toggle autosave and autoreload at runtime, and one to show the
current state (which mechanisms are active, the watcher binary, the
interval).

## Documentation

Full `:help` coverage in `doc/meta-notes.txt`, a new section (e.g.
`*meta-notes-autosave*`): what each setting does, the recommended
`.vimrc` for a fast and a slow machine, tmux `focus-events`, installing
`fswatch` (`brew install fswatch`), the conflict flow, undoing a reload.
Written so the human's agent at work can read `:help` and configure it.
README gets a short pointer.

## Not in scope

- Neovim.
- The CLI signalling Vim directly (needs `+clientserver`, usually absent
  in terminal Vim on macOS). The file watcher catches every writer instead.

## Done means

The settings above work and are documented; vader tests cover what can be
tested headless (scoping to notes buffers, autosave skipping when the file
changed on disk, the conflict handler keeping the buffer, settings off by
default). MINOR version bump. The human will try it in practice and tune.
