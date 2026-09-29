+++
id = "mn-dcc1"
title = "Time Block highlights invisible: metaNotesTableTime consumes both pipes of an am/pm time cell"
kind = "bug"
state = "integrated"
created_at = "2026-09-29T01:42:46.412Z"
updated_at = "2026-09-29T01:48:30.128793Z"
+++

URGENT. In after/syntax/markdown.vim, metaNotesTableTime (|\s*\d\{1,2}:\d\{2}\(am\|pm\)\s*|) consumes both pipes of a cell like '| 8:00am |', so the next cell has no opening pipe and the Time Block cell groups never match (synstack on 'mtg:' shows only metaNotesTimeBlock). Works with '8:00' or '9:00 am', which is why current vader tests pass. Fix: don't consume the pipes (\zs/\ze or lookarounds); check the other cell patterns for the same problem. Add vader tests with the real format: '| 8:00am | mtg: x | y |', '| 12:30pm | pers: y |', and [brackets] and (parens) cells after an am/pm time cell. PATCH bump. Done = ./run_tests.sh && pipenv run pytest test/unit/.

## Thread

### note · agent:manager · 2026-09-29T01:48:30.112Z
Removed metaNotesTime and metaNotesTableTime (both time-of-day highlights, the human's decision) from after/syntax/markdown.vim; the table time pattern consumed both pipes of an am/pm cell so Time Block cell groups never matched. Removed the time-log highlight requirement from the time-log spec and its vader tests; added am/pm row tests in test/syntax.vader. v0.14.1.

### note · agent:manager · 2026-09-29T01:48:30.128Z
integrated: 8c4e539
