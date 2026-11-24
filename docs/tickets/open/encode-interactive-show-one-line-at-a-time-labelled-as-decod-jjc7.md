---
id: mn-jjc7
title: "encode --interactive: show one line at a time, labelled as decode asks for it, Enter for the next"
kind: feature
created: 2026-11-24
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: [mn-8f4y, mn-abjq]
---

## The ask

From the human, meta-notes aide session, 2026-11-24, verbatim:

> the other thing I'd like is an "interactive" or "line-by-line" mode for the encoding side as well. This should be an option, but with the current approach it's hard to keep track of where I'm at in the encoding; with this option specified it should print one line at a time, waiting for <enter> and the format should match the decode like 'the header line: <words>' then 'line 1 of 11: <words>'

## What to build

1. **An option on encode**, `--interactive` / `-i` (aide's pick of the human's two names; the human can rename it). Without it, encode is unchanged.
2. **With it, encode shows one line at a time.** It prints the first line and waits for Enter, then the next, and so on until the last line:

   ```
   the header line: babab babas rojat fivun gazof
   line 1 of 2: badom kijos kudoz fadul jobit
   line 2 of 2: kutuf kudoh mihop
   ```

   Each label is exactly what decode prompts for that line (`the header line`, `line N of TOTAL`, from `words.decode` and the `{label}: ` prompt in cli.py), so the line the user reads off one machine matches the prompt on the other. Take the labels from one shared place so they can't drift.
3. **Input is the same as encode's today** (argument, else pipe, else the hidden prompt). Enter is read from the terminal (`/dev/tty`), not stdin, so a piped secret still works with `-i`. With no terminal, `-i` is an error that says it needs one.
4. **No other changes**: the encoded format, decode and plain encode output stay as they are. `--json` with `-i` is an error.

Update the spec (design/specs/words.md), tests (labels match decode's prompts; Enter between lines; piped secret with `-i`; no terminal), Vim help (`:help meta-notes-cli-encode`), README if it lists flags, and CHANGELOG. Use fake values only.

## Not now

Going back a line, or clearing the screen between lines: not asked for.
