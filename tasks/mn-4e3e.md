+++
id = "mn-4e3e"
title = "GitHub Actions CI for the check"
kind = "chore"
state = "integrated"
created_at = "2026-09-30T21:25:36.760Z"
updated_at = "2026-09-30T21:43:24.383972409Z"
size = "S"
branch = "bridle/ci"
commit = "6c774d1"
summary = "Added .github/workflows/ci.yml (push to main and PRs; ubuntu-latest; setup-uv, vim, vader.vim; runs ./run_tests.sh and uv run pytest test/unit/) and a README line. No version bump. Merged 6c774d1. The GitHub run is for the orchestrator to check."
+++

Add .github/workflows/ci.yml: on push to main and on pull requests, ubuntu-latest. Install uv (astral-sh/setup-uv) and vim; clone https://github.com/junegunn/vader.vim to ~/.vim/pack/testing/start/vader.vim (where run_tests.sh looks); then run './run_tests.sh' and 'uv run pytest test/unit/' (Python from .python-version, 3.11). Leave 'bridle spec check' out of CI (it needs the bridle binary). Mention CI in README's Testing section in a line. The worker can't see a GitHub run; after merging and pushing, the manager checks the run on main with 'gh run list --branch main --limit 1' (or reports that it can't) and tells the orchestrator the result. If it's green, a follow-up adds '[ci] github = true' to .bridle/config.toml (the orchestrator does that). Check: ./run_tests.sh && uv run pytest test/unit/ pass locally. No version bump.

## Thread

### note · agent:manager · 2026-09-30T21:43:23.651Z
integrated: 6c774d1 (branch bridle/ci)

### note · agent:manager · 2026-09-30T21:43:23.656Z
cleanup: removed nothing
