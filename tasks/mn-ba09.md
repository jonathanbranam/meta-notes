+++
id = "mn-ba09"
title = "Recurrence: recurring tasks and reminders (e.g. home maintenance) in the meta-notes CLI"
kind = "feature"
state = "open"
created_at = "2026-09-30T04:19:24.778Z"
updated_at = "2026-09-30T04:19:24.778Z"
+++

From the human via orchestrator. Add recurrence to the meta-notes CLI: recurring tasks and reminders, for example home maintenance (every 6 months, first of the month). A future life-assistant agent will use the CLI on the human's notes repo (bridle ticket phyy); recurrence is the main piece it lacks. Design-heavy: needs a spec first (rules: specs, versioning, languages), recurrence syntax compatible with the existing task line format (see the tasks spec and task_update.py, and any Obsidian-Tasks-style recurrence already parsed), and how completing an occurrence creates the next. No priority given by the human; left open, not planned, until sized and prioritised.
