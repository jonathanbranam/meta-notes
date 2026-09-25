## Context

The CLI (`scripts/meta_notes/cli.py`) builds one argparse parser whose
subcommand is required, and `_run()` resolves the notes root before calling a
handler unless the handler sets `resolves_root=False`. `main()` owns output:
with `--json` it redirects stderr and prints one JSON object from an
`Output`. `_Parser.error()` raises `CliError` rather than exiting, so no code
path calls `sys.exit` from inside argparse. There is no version anywhere, no
git tags, and `scripts/meta_notes/__init__.py` holds only a docstring.

Users install the plugin as a git checkout (vim-plug, a symlink into
`pack/`, or the development `runtimepath`), so between version bumps the
commit hash is the only thing that tells two installs apart.

## Goals / Non-Goals

**Goals:**
- One place to change the version.
- `--version` reuses the existing `Output`/`--json` path, so its JSON
  follows the same rules as every other command.
- Commit lookup never fails the command or adds noise.

**Non-Goals:**
- The plugin checking that the CLI's version matches its own. They ship
  together from one checkout, so they can't drift apart.
- Storing the version in `g:loaded_meta_notes`. Nothing reads that
  variable, and it would be a second copy of the version.
- Packaging (`pyproject.toml`, PyPI). The CLI still runs from the checkout.
- A CHANGELOG file. Archived openspec changes already record what changed.

## Decisions

**Version constant in `meta_notes/__init__.py`.** `__version__ = "0.1.0"`.
The CLI imports it. Alternatives: a top-level `VERSION` file (readable by
Vimscript without Python, but that's not needed yet, and it adds file I/O
and a path lookup); deriving the version from `git describe` (breaks for
non-git installs, and the tags don't exist yet). Starting at `0.1.0` rather
than `1.0.0` signals that the CLI interface is still settling. Several
proposed changes add commands.

**`--version` as a custom argparse action that raises.** argparse's built-in
`action="version"` prints and calls `sys.exit` during parsing. That skips
`main()`, so `--json` isn't honored and the output doesn't follow the CLI's
conventions. Instead, a small `_VersionAction` raises a private
`_ShowVersion` exception. `_run()` catches it and returns an `Output` from
`cmd_version()`. argparse runs an action as soon as it reaches the option, so
this happens before the required-subcommand check. The action goes on the
shared `common` parent parser, so `--version` works before or after a
subcommand, like `--root` and `--json`. Raising at parse time also means no
subcommand handler runs and no root is resolved.

Alternative: scanning `argv` for `--version` before parsing, the way `main()`
checks `--json`. That's rejected because it would also match
`meta-notes note new --version` as a note path, while argparse treats it as
an option.

**Commit lookup.** `git_commit(plugin_dir)` runs
`git -C <plugin_dir> rev-parse --show-toplevel --short HEAD`. It uses the
result only if the top level resolves (with `os.path.realpath`) to
`plugin_dir`. This stops the plugin from reporting the commit of an
enclosing repository, such as a dotfiles repo holding `~/.vim`. For the
dirty check, it runs `git -C <plugin_dir> status --porcelain
--untracked-files=no`, and any output means dirty. Both run with a short
timeout, stdin from `DEVNULL`, and stderr captured. A missing `git`, a
non-zero exit, or a timeout gives `(None, False)`. `plugin_dir` is two
levels above `meta_notes/__init__.py`, the same way `__main__.py` finds
`scripts/`.

Untracked files don't count as dirty. `__pycache__/` and local files such as
`Session.vim` would otherwise make every development checkout dirty.

**Output.** Text: `meta-notes 0.1.0 (f20d0de)` or
`meta-notes 0.1.0 (f20d0de-dirty)` or `meta-notes 0.1.0`. JSON:
`{"ok": true, "version": "0.1.0", "commit": "f20d0de", "dirty": false,
"warnings": []}`. No Python version or install path for now. Both can be
added to the JSON later without breaking callers.

**`:MetaNotesVersion` calls the CLI.** It uses a new
`meta_notes#cli#Version()` in `autoload/meta_notes/cli.vim`, which runs
`meta_notes#cli#Run(['--version'])`. It formats the text line from the
JSON fields, the same way the CLI does, and returns it, or echoes the error
with `ErrorMsg`. Asking the CLI keeps `__version__` the only copy and also
checks that Python and the CLI work from inside Vim, which is usually what
someone checking the version wants to know. `Run()` always passes `--root
<cwd>`, and `--version` never resolves the root, so the command works from
any directory. Vim has no standard `:version`-style hook for plugins.
`:MetaNotesVersion` follows the `:MetaNotes*` naming of the other commands.
There's no mapping. The command is used rarely, and `<localleader>`
mappings are for markdown buffers.

**Bump policy.** Documented in `AGENTS.md`, next to the openspec workflow.
When archiving a change that alters CLI or plugin behavior, bump the
version in the same commit: PATCH for fixes, MINOR for new commands, options,
or behavior, and MAJOR for incompatible CLI changes, once past 1.0. Then tag
that commit `v<version>` and push the tag. Tying the bump to archiving puts
it at the one step that already happens once per change.

## Risks / Trade-offs

- [Two `git` subprocesses slow down `--version`] → Only `--version` pays for
  them, never other commands. The timeout bounds the worst case.
- [Someone forgets to bump the version] → The commit hash still identifies
  the install exactly. The archive step in `AGENTS.md` names the bump.
- [Running `git` in the plugin directory when the user doesn't own it] → git
  may refuse with "dubious ownership". That's a non-zero exit, so it's
  treated as no commit.

## Migration Plan

None. The option is new. After it lands, tag the commit `v0.1.0`.
