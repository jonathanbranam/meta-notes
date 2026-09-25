## Why

meta-notes now ships Claude Code skills (starting with `skills/project-review/`),
but there's no way for a user to install them into their notes root. Claude
Code only finds project skills under `<project>/.claude/skills/`, so they
would have to link each skill by hand. The planned ceremonies in
`docs/planning-system.md` add several more skills, so this needs to be part of
setup.

Setup itself only exists in Vimscript (`:MetaNotesInit`), so setting up a notes
root requires Vim, and the ~200 lines of template content are stored as
Vimscript list literals. Under the "one implementation" principle in
`docs/planning-system.md`, init belongs in the `meta-notes` CLI along with
every other note operation. Skill install is built there instead of being
built in Vimscript and ported later.

## Dependencies

Builds on `cli-core` (archived 2026-09-25): the `meta-notes` package, the
`bin/meta-notes` shim, `--root`, and the `--json` and error conventions. That
dependency is met.

## What Changes

- Add `meta-notes init [--root <dir>] [--force]`, which creates the PPARA
  folders and templates the way `:MetaNotesInit` does today. It is meant to
  be run in the top-level directory of the notes root, usually right after
  `git init`.
- `init` creates a sentinel file, `.meta-notes`, at the top of the notes
  root. Its presence is what marks a directory as a notes root. It is meant to
  be committed with the notes.
- `init` doesn't search for where to initialize. It initializes `--root` when
  given (this is what Vim passes), otherwise the current directory. Unlike
  other commands, `init` creates the `--root` directory, including parents,
  if it doesn't exist. `META_NOTES_ROOT` is ignored, because it names an
  existing root to operate on, not where to create one.
- Other commands find the notes root by the sentinel instead of by folder
  names. When neither `--root` nor `META_NOTES_ROOT` is given, they search
  upward from the current directory for the nearest directory containing
  `.meta-notes`. The `plan/`, `project/`, and `area/` check is removed:
  those names are too generic to identify a notes root. An explicit `--root`
  or `META_NOTES_ROOT` is still used as given, with or without a sentinel, so
  Vim and the vader fixtures are unaffected.
- The upward search is bounded and quiet:
  - It checks each directory only for `.meta-notes`. It never lists a
    directory's contents.
  - It stops after `$HOME`.
  - It stops, without an error, at the first directory the user can't read,
    write, and enter. A notes root needs all three, so nothing above that
    point could be one. This also bounds searches outside `$HOME`: system
    directories such as `/`, `/Users`, and `/Volumes` aren't writable.
  - Stopping without a match is not an error in itself. Other commands then
    report that no notes root was found.
- Notes roots never nest. `init` runs the same bounded search from the
  target's parent. If it finds a `.meta-notes`, `init` fails, names that
  root, and changes nothing. `--force` doesn't override this. Re-running
  `init` in an existing root is not nesting.
- Existing notes roots have no sentinel. Running `meta-notes init` in one (or
  `:MetaNotesInit` in Vim) adds it without touching notes. Until then, a
  command run from a shell without `--root` fails with an error that says to
  run `meta-notes init` in the notes root.
- Move the template content out of `autoload/meta_notes/notes.vim` into
  markdown files shipped with the plugin. `init` copies them into
  `resource/template/`. The resulting files are the same as today's.
- `init` installs every skill in the plugin's `skills/` directory into
  `<root>/.claude/skills/`. It creates that directory if needed and links each
  skill to the plugin's copy, so updating the plugin updates the skills.
- Re-running is safe, including in an existing, populated notes root. Only
  missing folders, templates, and the sentinel are created, and no note is modified or
  removed. Existing folders and templates are kept. A correct skill
  link is left alone, and a stale or broken one is repointed. A real file or
  directory already at a skill's target is left alone with a warning. With
  `--force`, templates are overwritten and conflicting skill targets are
  replaced.
- `:MetaNotesInit[!]` keeps its name and behavior: it initializes Vim's
  current directory and shows the same per-folder and per-template messages
  as today, plus one per skill. It calls `meta-notes init [--force]` through
  the existing CLI helper (`--root` set to the current directory, `--json`).
  The Vimscript implementation is removed.
- The README and `doc/meta-notes.txt` document `meta-notes init` and the
  shipped skills.

## Capabilities

### New Capabilities
- `init`: Setting up a notes root: folders, templates, and installed Claude
  Code skills, and the `.meta-notes` sentinel, including what happens on
  re-runs, conflicts, and nested roots.

### Modified Capabilities
- `cli`: "Notes root resolution" changes. The walk up from the current
  directory looks for the `.meta-notes` sentinel instead of `plan/`,
  `project/`, and `area/`, stops at `$HOME` and at the first directory without read, write, and search
  permission, and `init` is exempt from resolution because it
  initializes a named directory. The other `cli` requirements (`--json`,
  errors, no git writes) apply to `init` unchanged.

## Impact

- `scripts/meta_notes/`: new `init` subcommand and module; `cli.py` finds
  the root by sentinel and skips root resolution for `init`
- Plugin template files: new location for template content (for example,
  `templates/*.md` at the plugin root)
- `autoload/meta_notes/notes.vim`: `meta_notes#notes#Init` becomes a thin
  caller, and the embedded template lists are removed
- `test/unit/`: pytest coverage for folders, templates, skill install,
  re-runs, conflicts, the sentinel, and nested roots; `test_cli.py`
  root-walk tests switch from folder markers to the sentinel and cover the
  `$HOME` and permission stops
- `test/init.vader`: existing tests must still pass against the CLI-backed
  command
- `README.md`, `doc/meta-notes.txt`: init, sentinel, root resolution, and
  skills documentation
- Notes roots: gain a `.meta-notes` sentinel and `.claude/skills/<name>`
  links to the plugin. Existing roots need `init` run once.
- Out of scope: removing skills the plugin no longer ships, and editing the
  notes root's `.gitignore`
