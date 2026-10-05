# Incidents

A running log of every failure or problem we find, so patterns show up and
we learn from them: something the human reports to the orchestrator or an
advisor, or anything a role discovers (a crash, a stall, a red `main`, a bad
merge, work that sat stuck, a role that did the wrong thing). The human
approved this log for meta-notes on 2026-10-03; the format is bridle's
`docs/context/incidents.md`.

This is a record, not a to-do list. Work that comes out of an incident is a
ticket or task, linked from the entry.

Newest first. Times are UTC. Each entry has:

- **What happened** and when, and how it was found.
- **Impact:** what it cost (time, work, money, trust).
- **Cause:** the root cause, or "unknown".
- **Category:** one or more of `connectivity`, `host`, `daemon`, `ci`,
  `merge`, `coordination` (work stuck or dropped between roles), `role` (a
  role or prompt did the wrong thing), `config`, `external`,
  `human-process`.
- **Follow-up:** the ticket or task, or "none" and why.

## 2026-10-05 02:15: meta-notes-ui workers couldn't spawn (worktree setup)

- **What happened:** the first worker for mu-83ya (meta-notes-ui v1.1)
  failed to spawn: the orchestrator's scaffold set `[worktrees] setup =
  "npm ci"` in a repo with no `package.json` yet. The manager asked the
  human (m-0005) to approve a fix. Found by the orchestrator from the
  manager's note.
- **Impact:** about 2 minutes, and one question in the human's inbox that
  the orchestrator answered.
- **Cause:** the orchestrator wrote config for the repo's future state,
  not its current one.
- **Category:** `config`.
- **Follow-up:** fixed in meta-notes-ui f85fcc5 (`test ! -f
  package-lock.json || npm ci`), daemon restarted. None further.

## 2026-10-03 23:03: v2.14.2 merged with the rule worded wrong

- **What happened:** mn-d368 (ticket qb8e) added the rule for an agent's
  unapproved plan that didn't happen. The worker wrote "clear the Plan
  (leave it empty) and set it to `no plan` in Actual" in `conventions.md`,
  and a self-contradicting line in `skills/time-block/SKILL.md`; the ticket
  said the Plan becomes `no plan`. The manager merged and tagged it.
  Found by the orchestrator reading the merged diff.
- **Impact:** a wrong instruction shipped in `meta-notes conventions` for
  about three minutes; one extra task and release (v2.14.3). No notes were
  edited with it.
- **Cause:** the worker (haiku, chosen by the manager for a docs-only task)
  misread the ticket; the manager's review checked the tests, not the text,
  and docs changes have no test that would catch it.
- **Category:** `role`, `merge`.
- **Follow-up:** fixed by mn-8f5e (ticket xq4q, v2.14.3). The orchestrator
  reads every merged skill or conventions diff.

## 2026-10-03 23:02: worker skipped the version bump as "docs-only"

- **What happened:** the same worker didn't bump the version, calling the
  change docs-only under `.bridle/rules/versioning.md`. Skills and
  `conventions.md` are shipped behaviour (`meta-notes conventions` prints
  it); the earlier tilde rule (bmen) got v2.12.4 the same way. Found by the
  orchestrator in the worker's log.
- **Impact:** small: one message to the manager; the bump was added before
  the merge (v2.14.2).
- **Cause:** the versioning rule says "changes to only docs ... don't bump
  it" and doesn't say that skills and the conventions text count as
  behaviour.
- **Category:** `role`.
- **Follow-up:** none yet; candidate: one line in the versioning rule naming
  `skills/`, `conventions.md` and `prime.md` as behaviour.

## 2026-10-03 22:20: worker reported done to the human, not the manager

- **What happened:** the worker on mn-d368 finished at about 22:20 and sent
  its "done" first to `agent` and then to `human`, not to the manager that
  gave it the task. The manager never heard, and the task sat finished but
  unmerged for about 40 minutes. Found by the orchestrator at 23:02 when a
  1-turn idle worker and an open task didn't add up; `bridle agent logs`.
- **Impact:** about 40 minutes' delay; a routine note in the human's inbox,
  which is only for what they must act on.
- **Cause:** the worker (haiku) didn't follow `.bridle/roles/worker.md`
  ("Report to whoever gave you the task (the sender in its message
  header)"); it couldn't find the sender in its inbox and guessed.
- **Category:** `role`, `coordination`.
- **Follow-up:** none yet. Watch for it again with haiku workers; if it
  recurs, the manager should use sonnet for workers or name the report
  target in the task message.

## 2026-10-05 02:41: meta-notes-ui main red for 40 minutes, 9 merges on red

- **What happened:** mu-d66x (97e0b13) added `server/example.test.ts`, the
  first test that runs the real `meta-notes` CLI. GitHub CI has no
  meta-notes, so it failed (`spawn meta-notes ENOENT`) and stayed red
  through df5f90d: 13 red pushes, 9 merges (v0.3.0 to v0.5.0). The daemon
  recorded one `ci.completed` (df5f90d, 03:20 UTC) and woke the
  orchestrator only then. The orchestrator saw CI "in progress" on 97e0b13
  and never re-checked.
- **Impact:** main red for about 40 minutes; nine merges broke the rule
  "never merge while main is red"; no product harm (local checks passed).
- **Cause:** test needing an external CLI with no CI setup for it; the
  meta-notes-ui manager can't read CI (its allowlist denies `gh`) and relied
  on wakes; the daemon's CI watch missed the earlier runs (cause unknown).
- **Category:** `ci`, `coordination`, `tooling`.
- **Follow-up:** CI fixed in ab00d7b (workflow checks out meta-notes,
  Python 3.11, `bin/` on PATH; green at 03:27 UTC, run 37259312840); bridle
  br-ysmu (missed CI events; a way for managers to read CI without gh).
  The manager then merged mu-qcn9 (dc45078) while CI on ab00d7b was still
  running, before the orchestrator's confirmation; both came out green. Told
  it to wait for confirmation on each merge until br-ysmu is fixed.
