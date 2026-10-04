+++
id = "mn-8xpc"
title = "Time report: work and personal time follow the root mode"
kind = "feature"
state = "open"
created_at = "2026-10-04T03:01:00.075Z"
updated_at = "2026-10-04T03:01:00.367216201Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
size = "M"
+++

---
id: 357e
title: "Time report: work and personal time follow the root mode"
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: [47rb]
see: [zyab]
tasks: []
---

# Time report: work and personal time follow the root mode

## The problem

The time report decides work vs non-work in code, the work way:
`NON_WORK_TAGS = {#personal, #off-task, #break}` and everything else,
untagged included, is work (`scripts/time_tracking.py:653-711`; spec
`design/specs/time-report.md:126-133`, fixed that way by 286n). In the
personal root that is backwards: "at home, everything's essentially
personal, unless it's work" (the human, zyab). The notes root's `CLAUDE.md`
tells agents not to tag `#personal` there, but the report still counts the
whole day as work.

## Change, by mode

- **work** (default): unchanged.
- **personal**: untagged time is personal; a `#work` tag (new; alias to
  decide) marks work. The "work window" (`analyze_work_day`, which trims
  `#personal` from the day's ends) doesn't apply. "Work duration" and the
  "Work vs Non-Work" section (`scripts/time_report.py:180-319`) become a
  day total plus a breakdown by tag, with work as one line when present.
- `HIGHLIGHTED_TAGS` and `TAG_GROUPS` (`time_tracking.py:19-25, 799-809`)
  are a hardcoded work list (meetings, recruiting, agile, fence...). Per
  mode defaults; personal: `#exercise`, `#family`, `#maint`/`#home` (the
  human hasn't picked between those last two).
- Tag aliases (`scripts/tags.py:11-19`): `#pers` -> `#personal` is a work
  idea; personal gets a work alias instead.

## Decided with the human, 2026-10-04

- In a personal root, `#work` marks work time.
- Home maintenance is `#maint` (not `#home`). Personal highlighted tags:
  `#exercise`, `#family`, `#maint`, `#work`.
- Highlighted tags stay per-mode lists, not config, until a root needs
  its own.
