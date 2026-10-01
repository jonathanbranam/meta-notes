+++
id = "mn-cf3d"
title = "Reload notice still never shows in a real Vim (v2.8.1)"
kind = "bug"
state = "integrated"
created_at = "2026-10-01T19:51:31.208Z"
updated_at = "2026-10-01T19:55:22.523991075Z"
branch = "bridle/reload-notice"
commit = "2bc964b"
summary = "Cause: FileChangedShellPost does fire for the autoread reload, but s:Check runs 'silent! checktime' and silent! swallowed the handler's :echomsg. Fix: s:Notice stores the stamp, then shows the message from timer_start(0). Reproduced and verified in a real Vim via tmux before and after; vader test now does a real outside edit and checks :messages. Version 2.8.2, merged 2bc964b, tagged v2.8.2. Side finding: a hit-enter prompt at startup (for example an error in a user after/plugin) blocks timers entirely."
+++

Follow-up to ticket autoreload-timer-and-notice-bugs-6p68. v2.8.1 fixed the timer: an outside edit now reloads within the interval. But no 'meta-notes: reloaded ... (u to undo)' message appears, not on the message line and not in :messages, for timer- or watcher-triggered reloads of an unmodified buffer. The FileChangedShellPost <buffer> autocmd is registered (:au meta_notes_buffer shows it). The vader test calls OnChangedShellPost() directly, so it can't catch this. Find out in a REAL Vim whether FileChangedShellPost fires for an autoread reload, and what v:fcs_reason holds then. If it doesn't fire, detect the reload another way (e.g. compare the stored stamp in the checktime path, or use the BufReadPost that a reload triggers) and show the notice. Repro (tmux is installed): make a scratch root with .meta-notes and plan/daily/note.md; vimrc with set runtimepath^=<worktree>, filetype plugin on, g:meta_notes_autoreload=1, g:meta_notes_watch=0, g:meta_notes_checktime_interval=1000; tmux new-session -d -s t -x 120 -y 30 "vim -u vimrc -i NONE plan/daily/note.md"; overwrite the file; sleep 2; tmux send-keys -t t ':messages' Enter; tmux capture-pane -p -t t. Done means the notice shows in that repro (report the capture to the manager). PATCH bump.

## Thread

### note · agent:manager · 2026-10-01T19:55:19.849Z
integrated: 2bc964b (branch bridle/reload-notice)

### note · agent:manager · 2026-10-01T19:55:19.853Z
cleanup: removed nothing
