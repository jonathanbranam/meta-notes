---
id: key-mappings
severity: must
roles: [manager, worker]
---
All key mappings are defined in the plugin, in `plugin/meta_notes.vim`, not
in the user's `.vimrc`. Use `<localleader>` for every mapping.
Filetype-specific mappings are buffer-local (`<buffer>`) maps set from
`autocmd FileType` in `plugin/meta_notes.vim`. Never use `after/ftplugin/`.

Why: `after/` is only searched when it's explicitly in `runtimepath`, and a
plain `set runtimepath+=` (how users install this plugin) doesn't add it, so
mappings there silently never load.
