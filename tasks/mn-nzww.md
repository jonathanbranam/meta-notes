+++
id = "mn-nzww"
title = "conventions.md: ASCII for the za9m Time Block examples"
kind = "chore"
state = "integrated"
created_at = "2026-10-07T01:38:15.466Z"
updated_at = "2026-10-07T01:51:05.176045110Z"
created_by = "external:orchestrator"
watchers = [
    "external:orchestrator",
    "agent:manager-1",
]
branch = "bridle/ascii-examples"
commit = "41e8c75"
+++

mn-za9m (5100f09, v2.26.5?) added examples to scripts/meta_notes/conventions.md (Editing the Time Block) written with U+2192 arrows and U+2013 en dashes, e.g. '9:00–10:00 → fills ...'. conventions.md had none before. Rule ascii-in-editable-text: the human edits these docs in Vim and can't easily type them.

Change: in that block only, write '9:00-10:00' with a hyphen and 'fills' without the arrow (e.g. '- `9:00-10:00` fills `9:00am, ...`'). Check design/specs/time-block-skill.md's new lines for the same and fix them too. No other text changes. Patch version bump if the project's versioning rule requires it for docs (.bridle/rules/versioning.md).

Verify: grep -nP '[\x{2013}\x{2014}\x{2192}]' scripts/meta_notes/conventions.md design/specs/time-block-skill.md prints nothing; ./run_tests.sh green.
Model: haiku. Out of scope: the za9m ticket's own text (the human's examples).

## Thread

### note · agent:ascii-examples · 2026-10-07T01:50:24.641Z
Done: 7 en dashes replaced with hyphens, 7 arrows removed in conventions.md event examples. All tests pass: 183 Vader, 1567 pytest, 30 spec checks. Commit: 6379da7

### note · agent:manager-1 · 2026-10-07T01:51:03.233Z
integrated: 41e8c75 (branch bridle/ascii-examples)

### note · agent:manager-1 · 2026-10-07T01:51:03.238Z
cleanup: removed nothing

### note · agent:manager-1 · 2026-10-07T01:51:05.176Z
Merged: 41e8c75, no version bump or tag (text-only chore; the worker did not bump). Worker reported vader 183/183, pytest 1567 passed, spec check 0 errors (not rerun by me; diff reviewed: only the 7 example lines changed, no time-block-skill.md change needed). Ticket for nzww, if any, left to the orchestrator.
