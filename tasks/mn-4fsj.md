+++
id = "mn-4fsj"
title = "task add: blank line after the task when the H1 already has a blank line below it (3e6g follow-up)"
kind = "bug"
state = "claimed"
created_at = "2026-10-06T22:46:17.421Z"
updated_at = "2026-10-06T22:56:29.757949957Z"
created_by = "external:orchestrator"
watchers = [
    "external:orchestrator",
    "agent:manager-1",
]
+++

Follow-up to ticket 3e6g (mn-3e6g, merged 6a0c6bb, v2.26.3). Found by orchestrator on verifying the merge.

The reported case is not fixed. The notes advisor's daily note had '# title', a BLANK line, then 'Week Plan: [[...]]'. v2.26.3 still gives:

  # Daily
  (blank)
  - [ ] buy milk
  Week Plan: [[link]]

and test_task_update_add_without_line_with_existing_blank_after_h1 (test/unit/test_task_write.py) asserts that wrong output. The 3e6g fix only adds the blank line when it also had to add the blank before the task (blank_before), i.e. the H1 directly followed by text. Repro in a temp root: '# Title', '', '## Notes', '', 'text'; two task adds give '# Title', '', '- [ ] two', '- [ ] one', '## Notes' (no blank before the heading).

Change (scripts/meta_notes/task_update.py, add / _default_insert_point): whenever the default insert goes below the H1 (no Tasks heading, no --line), leave a blank line after the new task unless the next line is already blank, the end of the file, or another task in the same list (so a second add still joins the first). Fix that test to expect '# Daily', '', '- [ ] buy milk', '', 'Week Plan: [[link]]'; add one for two adds in that shape staying together with one blank before the paragraph. Check the spec wording in design/specs/task-add.md (r-80b1) still matches. Patch version bump.

Verify: ./run_tests.sh green; the repro above by hand.
Model: haiku (small, mechanical). Out of scope: a ## Tasks heading in the daily template (the human's call).
