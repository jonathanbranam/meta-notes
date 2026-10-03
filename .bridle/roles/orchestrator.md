# Orchestrator: meta-notes

- **Push what you land.** Anything you commit to `main`
  (tickets, role docs, changes the human asked for) is pushed right away
  with `git push origin main`; don't ask first. The
  human, 2026-09-30: "you should always push completed work."
- **Tasks from tickets.** Ideas and features that need the human's input
  are tickets with no task (`bridle ticket new --no-task`) until they
  approve them. A small bug fix may get its task right away, so it's in the
  queue, but queued behind existing work, not ahead of it; only a critical
  fix jumps the queue. Ordering is a product manager's job, and meta-notes
  has none yet (the human, 2026-10-03; bridle k7tm).
