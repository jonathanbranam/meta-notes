---
id: 286n
title: The time report's Work vs Non-Work disagrees with its work duration
opened: 2026-10-01
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
---

# The time report's Work vs Non-Work disagrees with its work duration

## What happens

`meta-notes time --date 2026-10-01` on the human's notes (meta-notes 2.6.0)
reports, for one day:

- `### Total Time`: work duration 5 hr 46 min.
- `### Work vs Non-Work`: Work time 0m, Total logged 45m, Work percentage
  0.0%.

The log had two untagged `Work` entries, one `#personal` entry, and three
`#2026-10-ny` entries. The notes advisor found it (notes daemon, m-0012).

## Why

The two sections use different rules.

- **work duration** (`calculate_work_window`, `scripts/time_tracking.py`)
  counts every entry in the work window that has none of `NON_WORK_TAGS`
  (`#personal`, `#off-task`, `#break`).
- **Work vs Non-Work** (`calculate_work_vs_nonwork`, same file) still uses
  the hard-coded lists from the first implementation (88c6e93): work only
  with `#mtg`, `#dev`, `#admin`, `#meeting`, `#code`, `#coding`,
  `#administrative`; non-work only with `#pers`, `#break`, `#personal`.
  Anything else, untagged entries included, isn't counted at all.

The human doesn't use those work tags, so the section is always wrong for
them.

## Fix

Make `calculate_work_vs_nonwork` use the same rule as work duration: an
entry is non-work when it has any of `NON_WORK_TAGS` (after alias
normalization), work otherwise. Every timed entry counts, so Total logged is
the sum of all timed entries. Drop the hard-coded tag lists. Applies to the
day report and to the period report and `--json` wherever they use it.

Not in scope: whether a trip's project tag (`#2026-10-ny`) should count as
work. Both sections will count it as work; that's a separate question for
the human.

## Done means

For the day above, Work vs Non-Work shows Work 5 hr 46 min, Non-work 45 min,
Total logged 6 hr 31 min, matching Total Time. Unit tests cover untagged,
`NON_WORK_TAGS` and alias entries. It changes CLI output, so a patch
version bump (`.bridle/rules/versioning.md`).
