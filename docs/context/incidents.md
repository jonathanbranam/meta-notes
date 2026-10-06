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

## 2026-10-06 17:00: conventions say `no plan` unstruck; the human wants `~no plan~`

- **What happened:** the human, installing on the work computer, saw agents
  write `no plan` in Time Block Plan cells not struck out: "that's
  incorrect. It should be struck out with a single tilde." `meta-notes
  conventions` and the time-block and daily-shutdown skills say `no plan`
  "(not struck)", wording added with qb8e (mn-d368, v2.14.x) on 2026-10-03.
  The human's words on qb8e were only about not striking the agent's own
  unapproved plan.
- **Impact:** every `no plan` row written since then is unstruck; one more
  task and release.
- **Cause:** the qb8e brief went beyond the human's words ("not struck"),
  and nobody checked that wording against the quote.
- **Category:** `role`.
- **Follow-up:** ticket xjaq, task mn-xjaq.

## 2026-10-06 14:48: mn-cys2 built and merged inside its settle period

- **What happened:** the orchestrator filed and readied mn-cys2 at 14:48:13
  (settling until 14:53) and told manager-1 "it can go next". The manager
  spawned worker add-under-tasks at once; it reported done at 14:50:19 and
  the manager merged at 14:55:42. The task went `open -> integrated`, never
  planned or claimed. Found by the advisor; the human: "I figured it wasn't
  working here at all which is wasn't."
- **Impact:** the human's two corrections arrived inside the window; the
  first build missed them and was sent back once (a few minutes, one extra
  worker round).
- **Cause:** the daemon checks settling only at ready, the queue and claim;
  `bridle spawn worker` and `bridle task done` don't check task state. The
  orchestrator's "it can go next" read as a go.
- **Category:** `daemon`, `role`.
- **Follow-up:** bridle zta7 (enforce at spawn and done, default 10m,
  skip only for a critical fix). The orchestrator no longer tells the
  manager a task "can go next" while it settles.

## 2026-10-05 11:38: manager couldn't merge mn-cru4 or commit ticket moves (allowlist)

- **What happened:** the manager ran the mn-cru4 merge, push, tag and
  `bridle task done` as one chained command with `git push -q` and
  `git rev-parse`; `dontAsk` denied the whole command because those forms
  aren't on its allowlist (`.bridle/config.toml` `[roles.manager]`). It
  stopped and wrote "Decision for you" in its turn output, which reaches
  nobody, then idled. Earlier, its `git add`/`git commit` of three ticket
  moves (5qab, g8wz, 6dbp) was denied the same way and left uncommitted in
  the shared clone. Found by the orchestrator checking why a finished
  task sat unmerged.
- **Impact:** about 12 minutes' delay on a bug fix; no harm.
- **Cause:** the manager improvised command forms beyond its allowlist, and
  reported the denial in its turn output instead of a message. Ticket
  moves need a commit the manager isn't allowed to make.
- **Category:** `role`, `config`, `coordination`.
- **Follow-up:** merged as plain commands (8a7ebea, v2.24.1); the
  manager's role doc now says to run each git command on its own in the
  exact form shown, and to leave ticket moves to the orchestrator.

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

## 2026-10-05 23:19: cru4 fix hid real tasks in daily notes

- **What happened:** the cru4 fix (v2.24.1, 5205e26) skips every line under
  a daily note's `## Tasks Due Today` and `## Overdue Tasks`. The human also
  writes real tasks there by hand, so `meta-notes tasks` and `--agenda`
  stopped listing them. The notes advisor found it the evening after
  (notes m-0084).
- **Impact:** about 9 real tasks in the personal root invisible since the
  morning, two of them due 2026-10-06. The advisor renamed the heading in
  the 10-05 and 10-06 notes as a workaround; older notes still hidden.
- **Cause:** the cru4 brief and its verification assumed those sections
  held only snapshot copies; nobody checked the real notes for hand-written
  tasks there (the verification counted "2 real tasks" and stopped).
- **Category:** `regression`, `spec`.
- **Follow-up:** rg3v (task mn-hsxc): skip only the `- [[link]]` subtrees.
  The human then rejected the skip itself (2026-10-06 00:12 UTC: "Every place
  a task is listed, it should always show up"): a9h9 (task mn-s36r) removes
  it; the notes advisor cleans the copies out of the notes instead.

## 2026-10-06 00:20: new workers can't run Bash (kill-guard hook, old CLI)

- **What happened:** worker snapshot-revert (mn-s36r) had every Bash call
  refused: its PreToolUse hook runs `bridle kill-guard`, which the NUC's
  installed `bridle` (0.5.0, `~/.cargo/bin`, built 2026-10-05 10:39 UTC)
  doesn't have. It made its edits, then stopped, unable to test or commit.
  The orchestrator's `bridle daemon restart --upgrade` then tried to build
  meta-notes' own commit as bridle and failed (nothing changed).
- **Impact:** every agent spawned now on the NUC can't use Bash; the revert
  stalled about 10 minutes. The manager, spawned earlier, is unaffected.
- **Cause:** version skew between the daemon's agent settings (br-75h2,
  adb4d30f) and the installed CLI; how the 2026-10-01 daemon renders the new
  hook is unknown. The upgrade path uses the project's repo, not bridle's.
- **Category:** `tooling`, `deploy`.
- **Follow-up:** bridle t3vq (hook the CLI lacks), mtdg (upgrade builds the
  wrong repo). The manager finishes mn-s36r itself; the human reinstalls
  bridle on the NUC.
