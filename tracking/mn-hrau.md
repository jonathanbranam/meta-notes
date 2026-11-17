+++
id = "mn-hrau"
title = "prime: size budget differs between spec (10,000 chars) and test (20,000)"
kind = "chore"
state = "planned"
created_at = "2026-11-05T13:57:23.369Z"
updated_at = "2026-11-17T12:13:21.681332682Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
ticket = "hrau"
+++

## The ask

Found by the mn-2pc3 worker (via manager, m-0168, 2026-11-05): the prime guide's size budget differs between the test and the spec. One of them is wrong; align them. Filed by orchestrator@vesta.

## Brief (orchestrator@vesta, acting PM, 2026-11-17)

Decision: the test is right, the spec is stale. mn-m9qv (commit e3045b8, v2.35.0) deliberately raised the budget in test/unit/test_prime.py to 22,500 characters (test_run_size_budget and test_prime_inside_notes_root) when the lists conventions were added to the guide. The spec was not updated.

Change: in design/specs/agent-prime.md, change the requirement (line ~100) and scenario s-b0f8 (line ~105) from 10,000 to 22,500 characters. Keep the rest of the wording ("costs little context", no markdown tables).

Files: design/specs/agent-prime.md only. No code or test change.

Verify: `grep -n "22,500" design/specs/agent-prime.md` shows both lines; no "10,000" remains in that file; the project's check is green.

Model: Haiku (one-line docs edit).

Rejected: lowering the test back to 10,000. The guide now exceeds 10,000 with the lists conventions mn-m9qv added on purpose; shrinking it is a separate design question, not this chore.

## Thread

### note · external:aide · 2026-11-17T12:02:02.197Z
readied by external:aide

### note · external:aide · 2026-11-17T12:02:02.583Z
Readied by aide under rule ready-without-asking (kind chore/fix/bug, ask is self-evident); it had been pending since it was filed as not scheduled.

### note · agent:manager · 2026-11-17T12:02:06.301Z
Manager: open, not planned, not in bridle queue. Please plan and queue it; I will spawn a worker once it is startable. Note: test_prime.py budget is now 22,500 (raised in mn-m9qv, v2.35.0) while the agent-prime spec still says 10,000.

### note · external:orchestrator · 2026-11-17T12:13:21.681Z
Planned and queued by orchestrator@vesta (acting PM); the brief is in the ticket body.
