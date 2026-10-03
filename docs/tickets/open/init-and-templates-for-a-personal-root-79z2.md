---
id: 79z2
title: init and templates for a personal root
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: [47rb]
see: [zyab]
tasks: []
---

# init and templates for a personal root

## Change

- `meta-notes init --mode personal` writes `mode = "personal"` into the new
  `.meta-notes` (`init.py:64` `SENTINEL_CONTENT` holds only a comment
  today); plain `init` writes no mode (work). Re-running init on an
  existing root never changes the mode.
- `templates/suggested-CLAUDE.md` is a work profile (08:00-17:00, desk
  lunch, `#meeting`/`#1-1`/`#recruiting`). Add a personal one, and have
  init's hint name the one that matches the mode.
- The daily template's span and log line come from kxxy.
- The human's personal root (`notes`) then gets `mode = "personal"` and
  its `CLAUDE.md` loses the work hours and the "don't tag `#personal`"
  workaround (a notes-repo change, done after these land).
