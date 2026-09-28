---
id: versioning
severity: must
roles: [manager, worker]
---
The version is `__version__` in `scripts/meta_notes/__init__.py`, reported by
`meta-notes --version` and `:MetaNotesVersion`.

- **The worker bumps it** in the commit that completes a task that changes
  CLI or plugin behaviour: PATCH for fixes, MINOR for new commands, options
  or behaviour, MAJOR for incompatible CLI changes (once past 1.0). Changes
  to only docs, tests or specs don't bump it.
- **The manager tags** the merge commit `v<version>` after merging that
  branch into the integration branch, and pushes the tag
  (`git push origin v<version>`). Workers never tag.

Why: tags run unbroken from v0.1.0, one per behaviour change. Bumping in the
worker's branch keeps the version with the change it describes; tagging only
after merge means a tag never points at unmerged work.
