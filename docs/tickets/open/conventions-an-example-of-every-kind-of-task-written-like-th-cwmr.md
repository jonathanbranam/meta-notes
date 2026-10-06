---
id: cwmr
title: "Conventions: an example of every kind of task, written like the human's"
kind: feature
opened: 2026-10-06
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: []
---

## The ask

# Conventions: an example of every kind of task, written like the human's

The human, 2026-10-06 (to the orchestrator, directly):

> I've had this task pointed out as a bug by multiple agents. It just
> didn't appear. I was looking at the rules, and it's spelled out in the
> words, but the examples don't include an example that demonstrates
> this. I think what I want to see in the Markdown, at the beginning under
> Tasks, is examples of each kind of thing. Also, the example tasks have
> sentence capitalization. Remove that. I don't want sentence
> capitalization, and add project tags as well to those. Basically, they
> all look like the tasks that I write.

> One design change: if a recurring task is done on the exact date it was
> planned on, let's drop the green check as well. That's not necessary.

> Add the tags to the beginning of the passage. I do that pretty often
> because it helps order it visually.

Also asked: rescheduled (`>`) and an indented list with partial
completion. Pending the human's review of the block below; no task yet.

## Proposed block (Tasks section, replacing the current example)

```markdown
- [ ] #kitchen order tiles 📅 2026-09-28
- [ ] #kitchen #next call Sam about the quote ⏰ 15:00 📅 2026-09-28
- [ ] #make-bread buy a banneton 📅
- [ ] #2026-10-ny book flights 🛫 2026-09-21 📅 2026-09-30
- [x] #kitchen call the plumber 📅 2026-09-22 ✅ 2026-09-23
- [x] #2026-10-ny reserve parking at IND 📅 2026-09-22
- [x] #kitchen measure the backsplash 📅 ✅ 2026-09-22
- [ ] change the water filter 🔁 every 3 months 📅 2026-12-22
- [x] change the water filter 🔁 every 3 months 📅 2026-09-22
- [ ] check the softener salt 🔁 every week when done 📅 2026-10-01
- [x] check the softener salt 🔁 every week when done 📅 2026-09-22 ✅ 2026-09-24
- [>] #school order school photos 📅 2026-09-22
- [-] #kitchen tile the floor 📅 2026-09-30
- [o] #2026-10-ny pack for the trip 📅 2026-09-30
  - [x] pack the carry-on 📅 2026-09-29
  - [x] print the boarding passes 📅 2026-09-29
  - [ ] charge the headphones 📅 2026-09-30
- [ ] pack the carry-on
```

A numbered key follows it: open dated; time and `#next` (proper names
keep capitals); undated; start date; done late (✅); done on its due date
(no ✅); done undated (`📅 ✅`); recurring next occurrence (added above);
recurring done on its due date (no ✅, the design change); `when done`
next; `when done` done late (✅, the completion date sets the next one);
rescheduled; cancelled; partial parent (2 of 3 gives `o`, the CLI sets
it); checklist item (no date, not a task). Lines fit 80 columns (the
`when done` done line is 82 with emoji as two: shorten the text).

## Change

- `scripts/meta_notes/conventions.md`: the block and key; lowercase every
  other example task in the file, tags first.
- `scripts/meta_notes/task_update.py`: a recurring task (not `when done`)
  completed on its due date gets no ✅; update the "Recurring lines always
  get ✅" text and the `--no-completed` error to match.
- Open question: should `task add --tag` put tags first? The
  orchestrator recommends yes.
- Tests, patch or minor version bump.
