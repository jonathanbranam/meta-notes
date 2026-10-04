---
id: rb4z
title: NERDTree refreshes when folders and files are added in a notes root
kind: feature
opened: 2026-10-04
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: [mn-rb4z]
---

## The ask

The human, 2026-10-04: "vim is now reacting well to file updates, but my
nerd tree explorer doesn't update when new folders are added; investigate
potential solutions and write a ticket with the options and your
recommendation." It must be light on CPU and memory, like the live file
updates, with an opt-out (rule `light-on-resources`).

## Today

`autoload/meta_notes/autosave.vim` already runs one watcher job per notes
root (`fswatch -r`, or `inotifywait -m -r` with `create,delete,moved_to`),
with `.git`, `.venv` and `.meta-notes-cache` excluded. `s:WatcherOutput`
gets one path per line and only checks a loaded buffer with that name.
Other paths, including new folders, are dropped. NERDTree (installed:
preservim/nerdtree 690d061) has no auto-refresh of its own; the user
presses `R`/`r` or runs `:NERDTreeRefreshRoot`.

NERDTree's API: `g:NERDTree.IsOpen()` (a tree in this tab),
`b:NERDTree.root.findNode(g:NERDTreePath.New(dir))`,
`node.refresh()` (re-globs that directory and its already-loaded children
only) and `b:NERDTree.render()`. A collapsed directory that was never
opened has no children loaded, and NERDTree reads it fresh when opened, so
it needs nothing.

## Options

1. **Reuse the watcher, refresh only the changed directory (recommended).**
   In `s:WatcherOutput`, when the path isn't a loaded buffer (or is a
   create/delete/move), queue its parent directory. A debounce timer
   (~300 ms, reset per event) drains the set: for each tab whose NERDTree
   window is visible, find the parent's node; if it's in the tree and has
   loaded children, `refresh()` it, then render once, saving the cursor and
   returning to the user's window. Never refresh while in insert mode or
   the command line; retry on the next event or `CursorHold`.
   Cost: no new process, no polling; work only when files change and a
   tree is open, and only on the changed directories. Nothing happens in
   Vim sessions without NERDTree (`exists('g:NERDTree')` guard).
2. **Refresh the root on the watcher event.** Same trigger, but
   `:NERDTreeRefreshRoot`. Simpler, but it re-globs every expanded
   directory and echoes "This could take a while..." each time; a
   `git pull` or an agent writing many notes would refresh repeatedly.
3. **Refresh when focus returns or the tree window is entered.**
   `FocusGained` / `BufEnter` on the NERDTree buffer refreshes the
   expanded directories. No watcher needed, so it works where fswatch or
   inotifywait is missing, but the tree is stale while the user watches
   it, which is the case the human hit (agents adding folders while Vim
   sits open).
4. **A timer.** Poll and refresh every N seconds. Constant work for a rare
   event; rejected.
5. **Another plugin** (e.g. switch to fern.vim or nvim-tree, which watch
   files). Out of scope: the human uses NERDTree.

## Recommendation

Option 1, with option 3's `BufEnter` refresh of the tree window as a
cheap fallback when no watcher is running (no fswatch/inotifywait, or
`g:meta_notes_watch = 0`). Opt-out: `g:meta_notes_nerdtree_refresh = 0`
(default 1; only acts when NERDTree is loaded). Document in
`doc/meta-notes.txt` beside autosave, and in the README's Autosave and
Autoreload section.

Watch out for: fswatch reports a directory create as the directory's own
path (its parent is what to refresh), and a whole new subtree as many
events (the debounce collapses them); renames show as delete plus create;
NERDTree windows in other tabs (refresh only visible ones; others refresh
on `BufEnter`); the plugin's own reload (`:MetaNotesReload`) must not
start a second timer. Tests: vader with a stub `g:NERDTree` (NERDTree
isn't a test dependency) for the queue, the debounce and the opt-out.
