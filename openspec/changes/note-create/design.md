## Context

Note creation is spread across two Vimscript files. `template.vim` has
`FindTemplate`, `CreateContext`, `ProcessVariables`, `ExecuteCommand`, and
`ProcessTemplate`. `notes.vim` has the four `Open*Plan`/`OpenDaily` functions
(each computes a path, `mkdir`s the folder, `edit!`s the file, and fills the
buffer), `ExtractDateForTemplate` for `:MetaNotesOpen`, and the
`CalculateWeekStart`/`WeekEnd`/`Quarter` helpers. Nothing else in the plugin
uses these helpers.

The CLI (`scripts/meta_notes/cli.py`) already has the conventions this change
needs: `Output` with `data`, `text`, `warnings`, and text-mode-only
`notices`; stderr captured into `warnings` under `--json`; and
`meta_notes#cli#Run()` on the Vim side.

The shipped daily template runs `{{% python scripts/find_tasks.py ... %}}`
twice. No shipped template uses `{{% vim %}}`.

See proposal.md for motivation and the specs for required behavior.

## Goals / Non-Goals

**Goals:**
- One Python implementation of paths, discovery, and rendering, byte-for-byte
  compatible with the Vim output for the shipped templates
- Vim keeps its unsaved-buffer workflow through `--render`

**Non-Goals:**
- New template variables or syntax
- Changing `:MetaNotesDailyPrev`/`Next` or `:MetaNotesJumpToWeek` beyond
  what they inherit from `OpenDaily`/`OpenWeekPlan`
- Timeouts or sandboxing for command blocks (they run with the user's
  permissions, as today)

## Decisions

### 1. Two modules: `template.py` and `note.py`

- `scripts/meta_notes/template.py`: `find_template`, `build_context`,
  `render_line` (variables), `run_command_block`, and `render(path, context)`
  → `Rendered(lines, warnings, has_vim_blocks)`. No knowledge of note kinds.
- `scripts/meta_notes/note.py`: periodic path and template-date rules,
  `date_for_path` (the port of `ExtractDateForTemplate`), fallback headers,
  and `create(kind_or_path, date, template=None, render_only=False)` →
  `NoteResult(path, exists, created, template, content, warnings)`.
- `cli.py`: a `note` subcommand with nested subparsers `daily`, `weekly`,
  `quarterly`, `yearly` (optional `date`) and `new` (`path`, `--template`),
  all taking `--render`. `--root` and `--json` go on each nested parser via
  the existing `common` parent.

**Why split:** rendering is reused by anything that later renders a template
(`planning-skills`, the dashboard) without the periodic path rules.

### 2. Port the Vim semantics exactly, including quirks

Rendering must match the Vim output, so these behaviors are kept:

- **Command lines are whole-line.** Any line containing `{{%` is replaced
  entirely by the command's output; text around the block is dropped.
- **Output splitting.** Vim does `split(output, "\n", 1)`, which keeps a
  trailing empty item when output ends in a newline. So a block whose command
  prints `a\n` becomes two lines, `a` and an empty line. Python uses
  `output.split("\n")` for the same result.
- **stderr is merged** into the command's output, as with Vim's `system()`.
- **Variable parsing.** The expression inside `{{...}}` (matched by
  `{{([^}]+)}}`) is split at the first `:` into name-and-arithmetic and
  format; arithmetic matches `([^+-]+)([+-])(\d+)`. Date variables with no
  format render as `YYYY-MM-DD ddd`.
- **Failure text.** `<!-- Command failed: <line>\nError: <output> -->` and
  `<!-- Unknown command type: <type> -->`, verbatim.

Deliberate differences, none of which change output for the shipped
templates:

- Variables are substituted in one left-to-right pass (`re.sub` with a
  callback). Vim rescans from the start after each substitution, so a value
  containing `{{x}}` would be expanded again. One pass is safer.
- Date arithmetic uses `datetime.date` and `timedelta`. Vim adds
  `N * 86400` seconds to local midnight, which is off by a day across a
  fall-back DST change.
- Day and month names come from the C locale (English), regardless of the
  user's locale. Vim's `strftime` follows `LC_TIME`, but note filenames
  must not depend on locale.

**Alternative considered:** a cleaner renderer (partial-line command
blocks, strict errors). Rejected for this change; it would break existing
templates and the vader expectations. It can be a later change.

### 3. Running command blocks

`subprocess.run(cmd, shell=True, cwd=root, stdin=DEVNULL,
stdout=PIPE, stderr=STDOUT, text=True)`. For `python`, the command becomes
`<sys.executable> <cmd>`, with a leading `scripts/` replaced by the plugin's
absolute `scripts/` path (found from `meta_notes.__file__`). Using
`sys.executable` rather than `python3` runs scripts under the same Python
the CLI's version check accepted.

