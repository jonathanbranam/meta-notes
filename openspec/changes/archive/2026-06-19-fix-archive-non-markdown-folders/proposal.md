## Why

`MetaNotesArchive` had four bugs: (1) archiving any folder — with or without markdown files — did not update wiki-links pointing to the folder itself (e.g. `[[project/my-folder]]`); (2) archiving a folder containing only non-markdown files (e.g., JPGs) did not update wiki-links pointing to that folder (a consequence of bug 1, now also explicitly tested); (3) passing a file path without the `.md` extension gave "Path not found" even when the `.md` file existed; (4) paths with spaces required backslash-escaping at the vim command line. A fifth suspected bug — that the directory itself was not physically moved — was investigated and found to already work correctly; a regression test was added.

## What Changes

- **Folder wiki-link update (all folders, including subfolders)**: `MoveItem` now always appends the directory itself to `result.moves` after scanning for `.md` files. This ensures `UpdateAllWikiLinks` is called with a directory-level entry, updating `[[project/my-folder]]` → `[[archive/project/my-folder]]` for any archived folder regardless of its contents. Because `update_links.py`'s regex matches `[[old_path/anything]]`, links to subfolders (e.g. `[[project/root/subfolder]]`) are also rewritten to `[[archive/project/root/subfolder]]` in the same pass.
- **Wiki-link update for non-markdown folders**: A direct consequence of the above fix. Previously `result.moves` was empty for no-markdown folders, so `UpdateAllWikiLinks` was skipped entirely.
- **`.md` extension inference**: `Archive` now tries `path.md` automatically when the given path isn't found as-is, so `:MetaNotesArchive project/my-note` works the same as `:MetaNotesArchive project/my-note.md`.
- **Space-safe command invocation**: Command changed from `-nargs=? <f-args>` to `-nargs=* <q-args>`, so paths with spaces no longer require backslash-escaping at the vim command line.
- **Regression test — physical folder move**: Confirmed that archiving a folder of only non-markdown files physically moves the directory (the `mv` command always ran).
- **New tests**: Wiki-link update for non-markdown folder; wiki-link update for markdown-containing folder; `.md` extension inference; files with spaces.

## Capabilities

### New Capabilities

_(none — these are bug fixes and regression tests for existing behavior)_

### Modified Capabilities

- `archive`: Four behaviors changed. (1) Wiki-links pointing at a folder are updated on archive for all folder types (markdown-containing and non-markdown). (2) File paths may omit the `.md` extension. (3) The vim command accepts paths with spaces without backslash escaping.

## Impact

- `autoload/meta_notes/file_ops.vim`
  - `MoveItem` directory branch: always append `[l:source, l:dest]` to `result.moves` after the `.md` file scan, ensuring folder-level wiki-link updates fire unconditionally
  - `Archive`: empty-string arg guard for `<q-args>` compat
  - `Archive`: `.md` fallback inference when exact path not found
- `plugin/meta_notes.vim`: `MetaNotesArchive` changed to `-nargs=* <q-args>`
- `test/archive.vader`: six new test cases (physical non-markdown folder move, wiki-link update for non-markdown folder, wiki-link update for markdown folder, wiki-link update for subfolder of archived folder, no-extension path, spaces in filename)
