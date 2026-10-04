---
id: light-on-resources
severity: must
roles: [manager, worker]
---
meta-notes runs inside the human's editor all day, so it must not tax the
computer. Anything that runs in the background (in Vim, the CLI or a skill)
is careful with CPU and memory, and can be turned off.

- Prefer events to polling: reuse the existing watcher job
  (`autoload/meta_notes/autosave.vim`) and Vim autocommands before adding
  a timer or a new process. A timer is opt-in, never on by default.
- Do work only when it's needed: when something changed, only for what
  changed, and only when its result is visible (a loaded buffer, an open
  window). Debounce bursts (a `git pull`, an agent writing many notes).
- Do nothing in sessions that don't use the feature (no notes root, the
  other plugin not loaded).
- Every background feature has an opt-out setting (`g:meta_notes_...`),
  documented in `doc/meta-notes.txt`.

Why: the human, 2026-10-04: "the changes to vim should not use excess
compute or memory; similar to the live file updates; find careful
solutions that don't tax a computer excessively; provide an opt-out as
well."