A failed command adds a warning, `Command failed: <line>`. Under `--json`,
subprocess output never reaches the CLI's stdout because it is captured.

### 4. `{{% vim %}}` blocks are passed through for Vim

The renderer substitutes variables inside a vim block and keeps the line
as `{{% vim <command> %}}`. `Rendered.has_vim_blocks` is set. When writing
the note (no `--render`), `note.create` adds a warning:
`<path>: {{% vim %}} blocks are left as text outside Vim`. With `--render`
there is no warning, because the caller is expected to be Vim.

In Vim, the `vim` branch of `ExecuteCommand` survives as
`meta_notes#template#RunVimBlocks(lines)`: for each line matching
`{{%\s*vim\s\+\(.\+\)\s*%}}` it runs the command with `redir` and replaces
the line with the output split into lines, as today. Only this and
`GetPluginRoot`/`ExecutePythonScript` remain in `template.vim`.

**Alternative considered:** drop vim blocks. The user chose to keep them.

### 5. Content, files, and the Vim buffer

`content` is the rendered lines joined with `\n` plus a trailing `\n`, and
the file is written with exactly that (UTF-8). Vim fills the buffer with
`split(content, "\n", 1)` minus the final empty item, so saving the buffer
produces the same bytes the CLI would have written.

All five Vim entry points go through one helper,
`meta_notes#notes#OpenNote(args)`:

1. `meta_notes#cli#Run(['note'] + args + ['--render'])`; on `ok` false,
   `echoerr` the error and stop. Show warnings.
2. If `exists`, `edit!` the path.
3. Otherwise `mkdir(fnamemodify(path, ':h'), 'p')`, `edit!` the path,
   `setline(1, lines)`, run `RunVimBlocks`, and put the cursor on line 1 if
   `template` is non-null, else line 3, as today. The buffer is left
   modified.

Vim creates the folder, not the CLI, because `--render` must write nothing;
the folder is what makes `:write` work, as it does today.

`:MetaNotesOpen` calls `note new <link path>`. The link path is relative to
Vim's current directory, which `cli#Run` passes as `--root`.

### 6. Paths, dates, and errors

- `today` is `date.today()` once per invocation.
- `note new` accepts an absolute path inside the root (via
  `to_root_relative`). A path that normalizes outside the root, including
  through `..`, is `CliError("Path is outside the notes root: <path>")`.
- `date_for_path` uses the same four patterns as `ExtractDateForTemplate`
  (daily requires the ` ddd` suffix; weekly allows it). Non-matching paths
  get today.
- Invalid dates: `CliError("Invalid date: <value> (expected YYYY-MM-DD)")`.
- The existence check and write use `open(path, "x")`, so a note created
  between the check and the write is never overwritten.

### 7. Tests move with the code

The vader tests that call `CreateContext`, `ProcessVariables`,
`ExecuteCommand`, `ProcessTemplate`, `FindTemplate`,
`ExtractDateForTemplate`, and `Calculate*` test removed functions. Their
cases are ported to pytest (`test/unit/test_template.py`,
`test/unit/test_note.py`) and removed from the vader files. The vader tests
that drive `:MetaNotesDaily`, `:MetaNotesWeekPlan`, `:MetaNotesQuarterPlan`,
`:MetaNotesYearPlan`, `:MetaNotesOpen`, and daily navigation stay and must
pass unchanged. They already assert buffer contents and, in
`open_note.vader`, that the file doesn't exist until saved.

Compatibility is checked by rendering each shipped template in Vim (at the
commit before the switch) and in Python for fixed dates, with command
blocks stubbed to fixed output, and comparing byte-for-byte. The Vim
renderings are saved as fixtures in `test/fixtures/templates/`.

## Risks / Trade-offs

- [Subtle rendering differences break existing notes' look] → fixture
  comparison against the Vim output for every shipped template (Decision 7).
- [`python` blocks now use `sys.executable` instead of `python3` on PATH] →
  both are Python 3 in practice; the CLI already requires 3.10+.
- [A slow command block (large notes root) delays Vim for longer than
  today] → same work as today, plus one process start. No mitigation now.
- [vim blocks are silently raw in notes created by agents] → the CLI warns;
  the docs say so.
- [`cli-init` lands first and changes where templates come from] → both use
  `resource/template/`; tests use the shipped template files once they
  exist, otherwise fixtures copied from `Init`'s template lists.

## Migration Plan

No data migration. Existing notes are never touched. Rollback is reverting
the change; the Vim commands then render in Vimscript again.
