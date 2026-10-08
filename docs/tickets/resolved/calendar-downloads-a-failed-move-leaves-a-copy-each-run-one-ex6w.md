---
id: ex6w
title: "Calendar downloads: a failed move leaves a copy each run; one setting instead of two"
kind: bug
opened: 2026-10-08
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [rgev]
tasks: [mn-ex6w]
closed: 2026-10-08T15:02:45Z
---

## The ask

The human, 2026-10-08 (to the meta-notes aide), after trying the
Calendar Downloads pickup (rgev, v2.27.0) on their work Mac at v2.29.0:

> the path exists; also just relizing that could be one config var
> instead of two!
>
> it created FIVE! copies of the zip but never moved the original. that
> was from the agent; when I ran it myslef, it actually did move the file
> finally (not copy). so, maybe the agent was sandboxed from doing the mv
> from ~/Downloads on my work claude sandbox

## 1. A failed move leaves a copy in the cache, every run (bug)

`pick_up_downloads` (`scripts/meta_notes/calendar.py`) uses
`shutil.move`. When a rename isn't possible, `shutil.move` copies the file
and then deletes the source. In the agent's Claude Code sandbox, reading
`~/Downloads` is allowed but deleting from it isn't, so the copy
succeeds, the delete fails, and the original stays. The next run finds it
again and makes another copy, and so on (five here, likely capped by the
keep-5 pruning). When run by the human outside the sandbox, the move worked.

Wanted: a move is all or nothing. If the source can't be removed, remove
the copy just made (or check first that the source can be deleted) and
warn once, e.g. "Could not move <file> out of ~/Downloads (permission
denied); run `meta-notes calendar` outside the sandbox or allow writes to
~/Downloads". Never leave a duplicate. Also don't re-copy a file already
picked up (e.g. same size and mtime as an export in the cache).

## 2. One setting instead of two (the human's idea)

Replace `downloads` + `downloads_pattern` with one path-and-glob, e.g.
`downloads = "~/Downloads/*.ical.zip"`. Keep reading the two-key form for
a while (or migrate it), since it shipped in v2.27.0.

## 3. Say when nothing happens (the aide's suggestion)

Today a missing key, or a pattern that matches nothing, does nothing
silently. When the setting is present but matches no file, the run could
say so in verbose or `--json` output (not a warning every run when there
simply is no new export; that's normal).

Tests for 1 (simulate a source that can't be deleted: no copy left, one
warning, idempotent across runs) and 2. Version per versioning.md.

## The human's design for 1, 2026-10-08 (replaces "Wanted" under 1)

> 1) we need to not only copy a file b/c it might match one we have
> already
> 2) check if the latest file matches (idk, size only? timestamps won't
> match, SHA / hash it)
> 3) if the latest Downloads file is newer and SHA doesn't match, copy it
> over.

So: before copying, hash (e.g. SHA-256) the newest matching file in the
downloads folder and compare it with the exports already in the cache.
Copy it in only if it's newer than the newest cached export and its hash
matches none of them. Then remove the original when that's allowed (a
move); when it isn't (the agent's sandbox), leave it, with no copy made
and no repeated warning, since the cache already has it. Repeated runs
never make duplicates. Size alone isn't enough; the hash decides.

The human, on the effect today:

> sounds right; the current solution it's copying the file every time it
> runs and the cache isn't working at all (due to the sandbox)

Every run in the sandbox makes a new export file with a new name, so the
parsed-calendar cache (keyed by the export's name, size and mtime) never
hits and every `meta-notes calendar` reparses. The hash check above fixes
both. Test: two runs in a row with an undeletable source reuse the cache
on the second.
