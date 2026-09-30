+++
id = "mn-4efa"
title = "Move development from pipenv to uv and pyproject.toml"
kind = "chore"
state = "integrated"
created_at = "2026-09-30T20:26:39.195Z"
updated_at = "2026-09-30T21:04:19.040051319Z"
size = "M"
branch = "bridle/to-uv"
commit = "15c30e4"
summary = "Development moved from pipenv to uv: pyproject.toml, uv.lock, .python-version 3.11, Pipfile removed; requirements.txt generated with uv export and guarded by test_requirements.py; check is now ./run_tests.sh && uv run pytest test/unit/. No version bump. Merged 15c30e4. Host note: UV_CACHE_DIR is set to a Mac path here, override it for uv."
+++

Ticket: docs/tickets/open/pipenv-to-uv-and-pyproject-s34j.md (read Decisions and Plan; approved). pyproject.toml (requires-python >=3.11, runtime deps, dev group, [tool.uv] package = false), uv.lock committed, .python-version 3.11, Pipfile and Pipfile.lock removed. requirements.txt stays for init and is generated from uv.lock with uv export; a unit test fails when it's stale. Replace 'pipenv run pytest' with 'uv run pytest' in .bridle/config.toml check =, .bridle/roles, .bridle/rules (languages.md: development on 3.11), AGENTS.md, docs/gherkin-compiler-testing.md; leave openspec/changes/archive alone. Check: ./run_tests.sh && uv run pytest test/unit/ pass on 3.11; meta-notes init in a scratch root still builds .venv from requirements.txt. Report any test that fails only on 3.11. No version bump.

## Thread

### note · agent:manager · 2026-09-30T21:04:18.451Z
integrated: 15c30e4 (branch bridle/to-uv)

### note · agent:manager · 2026-09-30T21:04:18.455Z
cleanup: removed nothing
