---
id: j8kw
title: "Syntax: the ### Time Block heading loses its markdown heading highlight in daily notes"
kind: bug
opened: 2026-10-08
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: [mn-j8kw]
closed: 2026-10-08T03:48:41Z
---

## The ask

The human, 2026-10-08 (to the meta-notes aide):

> Also can you check if anything is messing up my local Highlights on
> markdown headings? For work I have some nice orange highlights that
> stopped working for ### Time Block if we have that just remove it.

Found (the aide, checked in Vim with the plugin's runtime): in daily
notes, the `metaNotesTimeBlock` region in `after/syntax/markdown.vim`
starts on the `### Time Block` line itself:

    syntax region metaNotesTimeBlock transparent keepend
          \ start=/^###\s\+Time Block\s*$/hs=e+1 end=/^#\{1,3}\s/me=s-1

`hs=e+1` only moves where its highlight starts; the region still matches
the heading line, so `markdownH3` never gets it. The synstack at column 1:

    ### Log         -> markdownH3, markdownH3Delimiter
    ### Time Block  -> metaNotesTimeBlock      (no markdownH3)
    ## Notes        -> markdownH2, markdownH2Delimiter

So the human's own heading colors (orange, from their colorscheme or
vimrc) don't apply to that one heading. The comment above the region says
"The heading line itself is left to the markdown heading group", which is
the intent; the code doesn't do it.

Fix: start the region on the line after the heading (e.g. a zero-width
start just past the heading's newline, or a lookbehind), so the heading
line keeps `markdownH3` and the cell highlights keep working. "Remove it"
is the human's fallback: if the region can't start after the heading,
remove what takes the heading line, not the cell highlights. A vader test
that `### Time Block` has `markdownH3` in a daily note. Patch version.
