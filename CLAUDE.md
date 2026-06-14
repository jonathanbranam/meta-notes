# Claude

Read @README.md and @AGENTS.md

## Key Mapping Convention

All mappings are defined in the plugin, not in the user's `.vimrc`. Use
`<localleader>` for all mappings. Filetype-specific mappings are set via
`autocmd FileType` in `plugin/meta_notes.vim` as buffer-local (`<buffer>`) maps.
Do not use `after/ftplugin/` — it requires the `after/` path to be explicitly
in `runtimepath`, which a plain `set runtimepath+=` does not provide.

