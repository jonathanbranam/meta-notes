+++
id = "mn-h7fb"
title = "skills: skip re-running meta-notes conventions when it's already loaded this session"
kind = "chore"
state = "integrated"
created_at = "2026-11-05T13:40:01.698Z"
updated_at = "2026-11-05T14:05:50.445099938Z"
created_by = "external:aide"
watchers = ["external:aide"]
commit = "0db03e6"
summary = "Shipped in 2.34.4 (merge 0db03e6): every skill's Start step skips re-running meta-notes conventions when it already ran this session."
ticket = "h7fb"
+++

docs/tickets/open/skills-skip-re-running-meta-notes-conventions-when-it-s-alre-h7fb.md

## Thread

### note · external:orchestrator · 2026-11-05T13:40:50.363Z
Approved for work: the human, via aide (m-0159, relaying email m-0195, 2026-11-05), verbatim: "More bug reports to investigate and fix." and (m-0181) "Please work on them and LMK when the changes have shipped." Readied by orchestrator@vesta.

### note · agent:manager · 2026-11-05T14:04:06.458Z
Manager review of bridle/conv-once: diff looks right. Not mergeable yet: main moved (2ab56da, an empty sync merge) after you branched, so main is not an ancestor of the branch. Please merge the local main into your branch (git merge main), re-run the check only if the merge brings anything beyond ticket or empty merges, commit, and message me.

### note · external:orchestrator · 2026-11-05T14:05:50.222Z
integrated: 0db03e6
