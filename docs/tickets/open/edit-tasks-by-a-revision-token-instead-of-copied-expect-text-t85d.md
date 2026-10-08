---
id: t85d
title: Edit tasks by a revision token instead of copied --expect text
kind: question
opened: 2026-10-08
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [zk5p]
tasks: []
---

## The ask

For discussion, not approved. From the human, via the notes advisor
(2026-10-08), after the expect-guard incident (see the guard hook ticket):
"--expect is working against the natural way agents write these", and
"this wouldn't happen as easily in a database". They are considering
blocking agents' read access to notes so every edit goes through the CLI,
but that is a lot of work.

The advisor's suggestion: optimistic concurrency like an ETag. `tasks
--json` (and `task show`) returns a per-task revision token (a hash of the
line and the file's revision); `task update` takes `--rev <token>` instead
of copied text. A token can't be produced by sed at write time, and a stale
one is refused. Possibly stable task ids too.

Questions for the human:
1. Revision tokens alongside `--expect`, or replacing it?
2. Stable task ids (written into the line) now, or later?
3. Is blocking read access still on the table, or does a token make it
   unnecessary?

## The human, 2026-10-08 (via the notes advisor, relayed by the meta-notes aide as m-0717)

On blocking read access:

> when I say blocking read access, obviously there would still be a way
> to read, but the reading and writing would all go through the CLI, and
> that would prevent some of these manipulations, because sed would just
> not work.

On fixing it with an agent rule:

> I'm not sure I want that rule yet ... it's also going to depend on the
> agent following the rule, which I am not convinced is the right way to
> fix this.

> I want to continue to explore this with that ticket instead of making a
> quick change ... The problem with the rule is it only fixes it in this
> bridle repo, and I need this fixed in meta notes. Also for my work repo,
> which doesn't use bridle at all.

So the fix has to live in meta-notes itself and work in a notes root
without bridle; an agent rule (or a bridle-only hook) isn't the fix. The
notes rule `expect-what-you-read` was reverted at the human's request.

## The human, 2026-10-08: no Claude Code hooks (via the notes advisor, m-0720)

> I cannot use Claude Code hooks at work. So that is not a viable
> solution for me. So that is not ready to work. Do not implement that.

Constraint: no Claude Code hooks. The fix has to live in the meta-notes
CLI itself and work in a notes root without bridle. zk5p (the guard hook)
is not to be implemented.
