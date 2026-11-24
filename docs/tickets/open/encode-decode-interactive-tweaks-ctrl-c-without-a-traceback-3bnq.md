---
id: mn-3bnq
title: "encode/decode interactive tweaks: Ctrl-C without a traceback; no blank line between encode -i lines"
kind: fix
created: 2026-11-24
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: [mn-jjc7, mn-8f4y]
hold: design
---

From the human, meta-notes aide session, 2026-11-24, after retesting v3.3.0. Verbatim: "make a ticket for small tweaks; don't ready it:"

> 1. KeyboardInterrupt / Ctrl-C in either interactive input should be caught and don't show the stack trace
> 2. encode -i should eat the newline or not print one or somehow not have a blank line between each line. see below:

```
 % meta-notes encode -i 'laksdf j;lkasjd flkasjd flkasjdf klasdjf '
the header line: babab babop dodij mamum vofog

line 1 of 6: bados kajor latoh kimob gahug

line 2 of 6: komur kudor kajug konoh budud

line 3 of 6: fadok kudor kajug konoh ninib
```

**Hold: the human said not to ready this ticket.** Wait for their go.

## The ask

1. **Ctrl-C without a traceback.** In every interactive input of encode and decode (the `*` secret prompt, the Enter waits of `encode -i`, decode's prompts), catch KeyboardInterrupt: print no stack trace, end the line so the shell prompt starts clean, leave the terminal mode restored (the `*` prompt's raw mode), print nothing to stdout, and exit non-zero (130, the usual code for Ctrl-C). A decode cut short this way still prints no partial secret.
2. **No blank line between `encode -i` lines.** The Enter the user presses shows up as an empty line under each labelled line. Make the output one labelled line per row, with no blank lines between them. For example, don't echo the Enter (read it without echo), or print the line without its own newline and let the user's Enter end it. Expected:

   ```
   the header line: babab babop dodij mamum vofog
   line 1 of 6: bados kajor latoh kimob gahug
   line 2 of 6: komur kudor kajug konoh budud
   ```

Tests: Ctrl-C at each prompt (no traceback, exit 130, terminal restored, nothing on stdout); `encode -i` output in a pseudo-terminal has no blank lines. CHANGELOG under a patch version.
