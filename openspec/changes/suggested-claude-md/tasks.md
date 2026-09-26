# Tasks

## 1. Suggested file and message

- [x] 1.1 Move `docs/work-notes-claude.md` to `templates/suggested-CLAUDE.md` and make its opening generic; verify `git status` shows a rename and the file starts with the `prime` line
- [x] 1.2 Add `init.SUGGESTED_CLAUDE_MD` and extend the `claude-md`/`missing` message in `cli.py` and `notes.vim` with the path and a `cp` command; verify with `test_init.py` tests that the text output contains the path, that the file exists and contains `init.PRIME_LINE`, and the init vader test for the path
- [x] 1.3 Update `*meta-notes-cli-init*` in `doc/meta-notes.txt` and README's init paragraph and Agents section; verify `:helptags doc` reports no errors

## 2. Integration

- [x] 2.1 Run `meta-notes init` in a new directory outside any notes root (inside `notes-test` it would nest), confirm it prints the suggested file's path, run the printed `cp`, and re-run init to see `found`; then run `pipenv run pytest test/unit/` and `./run_tests.sh`
