+++
id = "mn-y6mg"
title = "task add: accept --due undated (and none), like task update"
kind = "bug"
state = "integrated"
created_at = "2026-10-07T02:26:44.590Z"
updated_at = "2026-10-07T02:42:01.761096058Z"
created_by = "external:orchestrator"
watchers = [
    "external:orchestrator",
    "agent:manager-1",
]
branch = "bridle/add-undated"
commit = "2b3a306"
+++

Reported by the notes advisor, 2026-10-06 (notes m-0122): 'task add --due undated' fails with "argument --due: invalid value: 'undated' (expected YYYY-MM-DD)", so an undated task takes two calls (add with a date, then task update --due undated). Conventions (scripts/meta_notes/conventions.md line 11) say a bare due emoji is undated, and task update already takes '--due YYYY-MM-DD, undated (a bare due emoji), or none'. Confirmed by the orchestrator on v2.26.4.

Change: task add's --due takes 'undated' (writes a bare due emoji, same placement as task update) as well as a date; reuse task update's parsing. Whether 'none' makes sense on add (it means no due marker, i.e. the default) is the worker's call: accept it as a no-op or leave it out, and say which. Update design/specs/task-add.md, the --help text, doc/meta-notes.txt and conventions.md's task add line if it lists --due values. Test: add with --due undated writes '- [ ] x 📅'. Patch version bump.

Verify: ./run_tests.sh green; 'meta-notes task add a.md x --due undated' by hand in a temp root.
Model: haiku. Out of scope: other options on task add.

## Thread

### note · agent:add-undated · 2026-10-07T02:41:43.216Z
Implementation complete. Changes:

1. CLI (scripts/meta_notes/cli.py): Changed task add's --due argument from _day_value to _due_value, enabling 'undated' (and 'none' as a no-op).

2. Task update module (scripts/meta_notes/task_update.py): Updated add() docstring to reflect that 'undated' is now supported.

3. Spec (design/specs/task-add.md): Updated requirement to say --due accepts 'undated' (bare emoji); added scenario {#s-f0f1} for undated task.

4. Documentation:
   - doc/meta-notes.txt: Added note that --due accepts undated
   - scripts/meta_notes/conventions.md: Updated task add line to show undated option

5. Version: Bumped to 2.26.6 (PATCH for bug fix).

6. Tests:
   - test_task_update.py: Added test_add_undated() 
   - test_cli.py: Added test_task_add_undated(), removed stale ['--due', 'undated'] from error cases

Decision on 'none': Accept 'none' as a no-op (no due marker, same as default) for consistency with task update, even though it's not meaningful for add.

Manual test: ./bin/meta-notes task add test.md "example" --due undated correctly produces: - [ ] example 📅

All checks pass:
- ./run_tests.sh: 183/183 ✓
- uv run pytest test/unit/: 1568 passed ✓
- bridle spec check --require-ids: 30 file(s) ✓

Commit: accc7c62f1f7ad1998f546e116e471792db789c1

### note · agent:manager-1 · 2026-10-07T02:41:59.408Z
integrated: 2b3a306 (branch bridle/add-undated)

### note · agent:manager-1 · 2026-10-07T02:41:59.412Z
cleanup: removed nothing

### note · agent:manager-1 · 2026-10-07T02:42:01.761Z
Merged: 2b3a306, tagged v2.26.6, task done, worker removed. Worker reported vader 183/183, pytest 1568 passed, spec check 0 errors, and its hand run of 'task add --due undated' gave '- [ ] example 📅'. 'none' is accepted as a no-op (edit_line removes a marker that isn't there; no test for it). I did not rerun the suite. Ticket left for the orchestrator.
