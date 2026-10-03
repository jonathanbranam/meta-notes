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

### Requirement: Runtime control  {#r-6462}
The plugin SHALL provide `:MetaNotesAutosave` and `:MetaNotesAutoreload` (`on`, `off` or `toggle`, default toggle) and `:MetaNotesAutoStatus`, which shows autosave, autoreload, the watcher binary, the timer interval and the conflict diff setting.

#### Scenario: Toggle  {#s-67dd}
*Verification*: **non-executable**
- **WHEN** the user runs `:MetaNotesAutosave on`
- **THEN** autosave SHALL be on and the state SHALL be shown

### Requirement: GitGutter off in notes buffers  {#r-dc2f}
Unless `g:meta_notes_disable_gitgutter` is 0 (default 1), the plugin SHALL run `:GitGutterBufferDisable` on notes buffers, on read and on entry, whether or not autosave or autoreload is on. It SHALL do so only when `exists(':GitGutterBufferDisable')`, and SHALL NOT use the global `:GitGutterDisable`.

#### Scenario: Notes buffer  {#s-7773}
*Verification*: **non-executable**
- **WHEN** a buffer's file is under a notes root and vim-gitgutter is installed
- **THEN** `:GitGutterBufferDisable` SHALL run for that buffer

#### Scenario: Other buffer or option off  {#s-982c}
*Verification*: **non-executable**
- **WHEN** a buffer is outside a notes root, or `g:meta_notes_disable_gitgutter` is 0, or vim-gitgutter isn't installed
- **THEN** the plugin SHALL NOT disable GitGutter and SHALL NOT error
