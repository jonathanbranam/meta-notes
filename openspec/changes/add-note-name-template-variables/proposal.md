## Why

Templates have no way to reference the note's own filename — `{{project_name}}` only works inside `project/` folders and returns the project folder, not the note name. This makes folder-specific templates less useful in `area/`, `resource/`, and `plan/` where the note's own name is the natural heading. Alongside this gap, the template system has no documentation, so users must read source code to discover available variables, arithmetic, format specifiers, and the `{{% command %}}` syntax.

## What Changes

- Add `{{note_path}}` variable: path without extension (e.g. `project/foo/my-meeting-notes`)
- Add `{{note_name}}` variable: filename stem only (e.g. `my-meeting-notes`)
- Add `{{filename}}` variable: filename with extension (e.g. `my-meeting-notes.md`)
- Fix: replace `ProcessVariables`'s implicit date-detection heuristic (`^\d{4}-\d{2}-\d{2}$`) with an explicit allowlist of date variables (`date`, `today`, `week_start`, `week_end`); all other context values are treated as strings unconditionally
- Refactor: move `project_name` derivation from a special case in `ProcessVariables` into `CreateContext`, making it consistent with all other variables
- Add `doc/templates.md`: complete reference for the template system covering folder resolution priority, all supported variables and their options (arithmetic, format specifiers), and the `{{% vim/python/shell %}}` command syntax

## Capabilities

### New Capabilities
- `template`: Template system — folder resolution, variable substitution, command execution, and all supported syntax

### Modified Capabilities
_(none — no spec currently covers the template system)_

## Impact

- `autoload/meta_notes/template.vim`:
  - `CreateContext` gains `note_path`, `note_name`, `filename`, and `project_name` keys (derived from `filepath`)
  - `ProcessVariables` date-detection heuristic replaced with explicit date variable allowlist; `project_name` special-case block removed
- `doc/templates.md`: new documentation file (plain markdown, no vim doc format required)
- `test/`: vader tests for the three new variables and the refactored `project_name` path
