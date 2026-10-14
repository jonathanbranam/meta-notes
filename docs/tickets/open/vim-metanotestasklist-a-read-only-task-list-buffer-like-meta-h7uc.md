---
id: mn-h7uc
title: "Vim: MetaNotesTaskList, a read-only task list buffer like MetaNotesTimeReport"
kind: feature
created: 2026-10-14
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## The ask

From the human, by email (2026-10-14 ~4:22 PM ET, subject "Feature request for meta-notes"), relayed by bridle's aide (m-0018), verbatim: "Feature request for meta-notes - read-only task view. Please send this to the aide at meta-notes for implementation."

The attached spec, in full:

## project/meta-notes/Add a vim task list buffer to meta-notes

For the meta-notes plugin maintainer.

### Problem

Task listing today is CLI-only (`meta-notes tasks --agenda`, etc.), run
from a shell. The plugin already has a precedent for showing a CLI
report inside a scratch vim buffer: `MetaNotesTimeReport`
(`autoload/meta_notes/time_tracking.vim`,
`meta_notes#time_tracking#ShowReport()`) runs `meta-notes time --date
<date>` via `meta_notes#cli#Run()` and renders the output into a
readonly, `buftype=nofile`, `filetype=markdown` buffer named `Time
Report`, reusing the existing buffer/window if one is already open.
There's no equivalent for the task list — pulling it up means dropping
to a terminal.

An older personal vimrc (`~/work/local-dotfiles/vimrc.local:226`) had a
`TaskList_Open()` function doing roughly this against a predecessor
`tasks.py` script: open/reuse a `__Task_List__.md` scratch buffer,
clear it, and `:!python3 tasks.py` the output into it, with a (partially
working) `conceal` on the trailing ` file: ...` reference so the task
text reads cleanly while the file link stays available for jumping.

### Requested feature

A `MetaNotesTaskList` command, modeled directly on
`MetaNotesTimeReport`:

1. Runs `meta-notes tasks --agenda --json` (or similar) through
   `meta_notes#cli#Run()`.
2. Renders the result into a reused readonly scratch buffer (e.g. named
   `Task List`), `buftype=nofile`, `filetype=markdown`, same
   create-or-reuse-buffer/window logic as `ShowReport`.
3. Add a `<localleader>` mapping for it alongside the other
   buffer-local markdown mappings in `plugin/meta_notes.vim` (e.g.
   `<localleader>t`) — buffer-local, defined in the plugin (per
   `.bridle/rules/key-mappings.md`), not the user's vimrc.
4. Nice-to-have, not required for a first version: a buffer-local
   mapping in the Task List buffer to jump to a task's source file/line
   (each task's `file`/`line` from the JSON is already available —
   `tasks --json`'s output already has what `TaskList_Open`'s
   `conceal`-and-jump hack was working around by scraping a trailing
   ` file: ...` string).

### Why this belongs in the plugin, not this repo

`ShowReport`'s buffer-rendering pattern already lives in the plugin and
is the natural place to add a second report of the same shape; a
notes-repo-local script would duplicate that buffer-management code
instead of reusing it.

### Related

- [[project/meta-notes/Port tasks and time_log features into meta-notes]]

## Brief (orchestrator, 2026-10-14)

Decisions: mapping `<localleader>t` (free; buffer-local markdown map in
`plugin/meta_notes.vim`'s FileType autocmd, rule `key-mappings`). Include
item 4 in this version: `<CR>` in the Task List buffer opens the task's
file at its line (from `tasks --agenda --json`'s `file`/`line`); it's
small and it's what makes the list useful.

- Goal: `:MetaNotesTaskList` shows `meta-notes tasks --agenda` in a
  reused readonly `Task List` scratch buffer (`buftype=nofile`,
  `filetype=markdown`), same create-or-reuse logic as
  `meta_notes#time_tracking#ShowReport()`. Render from `--json`, keeping
  each task's file and line per buffer line for the jump; the text
  should read like the CLI's agenda (headings per day, task lines).
- Files: new `autoload/meta_notes/task_list.vim`; `plugin/meta_notes.vim`
  (command, mapping); `doc/` help (command and mapping); README key
  mappings table and project structure; `test/task_list.vader`;
  CHANGELOG and version per rule `versioning`. No Python change unless
  `tasks --agenda --json` lacks file/line (say so if it does).
- Verify: the vader test renders a fixture root's agenda into the buffer,
  reuses it on a second call, and `<CR>` on a task line opens its file at
  its line; `./run_tests.sh` green.
- Out of scope: editing tasks from the buffer, filters or arguments
  (agenda only), conceal tricks.
- Model: Sonnet (Vimscript plus a vader test; small but not mechanical).
