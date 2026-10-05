---
id: g8wz
title: "meta-notes ui: start, stop, status and open the meta-notes-ui server"
kind: feature
opened: 2026-10-05
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [5wam]
tasks: [mn-g8wz]
---

## The ask

The human, 2026-10-04: "I want meta-notes CLI to manage the server and
interact with it and vice-versa." The UI is its own repo, meta-notes-ui
(github.com/jonathanbranam/meta-notes-ui), installed by git clone + `npm ci
&& npm run build`. Its start contract is in that repo's ticket 83ya:

  node <clone>/dist/server/index.js --root <root> [--port N] [--host H]
    --token-file <path>
  writes <root>/.meta-notes-cache/ui/server.json (pid, host, port, url,
  version) on listen, removes it on exit.

Here:

- `[ui] path = "~/src/meta-notes-ui"` in `.meta-notes` (the clone);
  `[ui] host` and `port` optional defaults. `--path`, `--host`, `--port`
  override.
- `meta-notes ui start`: makes a token in `.meta-notes-cache/ui/token`
  (0600) if missing, starts the server detached with its log in
  `.meta-notes-cache/ui/server.log`, waits for server.json, prints the
  URL with `?token=` (and `--json`). Refuses if one is running for this
  root. Clear errors: no `[ui] path`, no `dist/` (run `npm run build`),
  no `node`.
- `ui stop` (SIGTERM the pid in server.json, wait, clean up a stale
  file), `ui status` (running or not, url, version, pid), `ui open`
  (start if needed, open the URL with `open`/`xdg-open`), `ui url`
  (print the URL with token, for the phone: `--host` binding needed).
- `meta-notes init` mentions `ui` only in its help, nothing installed.
- Works without bridle (rule works-without-bridle). Tests with a stub
  server script that honours the contract. Spec, pytest, docs, README.
  Minor version.
