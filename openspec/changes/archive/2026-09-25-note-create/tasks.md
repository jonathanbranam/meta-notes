## 1. Compatibility fixtures

- [x] 1.1 Before changing any Vimscript, render each shipped template (daily, weekly, quarterly, yearly) in Vim for fixed dates (including `2026-02-13` and a quarter boundary), with command blocks stubbed to fixed output, and save the results in `test/fixtures/templates/`; verify one fixture per template and date exists

## 2. Template rendering (`scripts/meta_notes/template.py`)

- [x] 2.1 `build_context` (date, today, week_start, week_end, quarter, project_name, path variables) and `render_line` (variables, arithmetic, format specifiers, default `YYYY-MM-DD ddd`, unknown-variable comment, single pass, C-locale names); verify by porting every `CreateContext`/`ProcessVariables` case from `test/template.vader` and `test/templates.vader` to `test/unit/test_template.py`
- [x] 2.2 `find_template` (folder `template.md`, then plan standard templates); verify with pytest cases ported from the `FindTemplate` vader tests
- [x] 2.3 Frontmatter stripping and whole-line command blocks: `python` (via `sys.executable`, `scripts/` resolved to the plugin), `shell`, run from the notes root with stderr merged and stdin closed; failure and unknown-type comments verbatim; a warning per failed command; verify with pytest cases ported from the `ExecuteCommand`/`ProcessTemplate` vader tests plus a failed-command warning test
- [x] 2.4 `{{% vim %}}` pass-through: variables substituted inside, line kept, `has_vim_blocks` set; verify with a pytest case
- [x] 2.5 Compare Python rendering to the task 1.1 fixtures byte-for-byte; verify the comparison test passes for every fixture

## 3. Note creation (`scripts/meta_notes/note.py`)

- [x] 3.1 Periodic path and template-date rules, English `ddd`, invalid-date error; verify with pytest cases for every path scenario in `specs/note-create/spec.md` (including the Monday-in-previous-quarter week)
- [x] 3.2 `date_for_path` for `note new` (port of `ExtractDateForTemplate`), `.md` appended, outside-root error; verify with pytest cases ported from the `ExtractDateForTemplate` vader tests plus the `..` case
- [x] 3.3 Template selection with `--template` override, missing-template error, and fallback headers per kind; verify with pytest cases for each header and the override scenarios
- [x] 3.4 `create`: write with parent folders using exclusive create, never touch an existing note, `render_only` writes nothing (no folders), vim-block warning only when writing; verify with pytest cases in `test/unit/test_note.py`, including that a pre-existing file's bytes and mtime are unchanged

## 4. CLI

- [x] 4.1 `note` subcommand with `daily|weekly|quarterly|yearly [date]` and `new <path> [--template]`, all with `--render`, `--root`, `--json`; verify `bin/meta-notes note --help` lists them
- [x] 4.2 Output: text mode prints the path (or the content with `--render`, or the `Note already exists` notice on stderr); JSON has `path`, `exists`, `created`, `template`, and `content` only when rendering a new note; verify with `test/unit/test_cli.py` cases for each spec JSON scenario and that stdout parses as a single object when a command block prints output

## 5. Vim integration

- [x] 5.1 Add `meta_notes#notes#OpenNote(args)` (CLI `--render`, errors, warnings, `edit!`, parent `mkdir`, fill buffer, cursor line 1 or 3) and `meta_notes#template#RunVimBlocks(lines)`; verify with a vader test that a template with `{{% vim echo "x" %}}` fills the buffer with `x`
- [x] 5.2 Switch `OpenDaily`, `OpenWeekPlan`, `OpenQuarterPlan`, `OpenYearPlan`, and `Open` to `OpenNote`; verify `./run_tests.sh test/planning.vader test/open_note.vader` passes unmodified
- [x] 5.3 Remove `FindTemplate`, `CreateContext`, `ProcessVariables`, `ExecuteCommand`, `ProcessTemplate`, `ExtractDateForTemplate`, and `Calculate*` from Vimscript, and remove their vader tests (ported in sections 2 and 3); verify `grep` finds no remaining callers and `./run_tests.sh` passes

## 6. Documentation

- [x] 6.1 `doc/meta-notes.txt`: `meta-notes note` in the CLI section; templates section covers rendering by the CLI, `--template`, the new resolution order, and vim blocks being left as text outside Vim; verify `:help meta-notes-templates` shows it
- [x] 6.2 README: `meta-notes note` example and updated project structure (`template.py`, `note.py`, new tests); verify by reading the rendered sections

## 7. Verification

- [x] 7.1 Run `./run_tests.sh` and `pipenv run pytest test/unit/`; all pass
- [x] 7.2 In a scratch notes root, run `meta-notes note daily` twice and `meta-notes note daily --render --json`; verify the first creates the file, the second leaves it unchanged, and the third reports `exists` true with no `content`
- [x] 7.3 Run `openspec validate note-create --strict`; it passes
