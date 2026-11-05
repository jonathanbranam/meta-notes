---
id: mn-2pc3
title: "prime: tell agents not to use host auto-memory; persist in CLAUDE.md or filed issues"
kind: feature
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

Notes from aide: Goes in the guide-only part (scripts/meta_notes/prime.md), not conventions, per the report.

---

# project/meta-notes/prime should say not to use host auto-memory

For the meta-notes plugin maintainer. Filed as an issue against
`meta-notes prime` (and/or its underlying guide text, wherever `meta-notes
prime` sources it in the plugin repo) — nothing in this notes repo should
be edited to work around it.

## Problem

Claude Code (and presumably other assistants) can have their own
persistent cross-session memory system, separate from this notes repo
and from the meta-notes CLI/skills. During this session, I used it to
save a capacity-threshold preference as a "memory" — the user objected:

> what memory? don't use memories!

and clarified the expectation directly:

> I need everything - all the rules and notes - tracked in this git
> repo or in meta-notes skills; update CLAUDE.md here or file bugs to
> update meta-notes skills

`meta-notes prime` is supposed to be the first command run every
session and is meant to establish how the assistant should behave in
this notes root. It currently says nothing about this — an assistant
with its own memory feature has no signal from `prime` telling it not
to use it, so the default behavior (saving a preference to the host's
memory store) silently works against the "everything lives in the git
repo" model this notes root depends on. Preferences saved outside the
repo are invisible to `git log`, don't sync across machines with the
repo, and aren't visible to a human reading the notes.

## Requested rule

Add a line to `meta-notes prime`'s output (or the guide it prints)
telling the assistant: don't use any host-provided persistent
memory/preference-saving feature in this notes root. Everything that
should persist across sessions belongs in one of:

- this root's `CLAUDE.md`, for the user's own standing preferences
- a filed issue under `project/meta-notes/` (see `Home.md`'s issue
  table), for anything that's really a request to change a
  meta-notes skill or the CLI itself

## Suggested change

`meta-notes prime`'s output is `meta-notes conventions`'s content
appended after a `# meta-notes guide` section unique to `prime`. Skills
(`daily-plan` and others) call `meta-notes conventions` directly on
every run, not `prime` — only CLAUDE.md's session-start instruction
calls `prime`. So put the new line in the guide-only portion, not in
conventions: conventions gets re-printed on every single skill
invocation, and this guidance only needs to fire once per session.

Add near the top of the guide text `meta-notes prime` emits (before the
`# meta-notes conventions` section it appends), something like:

> This notes root is the source of truth for anything that should
> persist across sessions. If your assistant has its own
> memory/preference-saving feature, don't use it here — put standing
> preferences in this root's `CLAUDE.md` and skill/CLI bug reports
> under `project/meta-notes/` instead, so everything stays in this git
> repo and visible to a human reading it.


---

## Plan (orchestrator@vesta, acting PM, 2026-11-05)

Haiku. Independent of the other tickets.

**Change:** add the requested paragraph near the top of the guide-only part
of `meta-notes prime` (scripts/meta_notes/prime.md, before the appended
conventions): don't use the assistant's own memory feature in a notes root;
standing preferences go in the root's `CLAUDE.md`, skill or CLI bug
reports go under `project/meta-notes/`. Not in conventions.md (it reprints
on every skill run).

**Files:** scripts/meta_notes/prime.md; design/specs/agent-prime.md (a
requirement/scenario for the line) and any test that asserts prime's
output; `__version__` (PATCH: guide text) and CHANGELOG.md per
.bridle/rules/versioning.md.

**Verify:** usual check green; `meta-notes prime` shows the paragraph
before `# meta-notes conventions`.
