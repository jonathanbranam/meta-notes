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
tasks: []
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
