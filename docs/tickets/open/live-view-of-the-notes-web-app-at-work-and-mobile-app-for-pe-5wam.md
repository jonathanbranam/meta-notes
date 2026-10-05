---
id: 5wam
title: "Live view of the notes: web app at work and mobile app for personal"
kind: explore
opened: 2026-10-05
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [5zm3, m6jy]
tasks: []
---

## The ask

The human, 2026-10-04, traveling, by voice (relayed by the notes advisor;
"nodes" = notes, "weights" probably "views"). To consider, not to schedule:

> Right now, I can't see the nodes repository very easily. I'm traveling,
> obviously, and there's not a really easy way to see this. [...] begin
> consideration of how we post this in a web app so that I can get a live
> view of what's going on. In the meantime, I open everything in the GitHub
> app, and it doesn't refresh very easily. [...] We need to build a proper
> UI for this, but there's a need for two things for this app:
> - A mobile app that has the weights and the actions for my personal
> - A combined need for a web app that I can run at work, that can give me
>   nudges, run a web page over localhost, and probably be a similar type of
>   thing that runs over the web and that I can access from my phone or
>   computer, giving just a richer interface to everything. The mobile app
>   will probably share a lot of the same capabilities. We'll probably build
>   both as web-based React apps, but that one will also have a bridge so it
>   can interact with the mobile device and send me pushes, alerts, and
>   alarms.

## Context

- The notes project's `project/life-app` (unified life app: vim + React PWA
  over the git repo) is the human's own plan for this.
- track-web, the human's hosted React PWA platform at branam.us, is a
  likely host for the mobile side.
- Nudges are 5zm3; live calendar is m6jy.
- meta-notes' CLI (`--json` on every command) is the natural backend: the
  apps read and edit notes through it, as agents and Vim do, so the race
  safety (`--expect`) carries over.
- Rule works-without-bridle: the work web app runs on the work machine,
  with no bridle.

## Open questions for the human

- Read-only live view first (today's plan, tasks, Time Block), or editing
  from the start?
- Where it runs: localhost at work only, the NUC for personal reached from
  the phone (Tailscale?), or hosted on track-web.
- One app with work and personal modes (like the notes root's `mode`), or
  two.
