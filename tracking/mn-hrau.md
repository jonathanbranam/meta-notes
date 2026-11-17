+++
id = "mn-hrau"
title = "prime: size budget differs between spec (10,000 chars) and test (20,000)"
kind = "chore"
state = "open"
created_at = "2026-11-05T13:57:23.369Z"
updated_at = "2026-11-17T12:02:06.301843539Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
ticket = "hrau"
+++

docs/tickets/open/prime-size-budget-differs-between-spec-10-000-chars-and-test-hrau.md

## Thread

### note · external:aide · 2026-11-17T12:02:02.197Z
readied by external:aide

### note · external:aide · 2026-11-17T12:02:02.583Z
Readied by aide under rule ready-without-asking (kind chore/fix/bug, ask is self-evident); it had been pending since it was filed as not scheduled.

### note · agent:manager · 2026-11-17T12:02:06.301Z
Manager: open, not planned, not in bridle queue. Please plan and queue it; I will spawn a worker once it is startable. Note: test_prime.py budget is now 22,500 (raised in mn-m9qv, v2.35.0) while the agent-prime spec still says 10,000.
