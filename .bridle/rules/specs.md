---
id: specs
severity: must
roles: [manager, worker]
---
Behaviour is specified in `openspec/specs/<capability>/spec.md`. A task that
changes behaviour edits that spec directly, on the worker's branch, in the
same branch as the code and tests. The branch diff is the spec delta, and
the manager's merge is what makes it current.

- Keep the existing grammar: `### Requirement: <name>` with a SHALL
  statement, then `#### Scenario: <name>` with `- **WHEN** ...` and
  `- **THEN** ...` bullets. A new capability gets a new
  `openspec/specs/<capability>/spec.md` with a `## Purpose` and
  `## Requirements`.
- Don't use the OpenSpec CLI, and don't create `openspec/changes/`
  directories. `openspec/changes/archive/` is history; leave it alone.

Why: bridle tasks replace OpenSpec's proposal and change lifecycle, but the
specs stay the record of how meta-notes behaves.
