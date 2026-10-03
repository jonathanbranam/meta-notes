---
id: h528
title: init warns when the file watcher (fswatch or inotifywait) is missing
opened: 2026-10-02
repos: [meta-notes]
changes: []
specs: [init, notes-autosave]
needs: []
see: [vim-autosave-and-autoreload-egvk]
---

# init warns when the file watcher is missing

Autoreload's watcher job needs `fswatch` (macOS) or `inotifywait`
(Linux). Only `:help meta-notes-autosave` says how to install them; the
README names the tools without an install command, and `init` doesn't
check for either.

The human, 2026-10-02, agreed: init checks and prints the exact command,
and installs nothing (no `brew install`: it runs `brew update` and can
upgrade other packages; apt needs sudo; and init can't tell whether the
user turned autoreload on).

## Change

1. `meta-notes init` checks for the platform's watcher with
   `shutil.which`, the way it checks for `meta-notes` on PATH, and when
   it's missing prints a warning (init still succeeds) with the command:
   - macOS (`fswatch`): `brew install fswatch`
   - Linux (`inotifywait`), Debian or Ubuntu (`/etc/os-release` ID or
     ID_LIKE has `debian`): `sudo apt install inotify-tools`
   - other Linux: name the `inotify-tools` package.
   Say it's only needed for `g:meta_notes_autoreload`. Same text in
   `--json` output's warnings.
2. README, Autosave and Autoreload: add the two install commands.
3. `:help` for init mentions the warning.

## Done means

Spec (init, and notes-autosave if it lists the requirement) and `:help`
updated; unit tests for found, missing on macOS, missing on Debian-like
Linux and missing on other Linux (mock `which`, platform and os-release).
PATCH bump.
