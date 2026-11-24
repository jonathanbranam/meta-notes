+++
id = "mn-8f4y"
title = "decode: piped input reads words as a stream, any whitespace between words and lines"
kind = "fix"
state = "planned"
created_at = "2026-11-24T13:44:01.452Z"
updated_at = "2026-11-24T13:59:22.740380576Z"
created_by = "external:aide"
watchers = ["external:aide"]
ticket = "8f4y"
+++

docs/tickets/open/decode-piped-input-reads-words-as-a-stream-any-whitespace-be-8f4y.md

## Thread

### note · external:aide · 2026-11-24T13:44:06.284Z
readied by external:aide

### note · external:aide · 2026-11-24T13:44:06.546Z
aide: readied under ready-without-asking (a fix with one clear design, the human's ask quoted above).

### note · agent:manager · 2026-11-24T13:44:11.546Z
Manager: not planned or queued yet. Please plan and queue it; I will spawn a worker once startable.

### note · external:aide · 2026-11-24T13:44:48.100Z
HOLD. The human, via aide, 2026-11-24: "hold the ticket a second". Do not plan, queue or start it until the human says go. hold: design set in front matter.

### note · external:aide · 2026-11-24T13:46:20.377Z
Hold lifted. The human, via aide, 2026-11-24: "sure, so also the CLI should work if I just paste in the entire text as well". The ask now covers interactive decode too: pasting the whole text at the prompt decodes, wrapped any way (see The fix). Ready to plan.

### note · external:orchestrator · 2026-11-24T13:59:22.740Z
orchestrator (acting PM): planned, queued tier 1. Brief is the ticket body (as widened by the human: piped and pasted input both read as a word stream). Model: Sonnet. Shares words.py/cli.py with mn-jjc7 (tier 2): run them one after another, this first. Verify: the listed tests pass in just check; by hand with fake values, piped all-on-one-line and mid-line-break inputs decode, and pasting a whole blob at the interactive prompt decodes.
