## 1. Variable

- [x] 1.1 Add `week_quarter` (quarter of `week_start`) to `build_context` in `scripts/meta_notes/template.py`; verify with `test/unit/test_template.py` cases for the three `week_quarter` scenarios in `specs/template/spec.md` (`2026-04-02` gives `Q2 Q1` for `{{quarter}} {{week_quarter}}`, `2026-01-01` gives `Q4`, `2026-02-13` gives `Q1`), and update `test_build_context_all_variables` to include it

## 2. Shipped daily template

- [x] 2.1 Change the week link in `templates/daily.md` to `[[plan/week/{{week_start:%y}}-{{week_quarter}}/{{week_start:%Y-%m-%d}}]]`, copy the file to `test/fixtures/init_templates/daily.md`, change `26-Q2` to `26-Q1` in `test/fixtures/templates/daily-2026-04-02.md`, and note the edit in the fixture test's docstring; verify `pipenv run pytest test/unit/test_init.py test/unit/test_template.py` passes
- [x] 2.2 Add a `test/unit/test_note.py` test that renders the shipped daily template for every day of 2025 and 2026 (command blocks stubbed) and asserts the `Week Plan:` link, with `.md` appended, equals `note.periodic_note("weekly", d)[0]`, which checks both the year and the quarter; verify it passes, and fails if the template is switched back to `{{quarter}}`

## 3. Documentation

- [x] 3.1 Document `week_quarter` in `doc/meta-notes.txt` under "Other variables", saying to use it for week plan paths and showing the daily template's link as the example; verify `:help meta-notes-template-variables` shows it

## 4. Verification

- [x] 4.1 Run `./run_tests.sh` and `pipenv run pytest test/unit/`; all pass
- [x] 4.2 In a scratch notes root, run `meta-notes note daily 2026-04-02` and `meta-notes note weekly 2026-04-02`; verify the daily note's week link, with `.md` appended, is the path the weekly command printed
- [x] 4.3 Run `openspec validate fix-week-plan-link-quarter --strict`; it passes
