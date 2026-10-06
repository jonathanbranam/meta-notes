+++
id = "mn-cys2"
title = "task add puts the task under ## Tasks, not after the Time Block"
kind = "bug"
state = "open"
created_at = "2026-10-06T14:48:13.910Z"
updated_at = "2026-10-06T14:50:19.306098443Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
+++

original id: cys2
docs/tickets/open/task-add-puts-the-task-under-tasks-not-after-the-time-block-cys2.md

## Thread

### note · external:orchestrator · 2026-10-06T14:49:05.325Z
Scope added (the human via advisor, m-0101): also fix the flat 'A done task gets ✅' sentence in conventions.md line 13 to state the due-today exception. Details on the ticket, section 'Also: the done stamp's due-today exception'.

### note · agent:manager-1 · 2026-10-06T14:49:10.787Z
manager: scope addition (conventions.md line 13 done-stamp due-today exception; see the ticket section 'Also: the done stamp's due-today exception') applies to this task. Worker add-under-tasks: please include it in the same branch, with the spec/conventions/doc wording matching what the ticket says.

### note · external:advisor · 2026-10-06T14:50:00.457Z
From the human, via advisor (2026-10-06): "It should look for a header called Tasks if that exists it should add tasks there. If it doesn't exist and no line number, tasks should go at the top of the file below the H1 file header after a blank space." (So: no --line -> under ## Tasks if present; else right after the H1 title and a blank line, not at the end of the file.)

### note · agent:add-under-tasks · 2026-10-06T14:50:19.306Z
done: task add without --line inserts at end of ## Tasks (v2.26.1). Vader 183/183, pytest 1555 passed 1 skipped, bridle spec check --require-ids 0 errors. Commit c379968
