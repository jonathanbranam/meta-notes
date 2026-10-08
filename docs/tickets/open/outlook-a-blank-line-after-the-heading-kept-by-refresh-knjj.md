---
id: knjj
title: "Outlook: a blank line after the heading, kept by refresh"
kind: bug
opened: 2026-10-08
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [pqwv]
tasks: [mn-knjj]
---

## The ask

The human, 2026-10-08 (to the meta-notes aide):

> One note on the Outlook functionality is that I like to have a blank
> line after headers in my Markdown files. I know it's not always
> required, but that's standard Markdown, so let's add that.
>
> Let's just update it to have the blank line, and then the refresh will
> keep the blank line. When we do the refresh, how much does it delete?
> Does it only delete the indents with the labels that the tool creates,
> is that right?

So: `meta-notes outlook` writes a blank line after `### Outlook (as of
...)` (and a blank line after the section, before the next heading, if
the template doesn't already give one), and `outlook refresh` keeps it.

Watch out (the aide, from `scripts/meta_notes/outlook.py`
`refresh_note`): the refresh takes the section as the heading line up to
the first blank line or heading. With a blank line right after the
heading, that block is the heading alone, so today's refresh would write
fresh lines under the heading and leave the old ones below the blank
line: duplicates. The section's end has to be found another way (e.g. up
to the next heading, skipping the blank after the heading), and existing
notes written without the blank line must still refresh correctly.

The human's question, answered from the code: the refresh replaces the
heading's "as of" time and only the lines starting with the labels it
writes (`- Weather:`, `- Temps:`, `- Sun:`, `- Alert:`, `- Moon:`,
`- Wind:`, `- Freeze:`, `- UV:`); every other line in the section is kept
(placed after the generated ones). Keep that, and say it in the help.

Tests: a new note has the blank line; refresh of a note with the blank
line keeps it and doesn't duplicate; refresh of an older note without it
still works; a hand-written line in the section survives. Patch version.

## The human, 2026-10-08 (to the meta-notes aide)

> Yeah, that's fine. I'm not so worried about old notes since I don't
> have any yet, really, but I think we should make it flexible either
> way. If somebody deletes that line or adds a line, it should do the
> refresh appropriately.

So: refresh must not depend on the exact blank-line layout. With the
blank line after the heading deleted, or extra blank lines added, it
still finds the whole section, replaces only its labeled lines, keeps
everything else, and leaves one blank line after the heading. Tests for
both cases.
