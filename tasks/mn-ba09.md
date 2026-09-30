+++
id = "mn-ba09"
title = "Design proposal: recurrence and time of day for tasks and reminders in the meta-notes CLI"
kind = "feature"
state = "planned"
created_at = "2026-09-30T04:19:24.778Z"
updated_at = "2026-09-30T04:22:33.289212Z"
+++

DESIGN PROPOSAL ONLY, nothing is built until the human approves it. Deliverable: a proposal document in tickets/ at the repo root (create the folder; never questions/) on bridle-adopt. Scope: recurring tasks and reminders (e.g. home maintenance) plus exact time of day on tasks and reminders (meta-notes lacks both). A future life-assistant agent will use the CLI on the human's notes repo; recurrence is the main piece it lacks. Model the syntax on the Obsidian Tasks plugin the human likes: every 3 months with a due date (recurrence emoji, then the rule, then the due date 2026-07-01), and 'when done' (next date counts from completion). The human's real examples and current rules are in bridle's ticket /Volumes/Data/work/bridle/bridle/docs/questions/open/a-life-assistant-agent-on-the-notes-repo-phyy.md (read only; do not copy the notes repo). The proposal should cover: syntax, parsing in scripts/tasks.py and task_update.py, what completing an occurrence does, time of day, CLI surface (tasks query, task update), interaction with existing specs, open questions for the human, and a suggested build breakdown. No code, no spec changes, no version bump.
