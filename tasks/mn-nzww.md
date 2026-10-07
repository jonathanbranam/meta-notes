+++
id = "mn-nzww"
title = "conventions.md: ASCII for the za9m Time Block examples"
kind = "chore"
state = "open"
created_at = "2026-10-07T01:38:15.466Z"
updated_at = "2026-10-07T01:38:18.847170481Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
+++

mn-za9m (5100f09, v2.26.5?) added examples to scripts/meta_notes/conventions.md (Editing the Time Block) written with U+2192 arrows and U+2013 en dashes, e.g. '9:00–10:00 → fills ...'. conventions.md had none before. Rule ascii-in-editable-text: the human edits these docs in Vim and can't easily type them.

Change: in that block only, write '9:00-10:00' with a hyphen and 'fills' without the arrow (e.g. '- `9:00-10:00` fills `9:00am, ...`'). Check design/specs/time-block-skill.md's new lines for the same and fix them too. No other text changes. Patch version bump if the project's versioning rule requires it for docs (.bridle/rules/versioning.md).

Verify: grep -nP '[\x{2013}\x{2014}\x{2192}]' scripts/meta_notes/conventions.md design/specs/time-block-skill.md prints nothing; ./run_tests.sh green.
Model: haiku. Out of scope: the za9m ticket's own text (the human's examples).
