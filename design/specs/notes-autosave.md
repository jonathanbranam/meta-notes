## Purpose

Specifies the Vim plugin's opt-in autosave and autoreload for notes buffers, so the human's unsaved edits are saved quickly and agents' edits (made through the CLI) show up quickly, without either overwriting the other.

## Requirements

### Requirement: Off by default and scoped to notes buffers  {#r-72f4}
The plugin SHALL do nothing for autosave and autoreload unless `g:meta_notes_autosave` or `g:meta_notes_autoreload` is set. When set, it SHALL apply only to buffers whose file is under a notes root, found as the nearest directory containing `.meta-notes`, stopping after `$HOME`.

#### Scenario: Buffer outside a notes root  {#s-8344}
*Verification*: **non-executable**
- **WHEN** autosave and autoreload are on and a buffer's file has no `.meta-notes` in its ancestors
- **THEN** the plugin SHALL NOT set `autoread` on it, save it, or check it for changes

### Requirement: Autoreload notices changes  {#r-8c8f}
With `g:meta_notes_autoreload` on, the plugin SHALL set `autoread` buffer-locally on notes buffers and run `:checktime` on `FocusGained`, from a file-watcher job (`fswatch` or `inotifywait`, one per notes root, excluding `.git/`, `.venv/` and `.meta-notes-cache/`, stopped when Vim exits) when `g:meta_notes_watch` is on, and every `g:meta_notes_checktime_interval` ms when that is above 0, started when the first notes buffer is attached (not only on a runtime toggle). When no watcher binary exists it SHALL say so once. It SHALL NOT reload a buffer in insert mode; the next check after leaving insert mode SHALL.

#### Scenario: Unmodified buffer reloads  {#s-5e9b}
*Verification*: **non-executable**
- **WHEN** a notes buffer has no unsaved edits and its file changes on disk
- **THEN** the buffer SHALL reload and a message SHALL say it was reloaded and that `u` undoes it, even when Vim skips `FileChangedShell` because `autoread` is set, and even when the reload happens inside a silenced `:checktime` (the plugin SHALL show the message from a timer, since `silent!` swallows `:echomsg`)

#### Scenario: Timer at startup  {#s-108a}
*Verification*: **non-executable**
- **WHEN** autoreload is on, `g:meta_notes_checktime_interval` is above 0, and a notes buffer is opened
- **THEN** the checktime timer SHALL be running, whether or not the watcher is on

### Requirement: Autosave never overwrites the disk  {#r-cbc5}
With `g:meta_notes_autosave` on, the plugin SHALL, after `g:meta_notes_autosave_delay` ms without a further change following `TextChanged` or `InsertLeave`, write the notes buffer only when the file on disk is unchanged since Vim read or wrote it, and SHALL NOT force a write or trigger Vim's changed-since-reading prompt.

#### Scenario: File changed on disk  {#s-37ee}
*Verification*: **non-executable**
- **WHEN** an agent changed the file after Vim read it and the buffer has unsaved edits
- **THEN** autosave SHALL NOT write, and the conflict flow SHALL start

### Requirement: Conflicts keep the buffer  {#r-9eb1}
When a notes buffer has unsaved edits and its file changed on disk, the plugin SHALL keep the buffer, SHALL NOT reload, SHALL pause autosave for that buffer with a message, and, when `g:meta_notes_conflict_diff` is on, SHALL open a scratch diff of the buffer against the file on disk. A successful write SHALL resume autosave and close the diff.

#### Scenario: Resolve by writing  {#s-0956}
*Verification*: **non-executable**
- **WHEN** the user resolves a conflict and writes the buffer
- **THEN** autosave SHALL resume for that buffer and the diff SHALL close

### Requirement: Manual writes are guarded  {#r-b6b5}
While autosave or autoreload is on, a write of a notes buffer to its own file (`:w`) SHALL be refused with a message when the file changed on disk since Vim read it or since the conflict diff was last shown. The refusal SHALL open the diff of disk against the buffer (when `g:meta_notes_conflict_diff` is on), or refresh an open diff to the current disk contents and message that the file changed again. A further write with the disk unchanged since SHALL NOT be refused by the plugin. The guard SHALL use a `BufWritePre` autocommand on notes buffers only, with no timer.

#### Scenario: Disk changed again under an open diff  {#s-9c28}
*Verification*: **non-executable**
- **WHEN** a conflict diff is open and the file changes on disk again, and the user writes
- **THEN** the write SHALL be refused, the diff SHALL show the latest disk contents, and the user SHALL be messaged

### Requirement: Runtime control  {#r-6462}
The plugin SHALL provide `:MetaNotesAutosave` and `:MetaNotesAutoreload` (`on`, `off` or `toggle`, default toggle) and `:MetaNotesAutoStatus`, which shows autosave, autoreload, the watcher binary, the timer interval and the conflict diff setting.

#### Scenario: Toggle  {#s-67dd}
*Verification*: **non-executable**
- **WHEN** the user runs `:MetaNotesAutosave on`
- **THEN** autosave SHALL be on and the state SHALL be shown

### Requirement: GitGutter off for a session started in a notes root  {#r-dc2f}
Unless `g:meta_notes_disable_gitgutter` is 0 (default 1), the plugin SHALL run the global `:GitGutterDisable` once, at VimEnter, when Vim's working directory is inside a notes root, whether or not autosave or autoreload is on. It SHALL do so only when `exists(':GitGutterDisable')`, and SHALL NOT use `:GitGutterBufferDisable`.

#### Scenario: Started in a notes root  {#s-7773}
*Verification*: **non-executable**
- **WHEN** Vim starts with its working directory inside a notes root and vim-gitgutter is installed
- **THEN** `:GitGutterDisable` SHALL run once

#### Scenario: Other directory or option off  {#s-982c}
*Verification*: **non-executable**
- **WHEN** the working directory is outside a notes root, or `g:meta_notes_disable_gitgutter` is 0, or vim-gitgutter isn't installed
- **THEN** the plugin SHALL NOT disable GitGutter and SHALL NOT error

### Requirement: NERDTree refresh  {#r-8af1}
Unless `g:meta_notes_nerdtree_refresh` is 0 (default 1) and only when `exists('g:NERDTree')`, the plugin SHALL, on a file watcher event for a path that is not a loaded buffer, queue the path's parent directory, and 300 ms after the last event (the timer reset per event, never more than one) SHALL refresh those directories in the NERDTree windows of the current tab that have them open or loaded, rendering each tree once and keeping the cursor and the user's window. It SHALL NOT refresh in insert mode or on the command line (CursorHold retries), and SHALL use no timer or process of its own to poll. Entering a NERDTree window SHALL start the watcher for its notes root and, when no watcher is running for it or the tree missed events (another tab), refresh the tree.

#### Scenario: Burst of changes  {#s-973d}
*Verification*: **non-executable**
- **WHEN** a folder with files is added under an expanded directory of a visible tree
- **THEN** that directory SHALL be refreshed and the tree rendered once, after the burst

#### Scenario: Opt-out or no NERDTree  {#s-3860}
*Verification*: **non-executable**
- **WHEN** `g:meta_notes_nerdtree_refresh` is 0, or NERDTree isn't loaded
- **THEN** the plugin SHALL queue nothing and start no timer
