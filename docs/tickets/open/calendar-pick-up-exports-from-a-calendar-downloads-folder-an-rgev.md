---
id: rgev
title: "Calendar: pick up exports from a Calendar Downloads folder and move them into the cache"
kind: feature
opened: 2026-10-08
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: []
---

## The ask

The human, 2026-10-08 (to the meta-notes aide):

> Oh, I forgot. I do have a really specific thing I want. At work, when I
> download my Gmail, I don't have any control over it. My calendar just
> goes straight to my Downloads folder, and then I have to find the file
> and drag it into the meta-notes cache. The file names clash because if I
> move the file every time, then the old one has the same name. If I
> leave them in Downloads and copy them, then it'll add a 1, 2, 3, 4, 5,
> but I don't want two copies of every calendar, so that's super annoying.
>
> I want to add another configuration for a folder that's outside of
> meta-notes, so it's not the cache. Call it the Calendar Downloads
> folder. We need a file match pattern to indicate what the file should
> look like, and this should just take care of everything. When calendar
> runs, it should go check that mapped folder. If there's a new file that
> matches the glob pattern, then move it and rename it into the cache
> with today's date.
>
> Since you're doing this automatically, we can just do hours and minutes
> as well, so yyyy mm dd hh mm. I'm on a Mac, so don't put a colon in
> there, but you can separate them with underscores or dashes. I don't
> even care, just all smashed together, it doesn't matter. We have
> pruning, right, so those get pruned later.

So:

- **Config:** two keys in the `[calendar]` table of `.meta-notes`, e.g.
  `downloads = "~/Downloads"` (the Calendar Downloads folder, outside the
  notes root; `~` expanded) and `downloads_pattern = "<glob>"` (what a
  calendar export there looks like). Key names are the implementer's
  call; both are optional and nothing changes without them.
- **When `meta-notes calendar` runs:** look in that folder for files
  matching the glob, and **move** (not copy) each into
  `.meta-notes-cache/ics/`, renamed with a timestamp to the minute and no
  colon, e.g. `2026-10-08_0915.zip` (keep the extension; `.zip` or
  `.ics`). The existing newest-by-mtime pick and keep-5 pruning
  (`KEEP_EXPORTS`) then apply as they do now.
- **For the implementer to settle and note** (the human said "I don't
  even care" about the separators):
  - The human said "today's date"; the move time and the file's own
    modification (download) time are nearly the same. Prefer whichever
    keeps the newest-export pick right; a move must keep the file's
    mtime, or set it so the moved file counts as newest.
  - Two files arriving in the same minute: don't overwrite; add seconds
    or a suffix.
  - A move that fails (permissions, folder missing) warns and the
    calendar still runs from the cache.
- Docs: README Calendar section, `:help meta-notes-cli-calendar` and
  `meta-notes-config`. Minor version.
