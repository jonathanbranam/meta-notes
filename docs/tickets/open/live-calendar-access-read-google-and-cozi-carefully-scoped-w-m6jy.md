---
id: m6jy
title: "Live calendar access: read Google and Cozi, carefully scoped write (Google first)"
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: []
---

## The ask

# Live calendar access

## The ask

The human, 2026-10-03 (relayed by the notes advisor, m-0044): "Definitely
need read and again, possible carefully scope write to two calendars: My
gmail and our family Cozi calendar but not sure if they have an API."

Today `meta-notes calendar` reads only a Google Calendar export (a `.zip`
of `.ics` saved into `.meta-notes-cache/ics/`). The NUC's notes root has
no export, so calendar questions there fail.

## What's known

- **Google Calendar** has a real API: read, and write scoped to chosen
  calendars (OAuth; `calendar.readonly`, `calendar.events`).
- **Cozi** has no public API as far as the advisor knows. It publishes a
  private ICS feed URL per calendar, so read via ICS is likely; write
  likely isn't. The feed URL is a secret: keep it out of the repo and
  the notes (the old Zettel vault had one, flagged to rotate).

## Open, the human's to decide

- Read first (Google API or a Google secret ICS URL; the Cozi ICS feed),
  replacing or alongside the export?
- Write: which calendar, which operations (create only? edit/delete?),
  and with what confirmation. Google first; Cozi likely can't.
- Where credentials live (OAuth token, feed URLs) on each machine.

Related: the human is sending a Cozi-replacement app idea to the dalek
orchestrator.
