+++
id = "mn-dcc1"
title = "Time Block highlights invisible: metaNotesTableTime consumes both pipes of an am/pm time cell"
kind = "bug"
state = "planned"
created_at = "2026-09-29T01:42:46.412Z"
updated_at = "2026-09-29T01:42:51.135826Z"
+++

URGENT. In after/syntax/markdown.vim, metaNotesTableTime (|\s*\d\{1,2}:\d\{2}\(am\|pm\)\s*|) consumes both pipes of a cell like '| 8:00am |', so the next cell has no opening pipe and the Time Block cell groups never match (synstack on 'mtg:' shows only metaNotesTimeBlock). Works with '8:00' or '9:00 am', which is why current vader tests pass. Fix: don't consume the pipes (\zs/\ze or lookarounds); check the other cell patterns for the same problem. Add vader tests with the real format: '| 8:00am | mtg: x | y |', '| 12:30pm | pers: y |', and [brackets] and (parens) cells after an am/pm time cell. PATCH bump. Done = ./run_tests.sh && pipenv run pytest test/unit/.
