+++
id = "mn-j8kw"
title = "Syntax: the ### Time Block heading loses its markdown heading highlight in daily notes"
kind = "bug"
state = "integrated"
created_at = "2026-10-08T03:25:40.378Z"
updated_at = "2026-10-08T03:47:44.247256819Z"
created_by = "external:aide"
watchers = ["external:aide"]
commit = "b74df41"
summary = "Time Block region now starts after the heading newline (lookbehind), so the ### Time Block line keeps markdownH3; cell highlights unchanged. Vader test and spec scenario added. v2.28.1."
ticket = "j8kw"
+++

docs/tickets/open/syntax-the-time-block-heading-loses-its-markdown-heading-hig-j8kw.md

## Thread

### note · agent:timeblock-hl · 2026-10-08T03:47:24.363Z
mn-j8kw done on bridle/timeblock-hl (fix commit 1234327, merge of main a31dff4), v2.28.1.

Fix: after/syntax/markdown.vim, the metaNotesTimeBlock region now starts after
the heading's newline via a lookbehind, start=/\(^###\s\+Time Block\s*\n\)\@<=/.
The heading line gets markdownH3 and no metaNotesTimeBlock; cell highlights
unchanged. (Tried \zs$ and \n starts first: they broke the cells, so not used.)

Tests:
- vader: ./run_tests.sh: Success/Total 184/184 (assertions 458/458), incl. new
  "The Time Block heading keeps its markdown heading highlight" in test/syntax.vader.
- pytest: uv run pytest test/unit/: 1610 passed, 1 skipped (the skip predates
  this change, not in my files).
- bridle spec check --require-ids: 31 files, 0 errors, 0 warnings.

Spec: design/specs/time-log.md new scenario s-6f8d (r-e44b). Help: doc/meta-notes.txt.
No CHANGELOG exists in this repo, so none added.

### note · agent:manager-2 · 2026-10-08T03:47:42.470Z
integrated: b74df41
