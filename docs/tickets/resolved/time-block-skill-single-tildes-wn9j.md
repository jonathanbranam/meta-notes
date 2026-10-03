---
id: wn9j
title: "time-block skill: single tildes for off-plan rows, never ~ for approximately"
kind: bug
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [zqqb]
tasks: [mn-3221]
closed: 2026-10-03T14:37:21Z
---

# time-block skill: single tildes, never `~` for "approximately"

The human, 2026-10-03 (relayed by the notes advisor): "No, single tildes. I
don't like double tildes; they're too long. Single tildes are what I have
configured in my syntax highlighting." The plugin's highlighting
(`after/syntax/markdown.vim`, `metaNotesOffPlan` and
`metaNotesTimeBlockTilde`) and `:help meta-notes-timeblock-hl` already use
`~text~`; the skill shipped in v2.12.2 says `~~write spec~~`.

## Change

1. `skills/time-block/SKILL.md`: the off-plan rule wraps the Plan in single
   tildes, `~write spec~`; drop "This is the default until the user says
   otherwise".
2. Add a hard rule: don't write `~` to mean "approximately" in the Time
   Block (`home ~9:20`); the single-tilde highlight catches it. Write
   `about 9:20` or the time alone.
3. The `time-block-skill` spec, if it names the tildes.

## Done means

Spec matches; checks pass. PATCH bump.
