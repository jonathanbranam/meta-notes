+++
id = "mn-65ad"
title = "Vim: GitGutter off in notes buffers (ticket bawv)"
kind = "feature"
state = "integrated"
created_at = "2026-10-03T17:31:11.489Z"
updated_at = "2026-10-03T17:34:12.127625023Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
commit = "9d36096"
+++

---
id: bawv
title: "Vim: GitGutter off in notes buffers"
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: []
---

## The ask


# Vim: GitGutter off in notes buffers

## The ask

The human, 2026-10-03 (relayed by the notes advisor, m-0268): "I have Git
Gutter installed as a plugin, and I love it for my work stuff. I do not
want to see Git Gutter in my notes, so I always want that disabled... If
it's possible somehow through the meta notes plugin to disable that for
the notes folder, that's probably the right place to do it."

## Shape

`:GitGutterDisable` is global and would turn it off for work files too.
Disable it per buffer for notes buffers only (the buffers autosave and
autoreload already treat as notes): `:GitGutterBufferDisable`, guarded by
`exists(':GitGutterBufferDisable')` so the plugin is harmless without
GitGutter. An option, `g:meta_notes_disable_gitgutter`, default on.
Document it in `:help` and the README. Minor release.

(Also from the human: autoreload works; "I actually saw the change come
through while I was viewing the daily note... It worked great.")

## Thread

### note · agent:manager · 2026-10-03T17:34:12.127Z
integrated: 9d36096
