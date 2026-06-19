## 1. Refactor — Date variable allowlist

- [ ] 1.1 In `ProcessVariables`, replace the date-detection heuristic (`match(l:value, '^\d\{4\}-\d\{2\}-\d\{2\}$')`) with an explicit allowlist check: `index(['date', 'today', 'week_start', 'week_end'], l:var_name) >= 0` (`autoload/meta_notes/template.vim`)
- [ ] 1.2 Wrap the string-variable replacement with `escape(l:replacement, '&\')` to prevent `substitute()` from misinterpreting `&` or `\N` in note names (`autoload/meta_notes/template.vim`)

## 2. Refactor — Move `project_name` into `CreateContext`

- [ ] 2.1 In `CreateContext`, derive and store `project_name` from the `filepath` parameter (second path component if path starts with `project/`, else empty string) (`autoload/meta_notes/template.vim`)
- [ ] 2.2 Remove the `project_name` special-case block from `ProcessVariables` (`autoload/meta_notes/template.vim`)

## 3. Feature — New path-derived variables

- [ ] 3.1 In `CreateContext`, derive and store `note_path` (`fnamemodify(filepath, ':r')`), `note_name` (`fnamemodify(filepath, ':t:r')`), and `filename` (`fnamemodify(filepath, ':t')`) from the `filepath` parameter (`autoload/meta_notes/template.vim`)

## 4. Tests — Refactored behaviour

- [ ] 4.1 Add vader test: `{{project_name}}` in a project folder still resolves to the project folder name after the refactor (`test/template.vader`)
- [ ] 4.2 Add vader test: `{{date+7}}` still applies arithmetic correctly after the allowlist change (`test/template.vader`)
- [ ] 4.3 Add vader test: `{{note_name}}` for a date-named file (`2026-06-19.md`) resolves to `2026-06-19`, not `2026-06-19 Fri` (`test/template.vader`)

## 5. Tests — New variables

- [ ] 5.1 Add vader test: `{{note_path}}` resolves to relative path without extension (`test/template.vader`)
- [ ] 5.2 Add vader test: `{{note_name}}` resolves to filename stem (`test/template.vader`)
- [ ] 5.3 Add vader test: `{{filepath}}` resolves to full relative path with extension (`test/template.vader`)
- [ ] 5.4 Add vader test: `{{filename}}` resolves to filename with extension (`test/template.vader`)

## 6. Documentation

- [ ] 6.1 Expand section 6 of `doc/meta-notes.txt` (`*meta-notes-templates*`) from its current two-sentence stub into a full reference: folder template resolution priority (3-step order), all supported variables with descriptions and examples, arithmetic and format specifier syntax, and the `{{% vim/python/shell %}}` command forms (vim help format, `:help meta-notes-templates`)

## 7. Verification

- [ ] 7.1 Run full test suite (`./run_tests.sh`) — all tests pass
