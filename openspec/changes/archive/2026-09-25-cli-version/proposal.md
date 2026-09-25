## Why

There's no way to tell which meta-notes a shell, agent, or bug report is
running. The plugin is installed from a git checkout and updated in place by
a plugin manager, and the CLI's commands and output keep changing as
proposals land. So "which version do you have?" has no answer today.
`meta-notes --version` answers it, and a version number that is bumped
deliberately records when behavior changed.

## What Changes

- Add a single version number for meta-notes, `MAJOR.MINOR.PATCH`, starting
  at `0.1.0`. It lives in one place in the Python package, and the CLI reads
  it from there.
- Add `meta-notes --version`. It prints `meta-notes <version>`, followed by
  the git commit (and `-dirty` if there are uncommitted changes) when the
  plugin is running from its own git checkout. It works outside a notes root
  and needs no subcommand.
- `meta-notes --version --json` writes one JSON object with `ok`,
  `version`, `commit`, and `dirty`, following the CLI's `--json` conventions.
- Add `:MetaNotesVersion` in Vim. It runs `meta-notes --version --json`
  and echoes the same line, so Vim users can check their version without a
  shell. Vim has no standard way for plugins to report a version, and a
  command named for the plugin is the usual convention.
- Document how the version is maintained: bump it when a change that alters
  CLI or plugin behavior is archived, and tag the release commit
  `v<version>`.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `cli`: adds a requirement for reporting the version with `--version`,
  with and without `--json`, and without resolving a notes root, and
  `:MetaNotesVersion`, which shows it in Vim.

## Impact

- `scripts/meta_notes/__init__.py`: the version constant.
- `scripts/meta_notes/cli.py`: the `--version` option, the git commit
  lookup, and output.
- `test/unit/test_cli.py`: tests for the new option.
- `plugin/meta_notes.vim` and `autoload/meta_notes/cli.vim`:
  `:MetaNotesVersion`, with a vader test.
- `doc/meta-notes.txt` (`:help meta-notes-cli`), `README.md`, and
  `AGENTS.md`: the option and the version bump policy.
- No new dependencies. The commit lookup runs `git` only if it's installed
  and the plugin directory is a git checkout.
