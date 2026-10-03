---
id: qh9v
title: "Planning record in the weekly review: daily notes, planned days, no-plan rows, crossed-out plans"
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: [gjf6]
see: [bmen]
tasks: [mn-0a21]
closed: 2026-10-03T14:56:41Z
---

# Planning record in the weekly review

## The ask

The human, 2026-10-03 (relayed by the notes advisor, m-0245), approved for
meta-notes. The weekly review (and a quarterly review later) should "look
back at every day and see: which days I had a daily note; which days I
planned; how many no-plan blocks there were; how many times I had to cross
out the plan and make a new plan." Crossed out = a Plan cell in single
tildes (bmen); no-plan = a Plan cell `no plan` (gjf6). "This isn't really
for punishing, just to help me look back on my week and assess how I'm
doing with planning." Mainly for work.

## Shape

Counting this by reading seven notes is error-prone for an agent, so give
the CLI the counts: per day in a `--date` period, whether the daily note
exists, whether `- [ ] plan complete` is checked (or the Time Block has
any Plan), the number of `no plan` rows and of `~crossed-out~` Plan
cells. Where it lives (a `time-block` subcommand, `ceremony status`, or a
new command) is the worker's call within the spec rules; `--json` as
always. `skills/weekly-review/SKILL.md` reports it in a short, neutral
section.

There's no quarterly-review skill yet; the command taking any `--date`
period is enough for one later. Don't build that skill here.

Minor release (new CLI output).
