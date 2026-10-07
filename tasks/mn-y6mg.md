+++
id = "mn-y6mg"
title = "task add: accept --due undated (and none), like task update"
kind = "bug"
state = "open"
created_at = "2026-10-07T02:26:44.590Z"
updated_at = "2026-10-07T02:26:48.515618852Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
+++

Reported by the notes advisor, 2026-10-06 (notes m-0122): 'task add --due undated' fails with "argument --due: invalid value: 'undated' (expected YYYY-MM-DD)", so an undated task takes two calls (add with a date, then task update --due undated). Conventions (scripts/meta_notes/conventions.md line 11) say a bare due emoji is undated, and task update already takes '--due YYYY-MM-DD, undated (a bare due emoji), or none'. Confirmed by the orchestrator on v2.26.4.

Change: task add's --due takes 'undated' (writes a bare due emoji, same placement as task update) as well as a date; reuse task update's parsing. Whether 'none' makes sense on add (it means no due marker, i.e. the default) is the worker's call: accept it as a no-op or leave it out, and say which. Update design/specs/task-add.md, the --help text, doc/meta-notes.txt and conventions.md's task add line if it lists --due values. Test: add with --due undated writes '- [ ] x 📅'. Patch version bump.

Verify: ./run_tests.sh green; 'meta-notes task add a.md x --due undated' by hand in a temp root.
Model: haiku. Out of scope: other options on task add.
