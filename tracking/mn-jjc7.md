+++
id = "mn-jjc7"
title = "encode --interactive: show one line at a time, labelled as decode asks for it, Enter for the next"
kind = "feature"
state = "open"
created_at = "2026-11-24T13:47:32.897Z"
updated_at = "2026-11-24T13:50:20.769513508Z"
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
