---
id: mn-8f4y
title: "decode: read words as a stream, piped or pasted, any whitespace between words and lines"
kind: fix
created: 2026-11-24
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: [mn-abjq, mn-exfd]
hold: design
---

## The ask

From the human, meta-notes aide session, 2026-11-24, verbatim:

> if I pipe into meta-notes decode, is it resilient for minor encoding/spacing issues like extra newlines and extra spaces at the start/end of a line or start/end of the entire blob? If not, let's make it more resilient to whitespace; everything should be supported with any amount of whitespace between words or lines

## What works today (aide tested v3.2.1, piped, fake value)

Blank lines before, between and after the lines, extra spaces and tabs at either end of a line or between words, CRLF, no final newline, and uppercase all decode correctly.

## What fails

Words wrapped across lines differently from how `encode` printed them:

- all words on one line: `Error: the header line: expected 5 words, got 13`
- a line broken in the middle (`badom kijos` / `kudoz fadul jobit`): `Error: line 1 of 2: expected 5 words, got 2`

## The fix

Piped or typed, read the input as one stream of words separated by any whitespace, ignoring line breaks. Group the words by the format, which already fixes the count: 5 for the header, then 4 data words plus a check word per line, and the last line's count comes from the length in the header. Check each group's check word and the whole-message digest as now. On a bad check word, name the line (by group) as now.

- **Interactive decode (a terminal) takes the same stream.** The human, verbatim, after aide asked whether typing should also take words across lines: "sure, so also the CLI should work if I just paste in the entire text as well". So pasting the whole encoded text at the prompt, in one go and wrapped any way, decodes. Typing line by line still works: each group is checked as soon as its last word arrives (at the Enter that completes it), so a typo is still caught per line.
- On a bad group when interactive: report it, discard whatever was buffered after it, and ask for that line again (named as now, e.g. "line 2 of 5"). Prompts should not pile up while a paste is being read: prompt only when waiting for more input.
- Words left over after the last line: an error naming the count, unless they are only whitespace.
- No change to the encoded format or to encode.

Update the spec (design/specs/words.md), tests (one word per line, all on one line, mid-line breaks, leftover words; interactive: a whole pasted blob, a bad group then a retype), Vim help and CHANGELOG. Use fake values only.
