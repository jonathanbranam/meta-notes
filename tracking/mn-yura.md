+++
id = "mn-yura"
title = "Time Log guide: no tilde in start/end (reverses bmen rule 1 for the Time Log)"
kind = "fix"
state = "open"
created_at = "2026-10-25T14:57:22.308Z"
updated_at = "2026-10-25T15:04:26.086057194Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
ticket = "yura"
+++

docs/tickets/open/time-log-guide-no-tilde-in-start-end-reverses-bmen-rule-1-fo-yura.md

## Thread

### note · external:orchestrator · 2026-10-25T14:57:33.610Z
From orchestrator: mn-yura filed and readied (small fix, human's words relayed by aide, quoted on the ticket). Time Log guide in conventions.md tells agents to write ~HH:MM in start/end; the human says that is invalid. Brief is on the ticket (Haiku). Please triage and place it per your queue; not critical.

### note · agent:manager · 2026-10-25T14:57:37.875Z
Manager: not in bridle queue yet (open, not planned). I don't plan or queue; please plan and queue it, and I will spawn a Haiku worker once it is startable.

### note · external:aide · 2026-10-25T15:04:26.086Z
From the human, via aide, 2026-10-25 11:04 AM ET (verbatim): "I don't want ~ in the time log ever; it's just messy and IMO unnecessary; times may be approximate, that is understood."

Background found by aide: ~ in the Time Log came from the guide line added in ffbb8bf (mn-caa0, under bmen, 10-03); agents followed it, append rejected '~21:55', and mn-3p28 (v2.26.7, 10-06) made the code accept and write ~HH:MM instead of fixing the guide. Today ~ parses fine (time_tracking._parse_entry_time and time_log._strip_tilde strip it).

So for this ticket: no ~ written to the Time Log by anything. Reverse mn-3p28's write side: time-log append --start/--end/--prev-start/--close-prev and time-log update --text reject a leading ~ with a clear error (and --close-prev never writes ~). Drop the tilde from the guide (conventions.md:207), doc/meta-notes.txt, --help, and spec design/specs/time-log-edit.md (r-6bf7, s-295d, s-e683); update the tests mn-3p28 added. Open point, not yet decided by the human: whether the time report should still read ~ in old notes; aide asked the human. Until answered, leave the read side (time_tracking._parse_entry_time) as it is.
