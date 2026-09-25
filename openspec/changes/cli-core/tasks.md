## 1. CLI skeleton

- [x] 1.1 Create `scripts/meta_notes/` package with `__main__.py` and `cli.py` (argparse subcommands); `scripts/` on `sys.path` so existing flat imports work
- [x] 1.2 Add `bin/meta-notes` shim; fail with a clear message on Python older than 3.10
- [x] 1.3 Implement notes root resolution: `--root`, `META_NOTES_ROOT`, walk up to a directory with `plan/`, `project/`, `area/`; change into the root
- [x] 1.4 Implement output conventions: human text by default; `--json` writes one object to stdout on success and failure (`ok`, `error`, `warnings`) and nothing to stderr; without `--json`, errors to stderr; non-zero exit on failure
- [x] 1.5 Tests for root resolution and output modes (`test/unit/test_cli.py`)

## 2. File operations

- [x] 2.1 Port `MoveItem` to `ops.move`: `.md` inference, target-exists error, parent creation, folder moves with non-markdown files, move list (each `.md` plus the folder), exact-match header rewrite, `update_links.update_all_links` per move with root `.`
- [x] 2.2 Port `Rename` to `ops.rename` (bare name keeps directory, `.md` appended)
- [x] 2.3 Port `Archive` to `ops.archive`: `.md` inference, allowed source folders, wildcard expansion with per-item results; error messages identical to the Vimscript
- [x] 2.4 Wire `move`, `rename`, `archive` subcommands; JSON result includes `moves` and link-rewritten files
- [x] 2.5 Tests mirroring every case in `test/archive.vader` and `test/rename.vader`, every scenario in `openspec/specs/archive/spec.md`, folder and hierarchy moves, and that a move in a git repo leaves the index and history unchanged (`test/unit/test_ops.py`)

## 3. Task query

- [x] 3.1 `tasks` subcommand calling `find_tasks` functions with the same options and text output
- [x] 3.2 `--json` output with file, line, text, status, dates, and report category
- [x] 3.3 Tests comparing `meta-notes tasks` text output to `find_tasks.py` for the default report and each filter, plus JSON fields (`test/unit/test_query.py`)

## 4. Vim integration

- [x] 4.1 Add a Vimscript helper that runs `bin/meta-notes --root <getcwd()> --json ...` and decodes the result
- [x] 4.2 Switch `meta_notes#file_ops#MoveItem`, `Archive`, and `Rename` to the helper, keeping signatures, return values, messages, and buffer handling (`autoload/meta_notes/file_ops.vim`)
- [x] 4.3 `:MetaNotesArchive` passes wildcards through to the CLI unexpanded
- [x] 4.4 Run `./run_tests.sh` with the vader tests unmodified; all must pass
- [x] 4.5 Remove `s:UpdateFileHeader`, `s:UpdateAllWikiLinks`, and the Vimscript move logic

## 5. Documentation

- [x] 5.1 CLI section in `doc/meta-notes.txt`
- [x] 5.2 Update README project structure (`bin/`, `scripts/meta_notes/`)

## 6. Verification

- [ ] 6.1 Run full test suite (`./run_tests.sh` and `pipenv run pytest test/unit/`)
