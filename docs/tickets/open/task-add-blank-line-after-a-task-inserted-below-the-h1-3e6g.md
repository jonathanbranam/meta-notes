---
id: 3e6g
title: "task add: blank line after a task inserted below the H1"
kind: bug
opened: 2026-10-06
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [cys2]
tasks: [mn-3e6g]
---

## The ask

# task add: blank line after a task inserted below the H1

Reported by the notes advisor, 2026-10-06 (notes m-0110), on v2.26.1
(cys2):

> on plan/daily/26-Q4/2026-10-10 Sat.md it inserted the task right after
> the H1's blank line with no blank line after it, so the task ran
> straight into 'Week Plan: [[...]]' (the paragraph below). It should
> leave a blank line after the inserted task too.

The advisor fixed the note by hand.

## Change

- `scripts/meta_notes/task_write.py` (or wherever cys2 put the
  below-the-H1 insert): when `task add` without `--line` finds no Tasks
  heading and inserts below the `# ` title, it leaves a blank line after
  the task too, unless the next line is already blank or the end of the
  file. A second task added the same way joins the first one's list
  (no blank line between the two tasks).
- Test in `test/unit/test_task_write.py` (or the cys2 tests): a note
  with an H1, a blank line and a paragraph gets H1, blank, task, blank,
  paragraph; a second add keeps the two tasks together.
- Patch version bump.

Not in this ticket: creating a `## Tasks` heading in daily notes that
have none (the advisor's other suggestion). That's a template question
for the human.

Verify: `./run_tests.sh` green; the case above by hand in a temp root.
