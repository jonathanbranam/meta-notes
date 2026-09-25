## 1. Sentinel-based root resolution

- [ ] 1.1 Add `scripts/meta_notes/root.py` with `find_root(start, home)` per design Decision 2 (sentinel `.meta-notes` only, one `isfile` per directory, `realpath` on both paths, stop after `$HOME`, stop silently at the first directory without read, write, and search permission, `OSError` ends the search); verify with the tests in 1.3
- [ ] 1.2 Switch `cli.resolve_root` to `find_root`, remove `is_notes_root` and `ROOT_MARKERS`, and change the no-root error to say to run `meta-notes init` or pass `--root`; verify `grep -rn "ROOT_MARKERS\|is_notes_root" scripts test` finds nothing
- [ ] 1.3 Tests in `test/unit/test_root.py` and `test/unit/test_cli.py` for every scenario in `specs/cli/spec.md`: walk up to the sentinel, folder markers alone not a root, explicit `--root` without a sentinel, stop at `$HOME` (set `HOME` via `monkeypatch`), stop at a non-writable directory with no permission error (`chmod 0o555`, restored in teardown), `HOME` unset, and the no-root error text; rewrite existing marker-based walk tests to use the sentinel; verify `pipenv run pytest test/unit/test_root.py test/unit/test_cli.py` passes

## 2. Shipped templates

- [ ] 2.1 Generate `templates/daily.md`, `weekly.md`, `quarterly.md`, and `yearly.md` at the plugin root by running the current `:MetaNotesInit` in a temp directory and copying `resource/template/*.md`; also save copies as `test/fixtures/init_templates/*.md`; verify `cmp` shows the two sets identical
- [ ] 2.2 Test that each `templates/*.md` is byte-identical to its fixture (`test/unit/test_init.py`); verify it passes

## 3. Init command

- [ ] 3.1 Add `scripts/meta_notes/init.py`: plugin root from `Path(__file__).resolve().parents[2]`; create the 13 folders in today's order, copy templates (`--force` overwrites), create `.meta-notes` with the marker comment only if missing; return per-item `kind`, `path`, `status` and warnings; verify with 3.5
- [ ] 3.2 Skill install in `init.py` per design Decision 6: a skill is `skills/<name>/` with `SKILL.md`; absolute link to the real plugin path; `created`, `exists` (by `realpath`), `repointed` (foreign or broken link, `os.remove` then link), `skipped` with warning (real file or directory), `replaced` under `--force`; verify with 3.5
- [ ] 3.3 Nesting check: search with `find_root` from the nearest existing ancestor of the target's parent before any write; fail with `Cannot initialize inside existing notes root: <root>` regardless of `--force`; verify with 3.5
- [ ] 3.4 Wire the `init` subcommand in `cli.py`: `resolves_root=False` default on the subparser so `_run` skips `resolve_root`; target is `--root` (`abspath(expanduser())`) or the current directory, `META_NOTES_ROOT` ignored; `os.makedirs(target, exist_ok=True)` after the nesting check; `OSError` becomes `CliError`; JSON `root` and `items`; text output one line per item plus `Meta-notes initialization complete!`; verify `bin/meta-notes init --root "$(mktemp -d)/n" --json` prints `ok: true` with every item `created`
- [ ] 3.5 Tests in `test/unit/test_init.py` for every scenario in `specs/init/spec.md`: empty directory, current directory, `--root` existing and missing (parents created), `META_NOTES_ROOT` ignored, nested inside a root with and without `--force`, re-run in a root, existing root without sentinel leaves every file unchanged, edited template kept and restored by `--force`, existing sentinel never rewritten, skill created / exists / stale repointed / real directory skipped with warning / replaced by `--force`, relative link to the right place counts as `exists`, plugin edit visible through the link, JSON report shape; verify `pipenv run pytest test/unit/test_init.py` passes

## 4. Vim integration

- [ ] 4.1 Rewrite `meta_notes#notes#Init(force)` to call `meta_notes#cli#Run(['init'] + ['--force' if force])`, `echoerr` on failure, echo the per-item messages from design Decision 8, show warnings with `meta_notes#cli#ShowWarnings`, then `Meta-notes initialization complete!`; verify `./run_tests.sh test/init.vader` passes unmodified
- [ ] 4.2 Add vader cases to `test/init.vader` for the sentinel and the `.claude/skills/project-review` link after `:MetaNotesInit`; verify `./run_tests.sh test/init.vader` passes
- [ ] 4.3 Remove the Vimscript folder list, template lists, and write loop from `autoload/meta_notes/notes.vim`; verify `grep -n "Time Block\|filename_pattern" autoload/meta_notes/notes.vim` finds nothing and `./run_tests.sh` passes

## 5. Documentation

- [ ] 5.1 `doc/meta-notes.txt`: document `meta-notes init` (options, `--root` creating the directory, re-runs, `--force`, nesting refusal, skills), rewrite `*meta-notes-cli-root*` for the sentinel and the bounded search, and update `:MetaNotesInit`; verify `:helptags doc` reports no errors
- [ ] 5.2 README: add `meta-notes init` to the Command Line section, a note that existing notes roots need `meta-notes init` run once to get `.meta-notes`, and `templates/` and `skills/` in the project structure; verify by reading the rendered sections
- [ ] 5.3 Update `docs/planning-system.md` where it describes installing skills or finding the notes root, if it does; verify `grep -n "symlink\|notes root" docs/planning-system.md` reflects init

## 6. Verification

- [ ] 6.1 Run the full suite (`./run_tests.sh` and `pipenv run pytest test/unit/`); all must pass
- [ ] 6.2 Manual check: `git init` a temp directory, run `bin/meta-notes init`, then `bin/meta-notes tasks` from its `project/` subfolder without `--root` finds the root; run `bin/meta-notes init` from that subfolder and confirm it refuses
