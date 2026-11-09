---
id: mn-abjq
title: encode and decode commands with --algorithm (default mn-proquint), replacing words; accept text as an argument
kind: feature
created: 2026-11-09
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: [mn-exfd]
---

## The ask

From the human, meta-notes aide session, 2026-11-09, after mn-exfd shipped in v2.38.0.

Verbatim:

> "words" is kind of weird as the base command. what we're really doing is either encoding or decoding something and "words" is ONE way to encode/decode something and we will likely add more in the future.

> meta-notes
> * encode --algorithm words
> * decode --algorithm words

> also, piping should work as should specifying the "secret" on the CLI since it may not actually be "secret" in the sense of sensitive

> I would also make "words" the default algorithm so this works:
> meta-notes encode $MY_TOKEN
> meta-notes decode

On the name: "I agree the name "words" should be improved to be more specific to what we're doing", then "something for now `mn-proquint` is fine".

## What to build

1. **New commands** `meta-notes encode [TEXT]` and `meta-notes decode`, with `--algorithm` / `-a`. The only algorithm is `mn-proquint`, and it is the default. The wire format is unchanged from v2.38.0.
2. **Remove** `meta-notes words encode` and `words decode`, with no alias (aide's recommendation: they shipped the same day and only the human uses them). The planner picks the version bump under `.bridle/rules/versioning.md`.
3. **Input for encode, in order** (aide's recommendation; the human's go, verbatim, in reply to "Say 'go' and I'll send it to the orchestrator with that order": "Go"): a TEXT argument wins and stdin is not read; otherwise piped stdin; otherwise the hidden prompt. Not an error when both are present: agents and scripts often have an open, empty stdin.
4. **Text starting with dashes need not work as an argument.** The human, verbatim: "IDC if the ----- works as a CLI argument or not. That can work only by pipe of needed." So PEM and GPG input goes by pipe, and no special handling is needed; the help says so. Space-containing arguments must round trip when quoted. Accepting an argument at all reverses mn-exfd's "never accept the secret as a command-line argument", by the human's words above.
5. **Help** shows the argument quoted, says a literal typed there lands in shell history and a value is briefly visible in `ps`, that the hidden prompt is for real secrets, and that binary must be piped (arguments can't hold NUL bytes).
6. **decode takes no text argument for now** (aide's recommendation; easy to add with a one-line algorithm). No auto-detection of the algorithm.

Update specs, tests, Vim help, README and CHANGELOG, including the rename of `:help meta-notes-cli-words`. Fake values only in tests.

## Not now

The human sees more axes than the one flag, and chose not to model them yet. Verbatim: "algorithm - literally what is the algorithm used, regardless of input method", "hand typing - how the algorithm will be used", "check digits/crc/etc - that checking is added to the encoding", "these feel like distinct axes, but let's KISS for now."
