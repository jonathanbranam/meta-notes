## 1. Tests — Regression (non-markdown folder move)

- [x] 1.1 Add vader test confirming a folder of only non-markdown files (JPGs) is physically moved to the archive location (`test/archive.vader`)

## 2. Fix — Folder wiki-link updates

- [x] 2.1 In `MoveItem` directory branch, unconditionally append `[l:source, l:dest]` to `result.moves` after the `.md` file scan so `UpdateAllWikiLinks` is called for every directory move (`autoload/meta_notes/file_ops.vim`)
- [x] 2.2 Add vader test: archiving a folder of only non-markdown files updates `[[project/folder]]` links (`test/archive.vader`)
- [x] 2.3 Add vader test: archiving a markdown-containing folder updates `[[project/folder]]` links (`test/archive.vader`)
- [x] 2.4 Add vader test: archiving a folder updates `[[project/folder/subfolder]]` links (subfolder paths covered by `update_links.py` regex) (`test/archive.vader`)

## 3. Fix — .md extension inference

- [x] 3.1 In `Archive`, after the `filereadable` / `isdirectory` checks, try `path_no_ext + '.md'` before erroring when neither check passes (`autoload/meta_notes/file_ops.vim`)
- [x] 3.2 Add vader test: `:MetaNotesArchive project/note` (no extension) archives `project/note.md` (`test/archive.vader`)

## 4. Fix — Space-safe command invocation

- [x] 4.1 Change `MetaNotesArchive` command definition from `-nargs=? <f-args>` to `-nargs=* <q-args>` (`plugin/meta_notes.vim`)
- [x] 4.2 Guard `Archive` against empty-string argument passed by `<q-args>` when no arg given: `(a:0 > 0 && a:1 !=# '') ? a:1 : expand('%:p:.')` (`autoload/meta_notes/file_ops.vim`)
- [x] 4.3 Add vader test: archiving a file whose name contains spaces works without backslash escaping (`test/archive.vader`)

## 6. Missing tests — uncovered spec scenarios

- [x] 6.1 Add vader test: `:MetaNotesArchive project/nonexistent` (no-ext path that resolves to neither a file nor a `project/nonexistent.md`) reports "Path not found" and makes no changes (`test/archive.vader`, spec scenario at spec.md line 39–42)
- [x] 6.2 Add vader test: archiving `project/root` rewrites a deeply-nested link `[[project/root/a/b/c]]` to `[[archive/project/root/a/b/c]]` (`test/archive.vader`, spec scenario at spec.md line 28–31)

## 5. Verification

- [x] 5.1 Run full archive test suite (`./run_tests.sh test/archive.vader`) — 20/20 pass
