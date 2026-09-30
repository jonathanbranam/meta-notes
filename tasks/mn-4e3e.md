+++
id = "mn-4e3e"
title = "GitHub Actions CI for the check"
kind = "chore"
state = "planned"
created_at = "2026-09-30T21:25:36.760Z"
updated_at = "2026-09-30T21:25:37.932182837Z"
size = "S"
+++

Add .github/workflows/ci.yml: on push to main and on pull requests, ubuntu-latest. Install uv (astral-sh/setup-uv) and vim; clone https://github.com/junegunn/vader.vim to ~/.vim/pack/testing/start/vader.vim (where run_tests.sh looks); then run './run_tests.sh' and 'uv run pytest test/unit/' (Python from .python-version, 3.11). Leave 'bridle spec check' out of CI (it needs the bridle binary). Mention CI in README's Testing section in a line. The worker can't see a GitHub run; after merging and pushing, the manager checks the run on main with 'gh run list --branch main --limit 1' (or reports that it can't) and tells the orchestrator the result. If it's green, a follow-up adds '[ci] github = true' to .bridle/config.toml (the orchestrator does that). Check: ./run_tests.sh && uv run pytest test/unit/ pass locally. No version bump.
