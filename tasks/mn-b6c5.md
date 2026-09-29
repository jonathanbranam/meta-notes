+++
id = "mn-b6c5"
title = "Time Block highlights for mtg:/pers:, [brackets], (parens) in daily notes"
kind = "feature"
state = "planned"
created_at = "2026-09-28T23:57:03.812Z"
updated_at = "2026-09-29T00:01:58.400195Z"
+++

Time Block highlights in daily notes (the human's request, 2026-09-28).

In a daily note, inside the Time Block section ONLY (nowhere else in the note, and never outside daily notes), highlight table cells like the human's work setup. Reference, read in place, don't copy into the repo: /Volumes/Data/downloads/vimrc.local.md lines 376-396 (azabiong/vim-highlighter, colour slots 1-7).

The Time Block is a markdown table. Each pattern highlights one cell (the text between two pipes), never across pipes or lines:

1. a cell containing `mtg:`
2. a cell containing `[square brackets]`
3. a cell containing `~text~` (two tildes in the same cell; this is also mn-d160's intended behaviour)
4. a cell containing `(parentheses)`
5. `train:`
6. `pers:`
7. `work:`

Seven distinct colours; vim-highlighter's default HiColor1-7 are a good palette. Depending on azabiong/vim-highlighter is fine if it simplifies the implementation; the worker decides.

Tests (vader): each pattern matches in a Time Block cell; none match outside the Time Block section of a daily note, or in a non-daily note; no match spans a pipe or a line.
