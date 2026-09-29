+++
id = "mn-fbc0"
title = "Stay-on-task check-ins: a skill plus a sleep-and-return CLI that asks for updates and fills the Time Block's Actual"
kind = "feature"
state = "planned"
created_at = "2026-09-29T03:23:22.014Z"
updated_at = "2026-09-29T03:29:02.775169Z"
size = "L"
+++

From the human, 2026-09-28, via advisor (verbatim):

> for meta-notes, I have an idea that needs some work to start on it: an agent that works similar to bridle orchestrator that helps me stay on task throughout the day; I'm not sure if I have anything in that repo about this; I might; I was thinkigna bout a local app with a localhost and some toast notifications, but I also like the way the bridle orchestrator is on a schedule and knows what is happening and can remind me. So, I was thinking along those lines; but at work I am sandboxes so, no claude hooks or anything; but I think running a job that sleeps and comes back would work fine; it could be a local CLI call that comes back and checks if I'm on task and asks for updates on the work so far
>
> it would help me update my time log "actual" and help me with trouble I have task switching.
>
> Go ahead and write that up as a new skill plus tooling; perhaps just within meta-notes itself since we already ship that?

What it asks for: a new product skill in `skills/` (rule `product-skills`) plus CLI tooling in `bin/meta-notes` / `scripts/meta_notes/` (stdlib Python, rule `languages`), with a spec in `openspec/specs/`.

What already exists (pointers, not decisions):

- `docs/planning-system.md`, "Local dashboard": a localhost dashboard with a quick time-log entry and reminders (browser notifications while the tab is open, a launchd job running `osascript` notifications for the rest). "Sequence" step 7 is "Dashboard with time logging and reminders", not built.
- The daily note's `### Time Block` has Plan and Actual columns (spec `time-log`). `daily-plan` fills Plan; `daily-shutdown` closes the day. Nothing updates Actual during the day.
- `meta-notes ceremony status --json` (spec `ceremony-status`) and `meta-notes prime` give an agent the day's state.
- The "sleeps and comes back" pattern the human likes is bridle's orchestrator watcher (`/Volumes/Data/work/bridle/bridle/scripts/orchestrator-watch.sh`). The agent runs it as a background Bash command, and Claude Code wakes the agent when the command exits. It needs no hooks, which matters because the human's work machine is sandboxed.

## Thread

### note · agent:manager · 2026-09-29T03:24:00.051Z
Plan (manager): one worker, three stages, all on the task thread. (1) Design first: write the spec in openspec/specs/ directly (check-in CLI and skill), read docs/planning-system.md, the time-log and ceremony-status specs, and the bridle orchestrator-watch.sh pattern; no hooks, stdlib Python. Open questions go to the human as a question on this thread (bridle ask); if one blocks the design, park and say so, do not invent. (2) Implement CLI (sleep-and-return command that exits when a check-in is due so the calling agent wakes) plus the skill in skills/ per product-skills, with pytest and docs. (3) MINOR version bump, report on the thread.

### note · external:advisor · 2026-09-29T03:27:02.994Z
From the human, via advisor: "we can ship v1 of this tonight and I can test it tomorrow"

### note · agent:manager · 2026-09-29T03:29:02.775Z
Update from the human via orchestrator: ship a v1 tonight for testing tomorrow. Do not let open design questions block: pick sensible defaults, write them in the spec, and list them in a thread note and your done summary for the human to review in the morning. Ask only if something truly cannot be defaulted.
