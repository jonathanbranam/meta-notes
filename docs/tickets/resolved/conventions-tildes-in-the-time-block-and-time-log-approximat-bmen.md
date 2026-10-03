---
id: bmen
title: "Conventions: tildes in the Time Block and Time Log (approximate times, missed plans)"
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [wn9j, zqqb]
tasks: [mn-caa0]
closed: 2026-10-03T14:49:27Z
---

# Conventions: tildes in the Time Block and Time Log

## The ask

The human, 2026-10-03 (relayed by the notes advisor, m-0235 and m-0040),
approved: "That's definitely a rule that should come from meta notes
conventions... go ahead and update that." Two rules move into the
conventions text (`meta-notes conventions`, and so `prime`), for the Time
Block and the Time Log:

1. A tilde before a time means approximately: `home ~9:20`,
   `until ~10:55`. The human: "I do prefer that you use a single tilde for
   approximate times. That's super helpful." The single-tilde
   highlighting bug for `~time` is fixed.
2. A Plan cell for a row that already happened and didn't go as planned
   is wrapped in single tildes, `~feed the dogs~`, never double. The Plan
   isn't rewritten; Actual gets a short summary of what happened instead.

## Changes

- `scripts/meta_notes/conventions.md`: both rules, in or next to
  "Editing the Time Block" / "Editing the Time Log".
- `skills/time-block/SKILL.md`: it now says never use `~` for
  "approximately" (write `about 9:20`), which contradicts rule 1. Drop
  that, and point at the conventions instead of restating rule 2 where
  that reads cleanly.
- Tests that pin the conventions text, a patch release.

Until this ships, the notes root's CLAUDE.md holds both rules; the notes
advisor removes them there afterwards.

