---
id: mn-qh2m
title: "find_tasks --mark-from: copy tasks as [<] 'from' lines so they aren't duplicate tasks; daily templates use it"
kind: feature
created: 2026-11-09
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## The ask

From the human, in the meta-notes aide session, 2026-11-09 (~9:30-10:00 AM ET). Approved: "Yes" to filing with the status name "from" and the option `--mark-from`.

## The problem, the human's words (verbatim excerpts)

> When building a daily note, in particular, when I'm running the find tasks script that gets run from the daily note template, what it does now is copy the task over, which feels like the right solution. But then we get task duplicates everywhere, and they're a pain to clean up.

> The overriding goal here is: I do like copying these in because they give me a clear list of the things that need to be done. I do want to retain somehow the indicators of start and due dates, so I don't have to look them up every time. I don't want to have these parse as actual tasks as if they were created today.

> My first thought is a less-than sign, and that means this came from somewhere else. A greater-than sign means this was copied to somewhere else.

Rejected by the human: ignoring a heading in the daily note during task search:

> I'm not a fan of it because I don't really like having that special thing ignored. My concern is that I would go type something in there, or some script or some agent or somebody would enter something in there. Then it would get overlooked

On scope:

> I don't think we necessarily need any automation for this. [...] Probably we could write something that would look up the file name, find this actual original task by the name, and then check them both off. That's really not necessary for the first version of this ticket.

> This needs to be an option for fine [find] tasks, not the only way it works, right? If I'm just calling fine tasks by myself and I want to, I think it should retain the current behavior. This would be a CLI option, something that we can set inside of the template so that it's called properly there.

> I like "from" as the name of the marker. It isn't a duplicate marker (eg like in jira).

## What to build (agreed with the human)

1. **New task status `<`, named "from"**: a copy of a task that lives elsewhere. Pairs with `>` (rescheduled: moved *to* another note).
   - `scripts/tasks.py` `STATUS_CHARS` knows `<` (today any unknown char reads as open, so `[<]` would still be a duplicate open task).
   - Task queries skip `<` lines the way they skip `>` lines: not in `--overdue`, `--due`, `--agenda`, etc. `--json` reports `"status": "from"`.
   - `meta-notes task update --status '<'` accepts it.
   - Vim syntax highlights `[<]` (after/syntax/markdown.vim).
   - conventions.md: a line beside "Carrying a task forward": `[<]` from = a copy of a task that lives elsewhere; `[>]` = the original moved away.
2. **`find_tasks.py --mark-from`**: writes each copied task line with `[<]` instead of its status box. Everything else unchanged: the text, 📅/🛫/⏰ dates, the `[[source note]]` line in `--condensed`. **Without the option, output is exactly as today.**
3. **Shipped templates use it**: the Due and Overdue `find_tasks.py` calls in `templates/daily.md` and `templates/daily-personal.md` get `--mark-from`.
4. **Marking a copy done is manual**: the human changes `<` to `x` (or `-`). Nothing else happens; the original stays open where it lives.

## Not in this version
- Completing a `[<]` copy does not close the original. Possible follow-up: find the original by the `[[source note]]` link and the task text, refuse if it changed (like `meta-notes list check` with `--source`, v2.35.0).

## Notes for the planner (told to the human)
- A copy marked `x` becomes an ordinary done task: out of open lists, as wanted, but it appears beside the original in views that include done tasks (`tasks --status all`, weekly completed work). Accepted.
- `init` doesn't overwrite a root's existing `resource/template/daily*.md` without `--force` (which also rebuilds `.venv`). CHANGELOG should say to add `--mark-from` to those two lines by hand in existing roots.
- Specs, tests (unit for status + flag; template fixture renderings in test/fixtures/templates), version bump, CHANGELOG.
