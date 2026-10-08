+++
id = "mn-knjj"
title = "Outlook: a blank line after the heading, kept by refresh"
kind = "bug"
state = "planned"
created_at = "2026-10-08T12:41:27.153Z"
updated_at = "2026-10-08T12:54:48.990424634Z"
created_by = "external:aide"
watchers = ["external:aide"]
+++

original id: knjj
docs/tickets/open/outlook-a-blank-line-after-the-heading-kept-by-refresh-knjj.md

## Thread

### note · agent:outlook-blank · 2026-10-08T12:54:48.990Z
Done, fd598d7 (v2.29.1). outlook prints a blank line after the heading; refresh finds the section as heading..next heading, drops generated lines, keeps others, and leaves exactly one blank after the heading and one before the next heading (tests: missing, extra, existing blank, hand-written line kept). Templates unchanged (renderer already adds the trailing blank). Checks: vader 184/184 (458 assertions), pytest 1619 passed 1 skipped, bridle spec check --require-ids 0 errors. Spec s-0af1 added, help updated. No CHANGELOG file in repo.
