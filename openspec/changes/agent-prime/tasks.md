# Tasks

## 1. Prime command

- [x] 1.1 Add `scripts/meta_notes/prime.py` with `render(text, root)` and `run(root)` mirroring `conventions.py`, and generators for `today-paths` (via `note.py`'s path function), `daily-sections` and `weekly-sections` (root template headings, shipped fallback), `tag-groups` (`TAG_GROUPS`), `skills` (`init.shipped_skills()`), and `conventions` (verbatim); verify with `test/unit/test_prime.py` tests for "Today's daily path" (fixed date), "Edited template", "New skill listed", "Conventions included", and an unknown marker raising
- [x] 1.2 Write `scripts/meta_notes/prime.md` per the `agent-prime` "Prime content" requirement and design decisions 4 and 6; verify with tests that assert the working hours, the archive rule, `Home.md`, `Meetings & Notes.md`, the naming rules, each finding command, and the `CLAUDE.md` preferences pointer are present
- [x] 1.3 Add the `prime` subcommand to `cli.py`, resolving the root optionally (`root` null and a leading no-root line outside a root); verify with tests through `cli.main` for "Inside a notes root", "JSON result", and "No notes root"
- [x] 1.4 Assert the size budget: a test runs `prime` in an initialized `tmp_path` root and checks stdout is at most 20,000 characters; verify `pipenv run pytest test/unit/test_prime.py`
- [x] 1.5 Document `prime` under a new `*meta-notes-cli-prime*` in `doc/meta-notes.txt` and in README's Command Line section and examples, with the `CLAUDE.md` line; verify `:helptags doc` reports no errors

## 2. Init check

- [x] 2.1 In `init.py`, add the `claude-md` item (`found` when `CLAUDE.md` or `.claude/CLAUDE.md` contains `meta-notes prime`, else `missing`), never writing either file; verify with `test_init.py` tests for "No CLAUDE.md", "Line present", and "Line in .claude/CLAUDE.md", and that the empty-directory run still has no warnings
- [x] 2.2 Add `claude-md` messages to `INIT_MESSAGES` in `cli.py` and to the message table in `autoload/meta_notes/notes.vim`, giving the line to add for `missing`; verify with a `test_cli.py` text-output test and the "Vim init shows the check" scenario in the init vader test
- [x] 2.3 Document the check in `*meta-notes-cli-init*` in `doc/meta-notes.txt` and README's init paragraph; verify both give the exact line

## 3. Skills

- [x] 3.1 Change the workday in `skills/calendar/SKILL.md` from 9:00–17:00 to 8:00–17:00; verify `grep -n '17:00' skills/*/SKILL.md` shows 8:00 in both `calendar` and `weekly-plan`

## 4. User's notes doc

- [x] 4.1 Rewrite `docs/work-notes-claude.md` as the work root's `CLAUDE.md`: the `prime` line first, then only personal preferences (lunch, breaks, the 15-minute shutdown block, the weekly admin checklist, meetings and personal time the user adds themselves); verify nothing in it contradicts `meta-notes prime` output

## 5. Integration

- [x] 5.1 In a real notes root with the `prime` line in `CLAUDE.md`, start a fresh Claude Code session and ask where today's daily note is, how to archive a finished project, and to add a task to a project; confirm it runs `meta-notes prime` first and answers from it; then run `pipenv run pytest test/unit/` and `./run_tests.sh`
