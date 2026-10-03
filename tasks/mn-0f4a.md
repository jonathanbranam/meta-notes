+++
id = "mn-0f4a"
title = "init warns when the file watcher is missing (ticket init-warns-when-file-watcher-missing-h528)"
kind = "feature"
state = "integrated"
created_at = "2026-10-03T00:14:21.072Z"
updated_at = "2026-10-03T00:16:23.493730244Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
commit = "40785d6"
+++

See docs/tickets/open/init-warns-when-file-watcher-missing-h528.md. init checks for fswatch (macOS) / inotifywait (Linux) and prints the install command (brew install fswatch; sudo apt install inotify-tools on Debian-like); installs nothing. README install commands. PATCH bump. git mv the ticket to resolved/ when done.

## Thread

### note · agent:manager · 2026-10-03T00:16:23.493Z
integrated: 40785d6
