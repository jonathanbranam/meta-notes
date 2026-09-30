---
id: s34j
title: Move development from Pipfile and pipenv to pyproject.toml and uv
opened: 2026-09-30
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
---

# Move development from Pipfile and pipenv to pyproject.toml and uv

The human, 2026-09-30: "transition from using Pipfile and pipenv to
pyproject.toml and uv; analyze if that would cause any problems with the
plugin install but I prefer uv much more."

## What uses pipenv today

Only development does. `Pipfile` and `Pipfile.lock` give the test
environment (pytest, pytest-bdd, and the calendar libraries so its tests
run). `pipenv run pytest test/unit/` is the Python half of the check, named
in `.bridle/config.toml` (`check =`), `.bridle/roles/manager.md` and
`worker.md`, `.bridle/rules/languages.md` and `python-tests.md`,
`AGENTS.md`, and `docs/gherkin-compiler-testing.md`. The `openspec/changes/archive/`
task lists mention it too; they are history and stay as they are.

## The plugin install doesn't use it

Users never run pipenv. `meta-notes init` builds `<root>/.venv` with
`python3 -m venv` and `pip install -r requirements.txt` (spec `init`,
`doc/meta-notes.txt`, README), and `bin/meta-notes` runs the CLI with that
venv's python, or the `python3` on `PATH`. Everything but `calendar` is
stdlib-only. So moving development to uv doesn't change the install, as
long as `requirements.txt` stays and `init` keeps using venv and pip.
Users then need nothing new. Vim plugin managers ignore a `pyproject.toml`.

## Decisions (the human, 2026-09-30)

Approved as below. `requirements.txt` is kept and generated from
`uv.lock` whenever it changes; development moves to 3.11.

## Plan

- **`pyproject.toml`** with `requires-python = ">=3.11"`, the runtime
  libraries (`icalendar`, `recurring-ical-events`, pinned as in
  `requirements.txt`) as `dependencies`, and `pytest` and `pytest-bdd` in a
  `dev` dependency group. `[tool.uv] package = false`: the CLI still runs
  from the checkout, it isn't built or installed. `uv.lock` is committed.
- **Remove `Pipfile` and `Pipfile.lock`.** Keep `pytest.ini` as it is.
- **The check** becomes `./run_tests.sh && uv run pytest test/unit/`
  everywhere the list above names it (the bridle `check =` too).
- **`requirements.txt` stays** for `init`, and is generated from `uv.lock`
  every time the lock changes: `uv export --no-dev --no-hashes
  --no-emit-project -o requirements.txt` (flags as needed for a plain
  pinned list pip reads). A unit test runs the export and fails when
  `requirements.txt` differs, so a lock change can't land without it.
- **Development runs on 3.11**, the version users are promised: a
  `.python-version` of `3.11`. The Pipfile's 3.14 was a mistake. Update
  `languages.md` to say so.

## Issues

None that block it. To keep in mind:

1. **Two files of runtime pins.** `requirements.txt` is generated, and the
   test above catches a stale one. The alternative, `init` reading
   `pyproject.toml` or calling uv, would make users install uv. Not
   recommended.
2. **Every machine that runs checks needs uv.** The NUC has it
   (`~/.local/bin/uv`); the Mac needs it too. The missing-tools rule
   covers a machine without it.
3. **Agents spawned before the change** have `pipenv run` in their
   prompts. Land it between tasks, not while a worker is running.

## Done means

No `pipenv` or `Pipfile` outside `openspec/changes/archive/`, `uv run pytest
test/unit/` (on 3.11) and `./run_tests.sh` pass, `requirements.txt` matches
`uv export`, and `meta-notes init` in
a scratch root still builds `.venv` from `requirements.txt`. No CLI or
plugin behaviour changes, so no version bump (`.bridle/rules/versioning.md`).
