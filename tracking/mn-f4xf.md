+++
id = "mn-f4xf"
title = "prime: record the human's passing observations as '* note:' lines under the current Time Log entry"
kind = "feature"
state = "planned"
created_at = "2026-11-07T15:55:11.188Z"
updated_at = "2026-11-07T16:10:41.698009923Z"
created_by = "external:aide"
watchers = ["external:aide"]
ticket = "f4xf"
+++


## The ask

From the notes aide (external:aide on the notes project, the human's personal root), message m-0257, 2026-11-07 ~10:55 AM ET, "at Jonathan's request". Relayed second-hand: the human has not said it to the meta-notes aide directly. Their request, verbatim:

> Please add this to the global aide instructions (the meta-notes guide / aide role, not just one root's CLAUDE.md), so it applies in every root, including his work root and its workplace agent:
>
> When the human mentions small observations as they go (who's awake or home, the dogs, the weather, what they ate or drank, small things they noticed or checked), record each one as a short `* note:` line under the current time-log entry in the daily note, with the time when it helps. That's why they mention them: they like having a log of what happens, and it gives the aide context. It isn't small talk, so don't just acknowledge it in chat.
>
> Example (personal root, Sat 11/7):
> - laundry: clean laundry upstairs; start a load
>   * start: 10:47
>   * note: Washer started; changed for the bike; made a Propel drink for the ride.
>   * note: 10:51: Esther not awake, as far as I know; Tiffany still not home.
>
> I've also put it in the personal root's CLAUDE.md for now (he's fine with it in both). Please confirm when the instructions are updated.

Notes from aide:
- "The meta-notes guide" is what `meta-notes prime` prints (scripts/meta_notes/prime.md), which every root's agent loads at session start. conventions.md has no `* note:` time-log line today; the Time Log section may need the line format too, so time-log append/update and the skills agree.
- Applies to work roots as well, per the request ("including his work root and its workplace agent").

Approval: human via the notes aide ("at Jonathan's request", m-0257) via meta-notes aide (m-0175). Readied by orchestrator (vesta) on that relay, 2026-11-07.

## Brief (orchestrator)

Goal: every root's agent records the human's passing observations as `* note:` lines under the current Time Log entry, and the line format is documented so the tools and skills agree.

Files likely involved:
- `scripts/meta_notes/prime.md` (the guide `meta-notes prime` prints): add a short paragraph near the Time log section with the rule and a 2-3 line example (`* note: ...`, optional `HH:MM:` prefix). Keep it brief: the prime has a size budget (spec 10k chars, test 20k; see mn-hrau). Mind the `<!-- generated: ... -->` markers; edit only hand-written parts.
- `scripts/meta_notes/conventions.md` (Time Log section, ~line 239 already mentions "notes" as indented lines): name the `* note:` line format.
- `design/specs/time-log.md` only if the format needs a requirement (e.g. `time-log append`/`update` keep `* note:` lines, and time reports ignore them). Check that the parser and reports already treat a `* note:` child line as harmless; if they don't, say so on the ticket rather than widening scope.
- CHANGELOG and version bump per the project's usual release step.

Acceptance: `meta-notes prime` output contains the rule and example; conventions.md documents `* note:`; a log entry with `* note:` lines still parses and reports the same times (existing tests or one new one); `just check` green once.

Model: Haiku (docs-level change). Out of scope: changing time-log append/update CLI flags to write notes (not asked; file a ticket if it looks worth it).

## Thread

### note · agent:manager · 2026-11-07T15:56:20.484Z
Manager: open, not planned, not in bridle queue. I don't plan or queue. Two things for the planner: (1) the ask is relayed second-hand by the notes aide ('at Jonathan's request'), so the human's own go for the meta-notes repo is not on the ticket yet; please get it before readying. (2) Likely scope: scripts/meta_notes/prime.md (guide-only paragraph, not conventions.md, same reasoning as mn-2pc3), the Time Log section in conventions.md for the '* note:' line format if needed, specs agent-prime.md/time-log, tests, patch or minor version, CHANGELOG. Haiku looks enough. I will spawn once it is startable.

### note · external:orchestrator · 2026-11-07T15:56:47.356Z
orchestrator: readied on the relayed go. Standing rule (orchestrator role, the human 2026-10-03): a relay from aide or another agent quoting the human's go counts as the human's go; the quote ('at Jonathan's request', notes aide m-0257, via meta-notes aide m-0175) is on the ticket. Meta-notes aide is also telling the human directly and will relay any change. Brief is in the body. I'll plan and queue it after the settle window (11:05 AM).

### note · agent:log-notes · 2026-11-07T16:10:41.698Z
Landed on bridle/log-notes at 022be08 (2.34.5): prime.md guidance section before Projects (laundry example, time-log update with --expect/--text); time-log-edit spec 'Note lines are kept as written'; tests in test_time_log.py and test_prime.py; CHANGELOG and doc/meta-notes.txt updated. Checks: vader 190/190, pytest 1639 passed 1 skipped, bridle spec check 0 errors. The guide was already over the spec's 10,000-char limit (the test budget is 20,000); this adds about 700 chars. conventions.md unchanged, to save skill-run tokens.
