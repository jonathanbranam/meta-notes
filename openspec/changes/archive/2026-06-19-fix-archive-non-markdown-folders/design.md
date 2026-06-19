## Context

`MetaNotesArchive` (`autoload/meta_notes/file_ops.vim`) delegates physical moves to `MoveItem` and link rewrites to `UpdateAllWikiLinks` → `scripts/update_links.py`. The pre-fix flow for directories was:

1. Glob for `*.md` files inside the source directory → add each to `result.moves`
2. Run `mv source dest` (moves everything, all file types)
3. If `result.moves` is non-empty, call `UpdateAllWikiLinks` with the per-file entries
4. Per-file entries update `[[project/folder/note]]` links, but never `[[project/folder]]`

Four bugs fell out of this design: no folder-level link updates (for any folder), `.md` extension required for single-file input, and spaces requiring manual escaping at the command line.

## Goals / Non-Goals

**Goals:**
- Folder wiki-links (`[[project/my-folder]]`) are rewritten on archive for all folder types
- `:MetaNotesArchive project/note` works without the `.md` suffix
- `:MetaNotesArchive path with spaces.md` works without backslash escaping
- All fixes covered by vader regression tests

**Non-Goals:**
- Changing how `update_links.py` matches links (the existing regex already handles directory paths correctly)
- Updating folder links when `MoveItem` is called directly (not via `Archive`) — out of scope
- Handling the pre-existing gap where `[[project/folder/note]]` links inside a markdown-containing folder are not updated by the directory-level entry (they are still updated by the individual file entries as before)

## Decisions

### 1. Always append directory to `result.moves` (not just when empty)

`MoveItem` now unconditionally appends `[l:source, l:dest]` to `result.moves` after the `.md` file scan, for any directory move.

**Why not only when `result.moves` is empty**: A folder with `.md` files also has `[[project/folder]]` links that point at the folder, not at a specific file. The individual file entries in `result.moves` only rewrote per-file links. The directory entry is needed in all cases.

**Subfolder links are covered for free**: `update_links.py` uses the pattern `\[\[old_path(/[^\]]*)?]]`, which matches both `[[project/root]]` and `[[project/root/subfolder]]` (and any deeper path). A single directory-level call with `old_path = project/root` therefore rewrites all links into the subtree — no additional entries are needed per subfolder.

**Side effect on `UpdateFileHeader`**: The header-update loop iterates over all `result.moves` entries, including the new directory entry. `UpdateFileHeader` calls `filereadable()` first and returns early for non-files — safe, no change needed there.

**Side effect on `update_links.py` call count**: For folders with `.md` files, `update_links.py` is now called once per `.md` file (for file-level links) plus once for the directory (for folder-level links). The directory call's regex (`[[project/folder/...]]`) overlaps with the file calls, but `re.subn` on already-replaced text finds nothing and makes zero writes — harmless.

### 2. `.md` inference in `Archive`, not in `MoveItem`

When the given path is not found as-is and not a directory, `Archive` tries `path_no_ext + '.md'` before erroring.

**Why in `Archive` not `MoveItem`**: `MoveItem` is a general-purpose move primitive used by both `Archive` and `Rename`. The `.md` inference is a convenience for the user-facing archive command only. Keeping it out of `MoveItem` avoids changing the contract for other callers.

### 3. `-nargs=* <q-args>` for `MetaNotesArchive`

Changed from `-nargs=? <f-args>` to `-nargs=* <q-args>`.

**Why `<q-args>` over `<f-args>`**: `<f-args>` splits on whitespace before passing to the function, so an unescaped space becomes two arguments and vim rejects the command. `<q-args>` passes the entire argument string as one value, preserving spaces.

**Why `-nargs=*` over `-nargs=?`**: With `<q-args>`, a zero-argument invocation passes an empty string rather than no argument at all. `-nargs=?` with `<q-args>` would pass `""` when the user types `:MetaNotesArchive`, hitting `a:0 > 0` as true. Switching to `-nargs=*` keeps the same arity semantics and the empty-string guard in `Archive` (`a:1 !=# ''`) handles the no-arg case correctly.

## Risks / Trade-offs

- **Slightly more `update_links.py` invocations for markdown folders**: One additional Python subprocess call per archive of a markdown-containing folder. For a personal notes plugin this is negligible.
- **`-nargs=*` allows arbitrarily many words**: Typing `:MetaNotesArchive foo bar` passes `"foo bar"` as the path, which fails gracefully with "Path not found." No silent data loss, but the error message may be confusing for users who expect a "too many arguments" error.
