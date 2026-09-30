---
id: specs
severity: must
roles: [manager, worker]
---
Behaviour is specified in `design/specs/<capability>.md`. A task that
changes behaviour edits that spec directly, on the worker's branch, in the
same branch as the code and tests. The branch diff is the spec delta, and
the manager's merge is what makes it current.

- Grammar: `### Requirement: <name> {#r-xxxx}` with a SHALL statement, then
  `#### Scenario: <name> {#s-xxxx}`, a `*Verification*: **executable**` or
  `**non-executable**` line, and `- **WHEN** ...` / `- **THEN** ...` bullets.
  Run `bridle spec id` to give new headings ids; never edit or reuse one.
  A new capability gets a new `design/specs/<capability>.md` with a
  `## Purpose` and `## Requirements`. Every scenario is `non-executable`
  for now (none is bound to a test); `bridle spec check --require-ids` is
  part of the check command.
- Don't use the OpenSpec CLI, and don't create `openspec/changes/`
  directories. `openspec/changes/archive/` is history; leave it alone.

Why: bridle tasks replace OpenSpec's proposal and change lifecycle, but the
specs stay the record of how meta-notes behaves.
