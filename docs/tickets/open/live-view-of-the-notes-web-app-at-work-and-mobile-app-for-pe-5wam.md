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

## v1 direction (the human, 2026-10-04)

> For v1 of a meta-notes UI I'd like to have a simple TypeScript Vite React
> app based on track-web and bridle-ui. There are some bridle packs that
> should reflect rules for this kind of app. My feeling is it should be a
> separate repo for organization, but I'd like it to be easily installable
> on my work computer. I can git pull and clone public GitHub projects and
> I can npm install public projects. KISS would be a clone. But I want
> meta-notes CLI to manage the server and interact with it and vice-versa.
> The server should use CLI commands just like agents do to alter and
> update notes. Main thing is that it should serve my entire notes repo as
> rendered markdown and give me nice UI tools on web and mobile to edit
> things. Also it should feature alerts and reminders and some interactive
> capabilities that vim doesn't. It should also update immediately like
> vim so it needs to watch for all file changes. It should feel roughly
> like Obsidian with plugins tailored to me. It should be able to edit note
> text as well, converting lines to markdown for editing (not like Google
> Docs, just editing markdown). It should render tables and frontmatter and
> understand all of my links and conventions.

## Proposed shape (orchestrator, for the human's review)

- **Repo:** `meta-notes-ui`, public on GitHub (code only; no notes in it).
  Installed by `git clone` + `npm ci` + `npm run build`, like the plugin.
  Stack as track-web: Hono on Node for the server, Vite + React + TS
  client, vitest, npm; bridle's `typescript` pack rules (npm, tsc, vitest
  style, check command, dev servers).
- **CLI ↔ server:** `meta-notes ui start|stop|status|open` finds the clone
  (`[ui] path` in `.meta-notes`), starts the server on the root, and keeps
  its pid, port and token in `.meta-notes-cache/ui/`. The server finds the
  root and the CLI from what it was started with, and calls `meta-notes
  ... --json` for every write (task update/add, time-block, time-log, note
  new, move/rename/archive), like agents. Reads go straight to the files.
- **Text editing:** a block or line range opens as raw markdown; saving
  needs a new race-safe CLI write in meta-notes (`note write <file>
  --lines A..B --expect <old> --text <new>`, or whole-file with a hash),
  the same `--expect` model as the other commands. That's the one
  meta-notes change v1 needs besides `ui`.
- **Live:** the server watches the whole root (chokidar or fs.watch,
  ignoring .git/.venv/.meta-notes-cache) and pushes changes over SSE; open
  views re-render, an open editor shows a conflict instead of clobbering.
- **Rendering:** markdown with GFM tables, frontmatter as a property panel,
  `[[wiki links]]` (resolved like the plugin), tags, task emoji (📅 ⏳ 🔁 ✅),
  Time Block and Time Log tables, tildes. A file tree and quick-open.
- **Tailored plugins (after the viewer/editor):** today's plan and Time
  Block, task check-off, alerts and reminders from due times and the Time
  Block (browser notifications), later nudges (5zm3).
- **Access:** binds 127.0.0.1 with a token by default (work machine);
  phone access is opt-in (bind to a LAN/Tailscale address), PWA install.

## Suggested v1 order

1. Repo skeleton, `meta-notes ui start/stop/status`, read-only render of
   any note with a file tree and live updates.
2. Links, frontmatter, tags, task syntax, Time Block/Log rendering.
3. Edits through the CLI: task check-off, raw markdown block edit
   (with meta-notes `note write`).
4. Today view, alerts and reminders, PWA on the phone.
