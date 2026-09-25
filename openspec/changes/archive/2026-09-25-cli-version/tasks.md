## 1. Version source

- [x] 1.1 Add `__version__ = "0.1.0"` to `scripts/meta_notes/__init__.py`, and check that `python3 -c 'import sys; sys.path.insert(0, "scripts"); import meta_notes; print(meta_notes.__version__)'` prints `0.1.0`

## 2. CLI option

- [x] 2.1 Add `git_commit(plugin_dir)` to `cli.py`. It returns `(short_hash, dirty)`, or `(None, False)` when git is missing, fails, times out, or the top level isn't `plugin_dir`. Unit tests cover a clean temporary repo, a dirty one (tracked file modified), untracked-only changes (not dirty), a plugin dir nested inside another repo (None), and a non-repo directory (None)
- [x] 2.2 Add `_VersionAction` and `_ShowVersion` to the `common` parent parser, and `cmd_version()` building the text line and JSON fields. Catch `_ShowVersion` in `_run()` before root resolution. `test_cli.py` tests cover: `--version` text output; `--version --json` fields and empty stderr; success from a directory with no notes root; `archive project/foo --version` reports the version and leaves `project/foo` in place
- [x] 2.3 Check that `meta-notes --help` lists `--version`, and that `bin/meta-notes --version` from `/tmp` prints `meta-notes 0.1.0 (<hash>)`

## 3. Vim command

- [x] 3.1 Add `meta_notes#cli#Version()` to `autoload/meta_notes/cli.vim` and `command! MetaNotesVersion` to `plugin/meta_notes.vim`. Add `test/version.vader`, which checks that `:MetaNotesVersion` echoes a line matching `^meta-notes \d\+\.\d\+\.\d\+` from a directory with no `.meta-notes` (using the temporary-directory pattern), and that `./run_tests.sh test/version.vader` passes

## 4. Documentation

- [x] 4.1 Document `--version` and its JSON fields under `:help meta-notes-cli` in `doc/meta-notes.txt`, add a `*meta-notes-cli-version*` tag, document `:MetaNotesVersion` with a `*:MetaNotesVersion*` tag in the commands section, and check that `:helptags doc` succeeds
- [x] 4.2 Mention `meta-notes --version` in the README's Command Line section
- [x] 4.3 Add the bump policy to `AGENTS.md`: bump PATCH, MINOR, or MAJOR in the commit that archives a behavior-changing change, then tag `v<version>` and push the tag

## 5. Verify

- [x] 5.1 Run `pipenv run pytest test/unit/` and `./run_tests.sh`, and check that both pass
