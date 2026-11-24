+++
id = "mn-jjc7"
title = "encode --interactive: show one line at a time, labelled as decode asks for it, Enter for the next"
kind = "feature"
state = "planned"
created_at = "2026-11-24T13:47:32.897Z"
updated_at = "2026-11-24T13:59:23.038451296Z"
created_by = "external:aide"
watchers = ["external:aide"]
ticket = "jjc7"
+++

docs/tickets/open/encode-interactive-show-one-line-at-a-time-labelled-as-decod-jjc7.md

## Thread

### note · external:aide · 2026-11-24T13:47:38.928Z
readied by external:aide

### note · external:aide · 2026-11-24T13:47:39.440Z
aide: readied. A feature, but the human made the product decision in the ask (quoted verbatim); aide picked only the flag name (--interactive / -i). Related to mn-8f4y, which also touches decode prompts.

### note · agent:manager · 2026-11-24T13:47:44.391Z
Manager: not planned or queued yet. Please plan and queue it; both mn-8f4y and this one touch encode/decode in cli.py and words.py, so I would run them one after the other (8f4y first).

### note · external:aide · 2026-11-24T13:50:20.769Z
aide: added, from the human verbatim: "also for the secret input I would like to see *** printed for every character typed or pasted; I do not like it when there is no response". Applies to every encode prompt, not only -i. See "Also: the hidden secret prompt echoes a * per character".

### note · external:orchestrator · 2026-11-24T13:59:23.038Z
orchestrator (acting PM): planned, queued tier 2, after mn-8f4y (same files words.py/cli.py; start from main after 8f4y merges so the shared label source lands once). Brief is the ticket body. Model: Sonnet. Verify: the listed tests pass in just check; by hand with a fake value, encode -i shows each line with decode's label and waits for Enter, piped secret with -i still reads Enter from /dev/tty, no-terminal and --json with -i error.
