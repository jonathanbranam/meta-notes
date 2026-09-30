+++
id = "mn-ba09"
title = "Design proposal: recurrence and time of day for tasks and reminders in the meta-notes CLI"
kind = "feature"
state = "integrated"
created_at = "2026-09-30T04:19:24.778Z"
updated_at = "2026-09-30T04:24:39.044345Z"
commit = "0d6c2f8"
summary = "Design proposal only: tickets/recurrence-and-time-of-day.md (merge 0d6c2f8). Recommends Obsidian Tasks recurrence syntax, completion spawning the next occurrence, a separate time-of-day marker, and an --at query; 10 open questions for the human on the thread. Nothing built."
+++

DESIGN PROPOSAL ONLY, nothing is built until the human approves it. Deliverable: a proposal document in tickets/ at the repo root (create the folder; never questions/) on bridle-adopt. Scope: recurring tasks and reminders (e.g. home maintenance) plus exact time of day on tasks and reminders (meta-notes lacks both). A future life-assistant agent will use the CLI on the human's notes repo; recurrence is the main piece it lacks. Model the syntax on the Obsidian Tasks plugin the human likes: every 3 months with a due date (recurrence emoji, then the rule, then the due date 2026-07-01), and 'when done' (next date counts from completion). The human's real examples and current rules are in bridle's ticket /Volumes/Data/work/bridle/bridle/docs/questions/open/a-life-assistant-agent-on-the-notes-repo-phyy.md (read only; do not copy the notes repo). The proposal should cover: syntax, parsing in scripts/tasks.py and task_update.py, what completing an occurrence does, time of day, CLI surface (tasks query, task update), interaction with existing specs, open questions for the human, and a suggested build breakdown. No code, no spec changes, no version bump.

## Thread

### note · agent:recur-design · 2026-09-30T04:24:23.522Z
Proposal written: tickets/recurrence-and-time-of-day.md (branch bridle/recur-design, commit d20ae23). No code, specs or version touched.

Recommendation
- Recurrence: Obsidian syntax as is. 🔁 every [N] day|week|month|year [when done] + 📅. The human's ~130 maintenance lines move over unchanged.
- Completing (task update --status x) on a 🔁 line: marks done, always stamps ✅, inserts the next occurrence as a new open line directly below, in one write. The done line keeps its line number; the new line is at line+1. Result JSON gains `created`. First line-inserting edit in the CLI.
- Next date: from due date, or from completion with `when done`; month ends clamp. Only the transition to done spawns; done-again, cancel, > and reopen don't. New --no-recur, --recur RULE|none, --time HH:MM|none.
- Time of day: separate `⏰ HH:MM` (24h, local) before the first date marker, since it stays Obsidian-safe. Alternative `📅 2026-10-01 15:00` breaks Obsidian's trailing-marker parse. A reminder = a task with ⏰; delivery (phyy Q4) stays outside meta-notes.
- Query: JSON gains time, recurrence, recurs_from_completion; new `--at now|HH:MM` for "what is due now". Untimed tasks are due all day.
- Found: there is no `task done` (it's task update --status x) and no `task add`, which capture will need.

Open questions for the human
1. ⏰ 15:00 or 📅 date 15:00? Still using Obsidian on these notes?
2. Done late (due 07-01, done 10-05): next 10-01 (Obsidian, overdue) or first future date? I'd match Obsidian; I haven't verified your version's behaviour.
3. Always stamp ✅ on recurring lines, even when done on the due date?
4. Next occurrence below or above? Keep done ones in Home Maintenance.md?
5. Recurring lines copied into daily notes: spawn there? I'd keep them in one home note and never copy 🔁.
6. Add `task add` here or separately?
7. Reminder lead time ("1 day before") in v1? I'd say no.
8. Which rules beyond every N days/weeks/months/years and every weekday come first?
9. Should untimed tasks show in `--at` from a morning cutoff?
10. Time zone: the machine's (NUC) local time OK?

Build: 8 steps (rules module, parse/report, time of day, complete-and-spawn, --at, weekday rules, optional task add, read-only migration check on a copy). Risk sits in date arithmetic and the line insert.

### note · agent:manager · 2026-09-30T04:24:36.161Z
Merged the proposal into bridle-adopt (0d6c2f8); tickets/recurrence-and-time-of-day.md. Awaiting the human's answers to the open questions above before any build task is planned. No code, spec or version change.

### note · agent:manager · 2026-09-30T04:24:39.044Z
integrated: 0d6c2f8
