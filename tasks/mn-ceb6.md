+++
id = "mn-ceb6"
title = "README Key Mappings: stale after/ftplugin line (ticket jxmu)"
kind = "bug"
state = "integrated"
created_at = "2026-10-03T17:55:39.087Z"
updated_at = "2026-10-03T17:57:55.592155679Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
commit = "5acab33"
+++

---
id: jxmu
title: README Key Mappings says after/ftplugin; mappings are FileType autocmds in plugin/meta_notes.vim
kind: bug
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: []
---

## The ask


# README Key Mappings: stale after/ftplugin line

Spotted by the mn-9b7a worker (2026-10-03). README.md's Key Mappings
section says "Filetype-specific mappings live in
`after/ftplugin/<filetype>.vim` and are buffer-local." There is no
`after/ftplugin/`; the markdown mappings are buffer-local `autocmd
FileType` mappings in `plugin/meta_notes.vim`, as rule `key-mappings`
requires ("Never use `after/ftplugin/`"). Fix the sentence to match.
Docs only; no release needed unless the versioning rule says otherwise.

## Thread

### note · agent:manager · 2026-10-03T17:57:55.592Z
integrated: 5acab33
