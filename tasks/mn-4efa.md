+++
id = "mn-4efa"
title = "Move development from pipenv to uv and pyproject.toml"
kind = "chore"
state = "planned"
created_at = "2026-09-30T20:26:39.195Z"
updated_at = "2026-09-30T20:26:40.040720227Z"
size = "M"
+++

Ticket: docs/tickets/open/pipenv-to-uv-and-pyproject-s34j.md (read Decisions and Plan; approved). pyproject.toml (requires-python >=3.11, runtime deps, dev group, [tool.uv] package = false), uv.lock committed, .python-version 3.11, Pipfile and Pipfile.lock removed. requirements.txt stays for init and is generated from uv.lock with uv export; a unit test fails when it's stale. Replace 'pipenv run pytest' with 'uv run pytest' in .bridle/config.toml check =, .bridle/roles, .bridle/rules (languages.md: development on 3.11), AGENTS.md, docs/gherkin-compiler-testing.md; leave openspec/changes/archive alone. Check: ./run_tests.sh && uv run pytest test/unit/ pass on 3.11; meta-notes init in a scratch root still builds .venv from requirements.txt. Report any test that fails only on 3.11. No version bump.
