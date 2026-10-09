+++
id = "mn-7tfg"
title = "Conflict diff closes and silently discards the newer disk write (autosave.vim, manual :w)"
kind = "bug"
state = "pending"
created_at = "2026-10-09T20:00:53.146Z"
updated_at = "2026-10-09T20:00:53.146Z"
created_by = "external:orchestrator@dalek"
watchers = ["external:orchestrator@dalek"]
+++

Filed by orchestrator for the human (via email to the bridle mail bridge, 2026-10-09 ~4:00 PM ET, SES hbkhpn5humocnkivtqe9m18sv4c8aa53t16tvo81: "Please file this as a bug report on the meta-notes project."). The report, verbatim:

# project/meta-notes/Conflict diff closes and silently discards the newer disk write

## Background

While an agent (Claude Code) was editing a daily note and the user had
the same file open in Vim with unsaved edits, autoreload's conflict
handling opened a diff split, but a second on-disk write landed before
the user resolved it. The diff split had already closed by then, so
when the user ran `:w` they just saw Vim's native "file has changed
since editing started; really overwrite?" prompt, with no indication a
second change was involved or how to recover it. The user chose `Y`
("overwrite anyway") and lost the agent's second edit.

## Sequence of events

1. User edits the note in Vim (buffer now modified).
2. Agent edits the note on disk (first on-disk change since the user's
   buffer was read).
3. `autosave.vim`'s `s:Conflict()` fires (modified buffer + changed
   stamp): it opens a vertical scratch split with the on-disk contents
   and `diffthis` on both windows (`s:OpenDiff()`,
   `autoload/meta_notes/autosave.vim` around lines 354–390).
4. While that diff split is still open and unresolved, the agent writes
   the note *again* (a second on-disk change).
5. User finishes reconciling the first diff and runs `:w` in the
   original buffer.

At this point Vim's own file-changed check kicks in (its mtime
comparison, independent of meta-notes' tracked `meta_notes_stamp`): the
file's mtime no longer matches what Vim read, because of the second
write in step 4. Vim shows its native prompt — something like:

```
W12: Warning: File "... .md" has changed since editing started
Do you want to write anyway? (y/n)
```

The user didn't know this prompt meant "there is now a *third* version
of this file on disk that you haven't seen" — the meta-notes diff
split from step 3 was already gone (it closes on any successful `:w`,
via `s:ClearConflict()`, lines 405–414), so there was no visual cue that
anything had changed again since that diff was last shown. Choosing `Y`
overwrote disk with the buffer's content, discarding the agent's second
edit with no backup and no recovery path.

## Root cause

- `s:OpenDiff()` snapshots the disk contents *once*, at the moment the
  first conflict is detected. It does not re-check or re-open if the
  file changes again while the diff is still open — the scratch buffer
  the user is comparing against can go stale while they're literally
  looking at it.
- `meta_notes#autosave#Save()` (lines 318–350) does guard against this
  for the *autosave* path: before writing, it checks `s:DiskStamp(a:buf)
  !=# getbufvar(a:buf, 'meta_notes_stamp', '')` and calls `s:Conflict()`
  instead of writing if the disk changed again. But that check only
  runs inside the plugin's own autosave flow. A manual `:w` from the
  user goes straight through Vim's normal write path, which has its own
  independent "changed since editing started" check and its own y/n
  prompt — the plugin's conflict machinery (and its diff view) isn't in
  the loop for that at all, so there is no second chance to see what
  changed.
- There is also no "disk changed again" notification equivalent to
  `s:Message(... 'autosave paused. Resolve, then :w' ...)` for this
  second-change-during-an-open-diff case — the user gets no meta-notes
  message at all between the first conflict message and Vim's own
  unrelated-looking prompt.

## Suggested fix direction (for meta-notes plugin, not this repo)

- Hook `FileChangedShell`/`BufWritePre` (or re-run the stamp check right
  before any write of a notes buffer, not just inside
  `meta_notes#autosave#Save()`) so a manual `:w` is covered by the same
  "did disk change again since I showed you a diff" guard, not just
  autosave's internal path.
- If the disk stamp has moved again while the scratch diff buffer from
  step 3 is still open, refresh the scratch buffer's contents (re-`read`
  the file) and re-message the user, rather than silently leaving a
  stale diff on screen (or none at all, once it's been closed for other
  reasons) while a plain Vim prompt handles the actual decision.
- At minimum, intercept Vim's own "has changed since editing started"
  write path for notes buffers and redirect it into
  `s:Conflict()`/`s:OpenDiff()` so the user always sees a diff — current
  on-disk contents vs. their buffer — before choosing to overwrite,
  instead of a bare y/n prompt with no diff available.
