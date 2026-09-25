## Why

Creating a note from a template is only possible inside Vim.
`autoload/meta_notes/template.vim` finds the template, fills in variables and
date arithmetic, and runs `{{% python ... %}}` blocks, and
`autoload/meta_notes/notes.vim` works out where daily, weekly, quarterly and
yearly notes go. The agent and the planned dashboard can't create notes, so
the `daily-plan` and `weekly-plan` skills in `planning-skills` can't produce
their output. Under the "one implementation" principle, note creation and
template rendering belong in the `meta-notes` CLI.

## Dependencies

- **`cli-core`** (archived): the `meta-notes` package, root resolution, and
  the `--json` and error conventions.
- **`cli-init`**: templates become markdown files shipped with the plugin
  and copied into `resource/template/`. This change renders those files.
  `cli-init` doesn't change the template format, so the two can be built in
  either order, but the tests should use the shipped template files.

## What Changes

- Add `meta-notes note daily|weekly|quarterly|yearly [<date>]`. The date
  defaults to today and accepts `YYYY-MM-DD`. It works out the note's path
  the same way the Vim commands do today (for example
  `plan/daily/YY-QN/YYYY-MM-DD ddd.md`). If the note doesn't exist, it
  creates the note from its template. It prints the path. With `--json`, it
  also reports whether the note was created or already existed.
- Add `meta-notes note new <path>` for any other note. It finds the
  template the same way `FindTemplate` does (a `template.md` in the same
  folder, then the standard template for plan folders) and falls back to a
  `# <path>` header. This is what following a link to a missing note uses.
  `--template <name>` skips discovery and uses
  `resource/template/<name>.md`; a missing named template is an error.
- An existing note is never overwritten or changed. The command just returns
  its path.
- `--render` renders the note without writing it. It prints the rendered
  content; with `--json`, it reports the path, whether the note already
  exists, and the rendered content (omitted when the note exists). Writing
  to disk is the default, so shells, agents and the dashboard create the
  file.
- With `--json`, stdout is a single JSON object and the note content is a
  string field in it. Command-block output is captured into the content,
  never passed through to stdout, and stderr becomes `warnings`, so a
  caller can't mistake stray output for note content.
- **Template rendering moves to Python.** Frontmatter is stripped. Variables
  work as specified in the `template` spec (path variables, date variables,
  arithmetic and format specifiers, `{{quarter}}`, `{{project_name}}`).
  Command blocks (`{{% python ... %}}` and `{{% shell ... %}}`) run from
  the notes root, as they do today. A failed command is written into the
  note as a `<!-- Command failed: ... -->` comment, as today, and is also
  reported as a warning. Rendered output matches the Vim implementation for
  the existing templates.
- **`{{% vim ... %}}` blocks stay in Vim.** The CLI can't run them, so it
  substitutes variables inside the block and leaves the block in its
  output. When Vim fills a buffer from `--render` output, it runs each vim
  block and replaces it with the output. A note the CLI writes directly
  keeps the block as text, and the CLI warns about it.
- **Vim becomes a thin caller.** `:MetaNotesDaily`, `:MetaNotesWeekPlan`,
  `:MetaNotesQuarterPlan`, `:MetaNotesYearPlan`, and note creation in
  `:MetaNotesOpen` call the CLI with `--render --json`. If the note
  exists, Vim opens it. Otherwise Vim opens a new, unsaved buffer named
  for the returned path and fills it with the rendered content. Nothing is
  written until the user saves the buffer, so opening a note and quitting
  without saving leaves no file, as today. The Vimscript rendering and path
  logic are removed. Navigation commands (`:MetaNotesDailyPrev`/`Next`,
  `:MetaNotesJumpToWeek`) keep working.

## Capabilities

### New Capabilities
- `note-create`: the `meta-notes note` commands, periodic-note path rules,
  never overwriting, `--render`, and JSON output

### Modified Capabilities
- `template`: rendering, including command blocks and template discovery,
  is done by the CLI. The Vim plugin calls it. Variable semantics are
  unchanged.

## Open Questions

None. Resolved:

- Vim shows an unsaved buffer, using `--render`.
- Command-block failures are written into the note as an error comment,
  as today, and reported as warnings.
- `note new` takes a `--template <name>` override.
- `{{% vim %}}` blocks are run by Vim when it fills the buffer.

## Impact

- `scripts/meta_notes/`: new `note` subcommand and a template-rendering
  module (stdlib only)
- `autoload/meta_notes/template.vim`: rendering removed or reduced to a
  wrapper
- `autoload/meta_notes/notes.vim`: `OpenDaily`, `OpenWeekPlan`,
  `OpenQuarterPlan`, `OpenYearPlan`, and `Open` call the CLI
- `test/unit/`: pytest coverage for paths, rendering, command blocks, and
  never overwriting
- `test/template*.vader`, daily and weekly note tests: must still pass
  against the CLI-backed commands
- `README.md`, `doc/meta-notes.txt`: document `meta-notes note`
