---
id: mn-h7fb
title: "skills: skip re-running meta-notes conventions when it's already loaded this session"
kind: chore
created: 2026-11-05
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## The ask

From the human by email (m-0195, 2026-11-05, subject "More bug reports to investigate"), filed from the work laptop. The human wrote, verbatim: "More bug reports to investigate and fix." The attachment follows verbatim.

Notes from aide: Low priority by the human's own note (a nice-to-have for multi-skill sessions). Touches every skill's Start step (checkin, daily-plan, daily-shutdown, project-review, task-cleanup, time-block, weekly-plan, weekly-review); overlaps the files mn-8xfd edits.

---

# project/meta-notes/skills should allow skipping conventions if already loaded

For the meta-notes plugin maintainer. Filed as an issue against the
skills in `skills/*/SKILL.md` in the plugin repo (every skill's "Start"
step that says to run `meta-notes conventions`) — nothing in this notes
repo should be edited to work around it.

## Problem

Every skill's Start section says something like:

> Run `meta-notes conventions` and follow it for everything below.

unconditionally. `meta-notes conventions` prints a long document (tasks,
tags, projects, subtasks, editing tasks, time block, time log, adding
lines, carrying tasks forward, ceremony markers, notes/structure — see
[[project/meta-notes/prime should say not to use host auto-memory]] for
how it relates to `meta-notes prime`). When several skills run in one
session (for example `daily-plan` then `weekly-plan`, as happened
today), the unconditional wording has the assistant re-run and
re-ingest that same long document again for the second skill, even
though it already has the identical text in context from the first
run minutes earlier. That's pure waste: no new information, just
burned context/tokens for a repeat read.

This session, I (the assistant) judged on my own that this was
redundant and skipped re-running `meta-notes conventions` for the
second skill (`weekly-plan`) since I already had its output in
context. That was the right call, but it was my own inference, not
something the skill text licensed — a stricter reading of "Run ... and
follow it" could reasonably re-run it every time, and another assistant
(or a future me, less confident about reusing context) might not make
the same judgment call.

## Priority note

This only wastes tokens when two or more skills run in the same
session (context not yet cleared between them) — the user reports
that's relatively rare for them; most sessions invoke only one skill
before a clear. So this is a nice-to-have cleanup for multi-skill
sessions, not an urgent fix: the 270-line conventions document is
genuinely useful to have loaded, it's only the *repeat* load within
one session that's wasted.

## Requested rule

Make the allowance explicit in each skill's Start step: only run
`meta-notes conventions` if it hasn't already been loaded earlier in
the current session; otherwise just follow what's already in context.

## Suggested change

In each skill's Start section, replace the unconditional instruction
with something like:

> If you already ran `meta-notes conventions` earlier in this session,
> skip re-running it and follow what you already have. Otherwise, run
> `meta-notes conventions` and follow it for everything below.

This mirrors how CLAUDE.md's own `meta-notes prime` instruction only
needs to fire once per session, not once per skill invocation.


---

## Plan (orchestrator@vesta, acting PM, 2026-11-05)

Haiku. Low priority (the human's note). Blocked by mn-8xfd and mn-n7bd: it
edits the Start step of every skill, including the files those two change.

**Change:** in each skill's Start step that runs `meta-notes conventions`,
use the suggested wording: skip re-running it if it was already run earlier
in this session; otherwise run it and follow it. Skills: calendar, checkin,
daily-plan, daily-shutdown, project-review, task-cleanup, time-block,
weekly-plan, weekly-review (all nine `skills/*/SKILL.md` that call it).

**Files:** those nine SKILL.md files; design/specs/ceremony-skills.md only
if a scenario asserts the unconditional wording; `__version__` (PATCH) and
CHANGELOG.md per .bridle/rules/versioning.md.

**Verify:** usual check green; `grep -n "meta-notes conventions"
skills/*/SKILL.md` shows the conditional wording in all nine.
