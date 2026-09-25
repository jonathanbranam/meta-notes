## Why

meta-notes now ships Claude Code skills (starting with `skills/project-review/`),
but there's no way for a user to install them into their notes root. Claude
Code only finds project skills under `<project>/.claude/skills/`, so they
would have to link each skill by hand. The planned rituals in
`docs/planning-system.md` add several more skills, so this needs to be part of
setup.

Setup itself only exists in Vimscript (`:MetaNotesInit`), so setting up a notes
root requires Vim, and the ~200 lines of template content are stored as
Vimscript list literals. Under the "one implementation" principle in
`docs/planning-system.md`, init belongs in the `meta-notes` CLI along with
every other note operation. Skill install is built there instead of being
built in Vimscript and ported later.

## Dependencies

**This change depends on `cli-core` landing first.** It needs the
`meta-notes` package, the `bin/meta-notes` shim, root resolution, and the
`--json` and error conventions from `cli-core` (its "CLI skeleton" task
group). Don't start implementing until `cli-core` is archived.

## What Changes

- Add `meta-notes init [--force] [--root <dir>]`, which creates the PPARA
  folders and templates the way `:MetaNotesInit` does today. There's no notes
  root yet, so `init` doesn't walk up to find one. It uses `--root`, and
  otherwise the current directory.
- Move the template content out of `autoload/meta_notes/notes.vim` into
  markdown files shipped with the plugin. `init` copies them into
  `resource/template/`. The resulting files are the same as today's.
- `init` installs every skill in the plugin's `skills/` directory into
  `<root>/.claude/skills/`. It creates that directory if needed and links each
  skill to the plugin's copy, so updating the plugin updates the skills.
- Re-running is safe. Existing folders and templates are kept. A correct skill
  link is left alone, and a stale or broken one is repointed. A real file or
  directory already at a skill's target is left alone with a warning. With
  `--force`, templates are overwritten and conflicting skill targets are
  replaced.
- `:MetaNotesInit[!]` keeps its name and behavior and calls
  `meta-notes init [--force] --json`. The Vimscript implementation is removed.
- The README and `doc/meta-notes.txt` document `meta-notes init` and the
  shipped skills.

## Capabilities

### New Capabilities
- `init`: Setting up a notes root: folders, templates, and installed Claude
  Code skills, including what happens on re-runs and conflicts.

### Modified Capabilities

*(none — `:MetaNotesInit` has no existing spec, and the `cli` capability from
`cli-core` doesn't change)*

## Impact

- `scripts/meta_notes/`: new `init` subcommand and module
- Plugin template files: new location for template content (for example,
  `templates/*.md` at the plugin root)
- `autoload/meta_notes/notes.vim`: `meta_notes#notes#Init` becomes a thin
  caller, and the embedded template lists are removed
- `test/unit/`: pytest coverage for folders, templates, skill install,
  re-runs, and conflicts
- `test/init.vader`: existing tests must still pass against the CLI-backed
  command
- `README.md`, `doc/meta-notes.txt`: init and skills documentation
- Notes roots: gain `.claude/skills/<name>` links to the plugin
- Out of scope: removing skills the plugin no longer ships, and editing the
  notes root's `.gitignore`
