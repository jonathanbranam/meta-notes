---
id: mn-p6ga
title: tasks --agenda leaves out started tasks due after the horizon
kind: bug
created: 2026-10-19
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
resolved: 2026-10-19T20:36:14Z
---

## The ask

From the human, by email to the aide (m-0110, 2026-10-19 4:22 PM ET), subject "Bug with agenda view", verbatim:

> See markdown attachment for a bug in the agenda view. Please fix this in the next version.

The attachment is kept at `/srv/shared/work/meta-notes-work/.bridle/inbox/mail/samsj7epdilnl4f43uu54qh6h9lvcb1j91vurko1/Task_list_agenda_hides_tasks_started_today_or_earlier.md`. Its gist:

- The task list buffer (`<localleader>t`, `:MetaNotesTaskList`, which runs `meta-notes tasks --agenda`) leaves out a task that has started (`🛫` today or earlier) when its due date (`📅`) is after the agenda horizon. Example, `area/cbt/CBT Tracker.md:9` in the human's notes root, on 2026-10-19:
  `- [.] 2026 Q4 #cbt 📅 2026-11-24 Tue 🛫 2026-10-09 Fri`
  `meta-notes tasks --ready` finds it; the agenda doesn't. Emoji order is not the cause.
- The cause is `agenda()` in `scripts/meta_notes/query.py`: a task with a due date past `end` is dropped (`continue`) before its start date is checked. `_is_ready()` in `find_tasks.py` checks the due date and the start date independently.
- Suggested fix: when the due date is after the horizon and the start date is on or before today, put the task under Today instead of dropping it.

Note: the current behaviour is documented. `agenda()`'s docstring says "a started task due after the horizon is left out" (from 6eb423e, mn-kbfa, 2.25.0). The attachment asks whether a flag would be better. The human asked for the fix in the next version, so change the default and update the docstring, the `:help` text and the specs to match. Don't add a flag.

Verify: a test where a task started before today and due after the horizon shows under Today in `--agenda` (text and `--json`), and a task not yet started and due after the horizon stays out. `just check` must be green.
