+++
id = "mn-abjq"
title = "encode and decode commands with --algorithm (default mn-proquint), replacing words; accept text as an argument"
kind = "feature"
state = "planned"
created_at = "2026-11-09T17:15:51.417Z"
updated_at = "2026-11-09T18:18:31.800629357Z"
created_by = "external:aide"
watchers = ["external:aide"]
ticket = "abjq"
+++

docs/tickets/open/encode-and-decode-commands-with-algorithm-default-mn-proquin-abjq.md

## Thread

### note · external:aide · 2026-11-09T18:07:19.944Z
From the human, via aide, verbatim: "Go". Sent to the orchestrator to plan and build.

### note · external:aide · 2026-11-09T18:07:39.957Z
From the human, via aide, verbatim: "IDC if the ----- works as a CLI argument or not. That can work only by pipe of needed." Change to mn-abjq item 4: text starting with dashes need not work as an argument; PEM and GPG go by pipe, no special handling, and the help says so. Ticket body updated. If a worker has started, please pass this on.

### note · agent:manager · 2026-11-09T18:07:50.308Z
Manager: open, not planned, not in bridle queue. Please plan and queue it; I will spawn a worker once it is startable.

### note · external:orchestrator · 2026-11-09T18:08:13.375Z
Planning notes (orchestrator). Approval: the human's "Go", and the change to item 4, are on this thread, relayed by aide (m-0272, m-0273). The ticket body as of fdd2f28 is the brief: item 4 means NO special handling for text starting with dashes; those inputs go by pipe and the help says so.

Model: Sonnet (input-order logic, and specs and docs to rewrite together).

Impact list: scripts/meta_notes/cli.py (replace the words parser with encode and decode, input order for encode), scripts/meta_notes/__init__.py (version), the words module only if the handlers need a small change, design/specs/words.md, test/unit/test_words.py, doc/meta-notes.txt (rename the meta-notes-cli-words help tag and section), README.md, CHANGELOG.md.

Version: removing `words` is an incompatible CLI change, so under .bridle/rules/versioning.md this is MAJOR: 3.0.0.

Verify: the project's normal check is green, once. Tests with fake values only: encode then decode round trip with the default algorithm and with -a mn-proquint; TEXT argument wins and stdin is not read, including with an open, empty stdin; piped stdin works when there is no argument; a quoted argument with spaces round trips; an unknown algorithm is an error; `meta-notes words` is gone with no alias; a line encoded by v2.38.0 still decodes (wire format unchanged). Help text covers everything in item 5, and says dash-leading text goes by pipe.

Deferred: a text argument for decode, not yet because the human accepted leaving it out and it is one line to add later. More algorithms and the human's other axes (hand typing, check digits), not yet because the human said "let's KISS for now".

Rejected: an alias for `words` (shipped the same day, only the human uses it); an error when both an argument and stdin are present (agents and scripts often have an open, empty stdin); auto-detecting the algorithm; handling for arguments that start with dashes (the human, item 4). Keep the spec and test file names unless renaming is trivial; internal names are out of scope.
