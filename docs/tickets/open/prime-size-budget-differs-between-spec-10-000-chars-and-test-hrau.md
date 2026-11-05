---
id: mn-hrau
title: "prime: size budget differs between spec (10,000 chars) and test (20,000)"
kind: chore
created: 2026-11-05
created_by: external:orchestrator
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## The ask

Found by the mn-2pc3 worker (via manager, m-0168, 2026-11-05): test/unit/test_prime.py test_run_size_budget asserts 20,000 characters, while design/specs/agent-prime.md says 10,000. One of them is wrong; align them (decide which budget is intended). Low priority; not scheduled. Filed by orchestrator@vesta.
