## Context

See proposal.md. Init reports the check as a `claude-md` item with
status `found` or `missing`; the CLI and Vim turn items into messages
through tables keyed by kind and status, formatted with the item's path.

## Goals / Non-Goals

**Goals:**
- A new root's first `init` shows where a ready-made `CLAUDE.md` is.

**Non-Goals:**
- Copying the file. `CLAUDE.md` is the user's; init keeps not writing it.
- A JSON field for the path. Agents don't set up roots; the text and Vim
  messages are enough.

## Decisions

### 1. `templates/suggested-CLAUDE.md`

`templates/` already holds files init reads by name (the note templates,
`cache-README.md`), and init copies only those it lists, so the new file
isn't copied. The name says what it is and that it becomes `CLAUDE.md`.

### 2. The message carries the path

The CLI formats the `missing` message with `init.SUGGESTED_CLAUDE_MD`,
the absolute path in the running plugin; Vim builds the same path from
`meta_notes#template#GetPluginRoot()`. The path is the one to `cp`, so
it must be the installed plugin's, not a repo-relative one.

## Risks / Trade-offs

- [The suggested file holds one person's habits] → Its intro says to
  edit them; this is a personal plugin.
