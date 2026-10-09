---
id: psgg
title: Ship a CHANGELOG for users, updated with every version bump
kind: feature
opened: 2026-10-09
filed_by: external:aide
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: [mn-psgg]
---

## The ask

The human, 2026-10-08 (to the meta-notes aide):

> Thx. Do we ship a CHANGELOG? We should start doing that for users.

We don't: no CHANGELOG, NEWS or release notes in the repo. Versions are
tracked only by `__version__` and tags (84 so far, v0.1.0 to v2.30.0),
per `.bridle/rules/versioning.md`.

Proposed (the aide; for the orchestrator to refine):

- `CHANGELOG.md` at the repo root, newest first, one section per version
  (`## 2.30.0 - 2026-10-08`), grouped Added / Changed / Fixed, written
  for users of the plugin and CLI (what changed for them, and anything
  they need to do, e.g. "replace `downloads` and `downloads_pattern` with
  one `downloads` setting"), not commit messages.
- The worker adds the entry in the same commit as the version bump, so
  the rule in `versioning.md` gains one line and a manager checks it on
  review. Docs-only changes don't get an entry, same as the version.
- README points to it; `meta-notes --version` could mention it.
- Open for the human: backfill. Start at the next version, or backfill
  2.x (or everything) from tags and merge messages. Aide's recommendation:
  a one-time short backfill of the 2.x minor versions, one line each, so
  recent changes (outlook, calendar downloads, recurrence) are findable.

## The human's answers, 2026-10-08 (to the meta-notes aide)

> It should include new functionality and changes to options and
> existing functionality.
>
> I think backfill but how far? Idk how far back 2.0 is but that sounds
> fine.

So: entries cover new functionality, and changes to options and to
existing behaviour (fixes too, where a user would notice). Backfill from
v2.0.0 (2026-09-30; 60 tags, v2.0.0 to v2.30.0), from the tags and merge
messages, one entry per version. Earlier versions (v0.1.0 2026-09-25 to
v1.x) aren't backfilled. Ready for a task.

The human, confirming the audience: "As you said - user facing things". Entries describe what a user of the plugin and CLI sees or must do; internal changes (tests, refactors, agent/bridle workflow, specs) stay out.
