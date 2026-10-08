---
id: zk5p
title: "Guard hook: refuse a meta-notes --expect computed at write time"
kind: feature
opened: 2026-10-08
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: [mn-zk5p]
---

## The ask

Approved by the human, via the notes advisor (2026-10-08): "I like number
three" (the guard hook option). Incident: the advisor ran `meta-notes task
update` with `--expect "$(sed -n ${n}p file)"` on line numbers grepped
before its own 3-line insert, so `--expect` compared the line with itself
and a finished task's date changed. The notes root now has rule
`.bridle/rules/expect-what-you-read.md`.

Ship a Claude Code PreToolUse hook with meta-notes that refuses a Bash
command running `meta-notes` (or `bin/meta-notes`) when `--expect`, or any
other check argument (time-log's `--prev`, for example), holds a command
substitution: `$(...)` or backticks. The refusal message says why in one
line: the expected text must be what you read earlier, written out
literally; computing it at write time turns the check off. The message
stands on its own (no bridle rule names): it must work in a root without
bridle, such as the human's work repo. The human, via aide, 2026-10-08:
the fix must live in meta-notes, not depend on an agent rule ("it's also
going to depend on the agent following the rule, which I am not convinced
is the right way to fix this").

- The hook is a CLI subcommand (for example `meta-notes hook expect-guard`)
  that reads the PreToolUse JSON on stdin and blocks with exit 2 and the
  message on stderr; anything else passes.
- `meta-notes init` wires it into the root's `.claude/settings.json`, the
  way it links the skills: create the file if missing, add the hook if
  absent, leave the rest of the file alone, idempotent. (init never edits
  CLAUDE.md; settings.json is tool config, like the skills links.)
- A `$VAR` that was set earlier from a literal is fine; only `$(` and
  backticks inside the check argument are refused. Don't try to parse
  shell fully: match the argument text.

Verify: unit tests for the hook (a refused `--expect "$(sed ...)"`, a
refused backtick form, an allowed literal and an allowed `"$old"`), and an
init test for the settings.json merge. `./run_tests.sh` and pytest green
once. Model: Sonnet (shell-argument matching needs care). Size: S.
