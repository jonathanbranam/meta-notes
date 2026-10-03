---
id: 47rb
title: "Root mode: mode = work or personal in .meta-notes"
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [zyab]
tasks: []
---

# Root mode: `mode = "work"` or `"personal"` in `.meta-notes`

The foundation for zyab. The human decided, 2026-10-03:

> we're going to just use meta notes itself to determine whether to change
> some behaviors, depending on whether this is a work repo or a personal
> repo ... some of the implementation will take a flag or a parameter to
> tell if this is a work repo or not. We should read it from a file. It
> probably goes in configuration ... that could turn certain things on and
> off and change behavior across the [plugin] and throughout the scripts.

## Design (proposed)

- A top-level key in `.meta-notes` (read as TOML by `config.py`):
  `mode = "work"` or `mode = "personal"`. Absent means `work`, today's
  behaviour, so existing roots don't change. Any other value is an error
  naming the two choices.
- One accessor in `config.py` (e.g. `config.mode(root)`) that every command
  uses. Today only `calendar` and `checkin wait` load config; the time
  report and `prime` read none, so they gain a config load.
- Visible to agents: `meta-notes prime` states the mode near the top, and
  `meta-notes conventions` prints the mode's text where it differs (the
  dependent tickets fill those parts). Agents learn the mode from the CLI,
  never by guessing from the root's path.
- Visible to Vim and scripts: `--json` output that depends on it carries
  `"mode"`; the plugin reads it through the CLI if it ever needs it
  (nothing in Vim needs it yet).
- The root's `CLAUDE.md` keeps personal preferences (routines, a workout);
  the mode covers what the code and the shipped skills do.

## Out of scope

Each behaviour that changes is its own ticket: 357e (time report), kxxy
(hours and days), bup2 (ceremony skills), 79z2 (init and templates).

## Open with the human

- The key's name and values (`mode`, `work`/`personal`).
- Whether hours and workdays get their own keys now or only mode defaults
  (kxxy).
