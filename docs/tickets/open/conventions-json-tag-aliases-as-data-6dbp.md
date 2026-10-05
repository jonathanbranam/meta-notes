---
id: 6dbp
title: "conventions --json: tag aliases as data"
kind: feature
opened: 2026-10-05
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: []
---

## The ask

meta-notes-ui (mu-ruun) needs the tag aliases to fold #mtg into #meeting and the like. They're a hardcoded table in scripts/tags.py chosen by the root's mode, and `meta-notes conventions` shows them only as prose. Add a `tag_aliases` object (alias -> target, without the #, for the root's mode) to `meta-notes conventions --json`, from the same table, so other tools read them instead of copying it. Text output unchanged. Minor bump; update :help and the conventions spec if it covers the JSON.
