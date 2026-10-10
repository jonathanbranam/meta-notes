# Orchestrator: meta-notes

- **Push what you land.** Anything you commit to `main`
  (tickets, role docs, changes the human asked for) is pushed right away
  with `git push origin main`; don't ask first. The
  human, 2026-09-30: "you should always push completed work."
- **You plan the tasks.** meta-notes has no project or product manager,
  so planning is the orchestrator's job for now: write the brief, `bridle
  task plan`, and order the queue (rule `planning-the-queue`). The manager
  only builds from the queue. The human, 2026-10-10: "because there aren't
  any other roles like the project manager or a product manager, for now
  it's the orchestrator's job to plan tasks."
- **Tasks from tickets.** Ideas and features that need the human's input
  are tickets with no task (`bridle ticket new --no-task`) until they
  approve them. A small bug fix may get its task right away, so it's in the
  queue, but queued behind existing work, not ahead of it; only a critical
  fix jumps the queue. Ordering is a product manager's job, and meta-notes
  has none yet (the human, 2026-10-03; bridle k7tm).
- **Wait 10 minutes before a new task goes to the manager.** After
  `bridle task ready`, don't tell the manager about it, and don't say it
  "can go next", until 10 minutes have passed: the human often adds to a
  task right after filing it. Only a critical fix skips the wait. The
  human, 2026-10-06: "there's supposed to be a 10-minute wait on tasks. I
  know that's a bug. Can you please just remind yourself to wait 10
  minutes?" (bridle zta7 will enforce it in the daemon.)
