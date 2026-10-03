---
id: zyab
title: Personal and work notes roots plan differently; make meta-notes flexible for both
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [daily-exercise-block-in-planning-u34c]
kind: explore
tasks: []
---

# Personal and work planning differences

The human uses meta-notes for both personal and work planning, in separate
notes roots. They said (2026-10-03, relayed by the notes advisor):

> When planning my days, like this is for my personal planning. I have work
> planning. Both use meta notes... there's some things that are different in
> how I manage, of course, my personal life and my work life. So we'll
> probably end up... trying to update meta notes a little bit so that it kind
> of is more flexible for that distinction.

## Not ready

An idea, not a design. Before it's scheduled, find out from the human which
differences matter: working hours and the working day in `prime`, which
ceremonies run (weekly review for a manager is work-only), templates, the
skills' wording. Then decide where each lives: per-root `.meta-notes` config,
the root's `CLAUDE.md` (which already overrides the guide), or templates.
Prefer what the root's `CLAUDE.md` already handles before adding config.

## More from the human, 2026-10-03

"Nothing is to be done yet, but just a note."

- Tags flip meaning between roots: "at work, everything's considered work,
  or it should be, unless it's personal or a break. But at home,
  everything's essentially personal, unless it's work... when you put it in
  one plug-in, it gets a little confusing between work and not work. So I
  don't know how to resolve that yet." This touches the time report's Work
  vs Non-Work split (286n). Home tags they'd use: `#exercise`, `#family`,
  and one for home maintenance (`#maint` or `#home`, undecided).
