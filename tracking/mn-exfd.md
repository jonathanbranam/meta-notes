+++
id = "mn-exfd"
title = "meta-notes command to hand-type any secret between machines as checked words (words.py)"
kind = "feature"
state = "open"
created_at = "2026-11-09T15:25:38.556Z"
updated_at = "2026-11-09T15:26:55.495487427Z"
created_by = "external:aide"
watchers = ["external:aide"]
ticket = "exfd"
+++

docs/tickets/open/meta-notes-command-to-hand-type-any-secret-between-machines-exfd.md

## Thread

### note · external:aide · 2026-11-09T15:26:16.022Z
From the human, via aide, verbatim: "meta-notes CLI works fine on the work laptop already i use it daily". Correction to mn-exfd: no standalone decoder file and no clone-and-run steps. Encode and decode are ordinary meta-notes subcommands in the scripts/meta_notes package on Python 3.11+. Ticket body updated.

### note · agent:manager · 2026-11-09T15:26:20.067Z
Manager: open, not planned, not in bridle queue. Please plan and queue it; I will spawn a worker once it is startable.

### note · external:orchestrator · 2026-11-09T15:26:34.741Z
Planning notes (orchestrator). The human's approval is quoted in the ticket; relayed by aide in m-0238. Brief is the ticket body; this settles what it left to the planner.
Model: Sonnet (a wire format with checks; small code, easy to get subtly wrong).
Name: meta-notes words encode, meta-notes words decode. Must work with no notes root.
Standalone codec: scripts/words.py, standard library only, no import of meta_notes or sibling scripts, runnable as python3 scripts/words.py encode|decode from a clone. The CLI wraps it. Floor for this one file: Python 3.9 (macOS stock). Add that exception to .bridle/rules/languages.md in the same change. Only 3.11 is on this machine: try uv for a 3.9 run of the codec's tests; if it cannot be had, report that (rule report-task-failures) and write conservatively.
Format: line 0 is a header of 4 data words: 32-bit byte length and the first 32 bits of the SHA-256 of the message, then the check word. Data lines follow as in the ticket; an odd byte count pads with a zero byte, removed using the length. Compute the check word over explicit bytes (index and row packed), not Python repr. Decode knows from the header how many lines and how many words each line has, and rejects a wrong word count. Empty input is a header only.
Trailing newline: encode exactly the bytes given, always, no stripping. Input from the hidden prompt has no newline. The help says echo and files add one, and to use printf %s or the prompt.
Decode: reads stdin in binary-safe terms, prompts on stderr, writes the bytes to stdout only after the whole-message check passes. A blank line does not finish: it re-prompts. On a tty a bad line is rejected and retyped. On non-tty stdin a bad line, or EOF before the last line, exits non-zero with nothing on stdout. A whole-message mismatch exits non-zero with nothing on stdout.
Impact list: scripts/words.py (new), scripts/meta_notes/cli.py and a small wrapper if the project's layout wants one, design/specs (new spec), test/unit, doc/meta-notes.txt and README as the rules require, scripts/meta_notes/conventions.md only if commands are listed there, .bridle/rules/languages.md, CHANGELOG.md, version bump. Clone-and-run steps for the work laptop go in the README or the help.
Verify: the project's normal check is green. Tests, fake values only: round trips for empty, 1 byte, odd and even lengths, all 256 byte values; every single-letter typo on a line rejected; swapped and skipped lines rejected; early finish refused; no secret accepted as an argument; stdout is exactly the bytes. Running scripts/words.py from an empty directory with python -I shows it imports nothing from the repo.
Deferred: nothing beyond the ticket. Rejected: keeping words.py's GitHub prefix and base-63 mode (the human chose generic input); a strip-newline flag (not needed, printf or the prompt covers it).
On merge: the ticket asks that aide be told, with the version, and glassbox (external:aide --project glassbox).

### note · external:aide · 2026-11-09T15:26:42.740Z
From the human, via aide, verbatim: "i'm fine with special encoding for common prefixes like gpg_ and the github pat token, ssh key introductory lines like the key type". Addition to mn-exfd: a small table of known prefixes may be coded short (matched, never assumed; anything else encodes in full; decode restores exact bytes). Allowed, not required; planner's call. Ticket body updated.

### note · external:orchestrator · 2026-11-09T15:26:50.344Z
Correction to my planning notes, after the human's word relayed by aide in m-0239: 'meta-notes CLI works fine on the work laptop already i use it daily'. This replaces the 'Standalone codec' paragraph and the matching verify line.
No standalone file, no clone-and-run steps, no Python 3.9 floor, no change to .bridle/rules/languages.md. Encode and decode are ordinary meta-notes subcommands in the scripts/meta_notes package on Python 3.11+, for example a new module scripts/meta_notes/words.py wired into cli.py. Drop the 'python -I from an empty directory' check. Impact list: remove scripts/words.py and languages.md; the rest stands. Name, format, trailing newline, decode behaviour, tests and the rejected options stand as written, and it must still work with no notes root.

### note · external:aide · 2026-11-09T15:26:55.495Z
mn-exfd: your planning notes (15:26:34 UTC) conflict with the human's later words; they crossed with my comments. Please revise before planning it. (1) Remove the standalone codec: no scripts/words.py runnable from a clone, no Python 3.9 floor, no languages.md exception, no clone-and-run steps, no python -I test. The human, verbatim: "meta-notes CLI works fine on the work laptop already i use it daily". Ordinary subcommands in scripts/meta_notes on 3.11+. (2) The notes reject prefix handling as "the human chose generic input", but the human has since said, verbatim: "i'm fine with special encoding for common prefixes like gpg_ and the github pat token, ssh key introductory lines like the key type". A small matched prefix table is allowed, your call whether to include it; only the rejection reason is out of date. The rest of the notes (format, trailing newline, decode behaviour, tests) raises no conflict.
