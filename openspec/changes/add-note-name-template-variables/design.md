## Context

`ProcessVariables` (`autoload/meta_notes/template.vim`) resolves `{{variable}}` tokens in two passes: special-cased variables handled first (currently only `project_name`), then a generic path that looks the variable up in the context dict. The generic path auto-detects whether the value is a date by matching `^\d{4}-\d{2}-\d{2}$` — if it matches, date arithmetic and formatting are applied; otherwise the value is used as-is. This heuristic creates a latent bug: a note named `2024-01-15.md` would cause `{{note_name}}` to resolve as `"2024-01-15 Thu"` instead of `"2024-01-15"` because the stem matches the date pattern.

`CreateContext` populates the context dict with: `date`, `today`, `week_start`, `week_end`, `quarter`, `filepath`. Because `filepath` is already in the dict and its value (e.g. `project/lunch/Lunch Ideas.md`) never matches the date regex, `{{filepath}}` already works as a template variable — no code change is needed, only documentation.

The four agreed variable names are:

| Variable | Value | Example |
|---|---|---|
| `{{note_path}}` | path without extension | `project/lunch/Lunch Ideas` |
| `{{note_name}}` | filename stem only | `Lunch Ideas` |
| `{{filepath}}` | full path with extension | `project/lunch/Lunch Ideas.md` *(already works)* |
| `{{filename}}` | filename with extension | `Lunch Ideas.md` |

## Goals / Non-Goals

**Goals:**
- `{{note_name}}`, `{{note_path}}`, and `{{filename}}` work correctly in any template
- All four path variables are documented in `doc/templates.md` alongside all other template features
- No date arithmetic or format specifiers apply to path variables (they are always raw strings)

**Non-Goals:**
- Adding arithmetic or format-specifier support to path variables
- Changing how date variables (`date`, `today`, etc.) behave
- Producing vim `:help` formatted documentation (plain markdown is sufficient)

## Decisions

### 1. Replace the date-detection heuristic with an explicit allowlist in `ProcessVariables`

Instead of testing each context value's format to decide whether to apply date processing, explicitly enumerate the variables that support date features:

```vim
let l:date_vars = ['date', 'today', 'week_start', 'week_end']
if index(l:date_vars, l:var_name) >= 0
  " apply arithmetic / format specifiers
else
  " string: use value as-is
endif
```

**Why not keep the heuristic:** A note named `2024-01-15.md` produces `note_name = "2024-01-15"`, which matches `^\d{4}-\d{2}-\d{2}$` and would be silently rendered as `"2024-01-15 Thu"`. The allowlist eliminates the ambiguity entirely — date features are available only on variables that are semantically dates, regardless of what any string value happens to look like.

**Why allowlist over blocklist (excluded string variables):** The set of date variables is small and stable; new variables added in future are strings by default without any extra bookkeeping.

### 2. Move `project_name` derivation into `CreateContext`; remove its special case from `ProcessVariables`

Compute `note_path`, `note_name`, `filename`, and `project_name` in `CreateContext` from the `filepath` parameter and store them as plain strings in the context dict. With the allowlist in place (decision 1), they pass through `ProcessVariables` as strings unconditionally.

**Why this is safe for `project_name`:** The special-case block currently ignores arithmetic and format specifiers anyway (it substitutes and `continue`s without checking `l:arithmetic` or `l:format`). The generic string path produces identical behaviour. The `<!-- ERROR: No filepath in context -->` guard in the special case is dead code — `filepath` is always set by `CreateContext`.

**Result:** `ProcessVariables` has no special cases at all; all variable behaviour is determined by the allowlist check on the variable name.

### 3. `{{filepath}}` requires no code change

It already resolves correctly via the generic path (the value contains slashes and an extension, never matching the date regex — and with the allowlist it is unambiguously a string). Documentation only.

### 4. Documentation as `doc/templates.md` (plain markdown)

A single reference file covering: folder template resolution priority, all variables with their options (arithmetic, format specifiers), and the `{{% type command %}}` syntax. Plain markdown rather than vim `:help` format — this is a personal plugin and the file is more useful as something readable in a browser or editor than something navigated with `:help`.

## Risks / Trade-offs

- **`{{note_path}}` contains slashes**, which means it is not valid as a bare heading on its own in some contexts — but this is the intended use (e.g. `# {{note_path}}` produces `# project/lunch/Lunch Ideas`, matching the existing standard). No mitigation needed; it is the intended behavior.
- **Vim's `substitute()` interprets `&` and `\N` in the replacement string.** Note names containing `&` (e.g. `Bread & Butter.md`) would be mis-substituted. This pre-exists for `project_name` and is not introduced by this change. Mitigation: wrap all context value replacements with `escape(l:replacement, '&\')` — this covers `project_name` (now going through the generic path) and the three new variables.
