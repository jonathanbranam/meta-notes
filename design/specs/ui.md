# ui Specification

## Purpose
Specifies `meta-notes ui`, which starts, stops, reports and opens the meta-notes-ui server (its own repo, installed by the user with `git clone` and `npm ci && npm run build`). The CLI only manages the server process; nothing here needs bridle.

## Requirements

### Requirement: Start the UI server  {#r-5187}
`meta-notes ui start [--path DIR] [--host H] [--port N]` SHALL run `node <DIR>/dist/server/index.js --root <root> --token-file <root>/.meta-notes-cache/ui/token`, plus `--host` and `--port` when set, detached, with its output appended to `.meta-notes-cache/ui/server.log`. DIR, host and port SHALL default to `path`, `host` and `port` in the `[ui]` table of `.meta-notes`; the options override them. It SHALL create the token file with mode 0600 when missing and keep an existing one. It SHALL wait for the server to write `.meta-notes-cache/ui/server.json` (`pid`, `host`, `port`, `url`, `version`) and print the `url` with `?token=<token>` appended. With `--json` it SHALL return `running`, `url`, `pid`, `host`, `port` and `version`. It SHALL fail, naming the fix, when no path is configured, `dist/server/index.js` is missing, `node` is not on `PATH`, the server exits early or does not write `server.json` within 10 seconds, or a server is already running for this root.

#### Scenario: Start  {#s-1f38}
*Verification*: **non-executable**
- **WHEN** `[ui] path` names a built clone and the user runs `meta-notes ui start`
- **THEN** a 0600 token file SHALL exist and the command SHALL print the server's URL with `?token=`

#### Scenario: Already running  {#s-dcbb}
*Verification*: **non-executable**
- **WHEN** a server is running for the root and the user runs `meta-notes ui start`
- **THEN** the command SHALL fail and SHALL NOT start a second server

#### Scenario: Not built  {#s-9813}
*Verification*: **non-executable**
- **WHEN** the clone has no `dist/server/index.js`
- **THEN** the command SHALL fail with an error saying to run `npm run build`

### Requirement: Stop and status  {#r-edac}
`meta-notes ui status` SHALL report whether a server is running, from `server.json` and whether its pid is alive; with `--json` it SHALL return `running` and, when running, `url` (without the token), `pid`, `host`, `port` and `version`. A `server.json` whose pid is dead SHALL count as not running and be removed. `meta-notes ui stop` SHALL send SIGTERM to the pid, wait up to 10 seconds for it to exit, and remove a leftover `server.json`; with none running it SHALL succeed and say so, returning `stopped: false` with `--json`.

#### Scenario: Stale server.json  {#s-a1b2}
*Verification*: **non-executable**
- **WHEN** `server.json` names a pid that is not alive and the user runs `meta-notes ui status`
- **THEN** the command SHALL report not running and `server.json` SHALL be removed

#### Scenario: Stop  {#s-6a87}
*Verification*: **non-executable**
- **WHEN** a server is running and the user runs `meta-notes ui stop`
- **THEN** the process SHALL have exited and `server.json` SHALL be gone

### Requirement: URL and open  {#r-cdad}
`meta-notes ui url` SHALL print the running server's URL with `?token=` appended, and fail when none is running. `meta-notes ui open [--path] [--host] [--port]` SHALL start the server when none is running, then open the URL with `open` (macOS) or `xdg-open`, and fail naming the opener when it is missing. With `--json` both return the fields of `start`; `open` adds `started`.

#### Scenario: Open starts when needed  {#s-da5e}
*Verification*: **non-executable**
- **WHEN** no server is running and the user runs `meta-notes ui open`
- **THEN** the server SHALL be started and the URL with the token opened
