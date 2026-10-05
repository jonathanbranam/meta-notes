"""
Manage the meta-notes-ui server (its own repo) for a notes root.

The server's start contract: it is run as
`node <clone>/dist/server/index.js --root R [--port N] [--host H]
--token-file F`, writes <root>/.meta-notes-cache/ui/server.json (pid, host,
port, url, version) once it listens, and removes it on exit.
"""

import json
import os
import secrets
import shutil
import signal
import subprocess
import sys
import time

from meta_notes import config

UI_DIR = os.path.join(".meta-notes-cache", "ui")
ENTRY = os.path.join("dist", "server", "index.js")
START_TIMEOUT = 10.0
STOP_TIMEOUT = 10.0


def _dir(root: str) -> str:
    return os.path.join(root, UI_DIR)


def _info_path(root: str) -> str:
    return os.path.join(_dir(root), "server.json")


def _token_path(root: str) -> str:
    return os.path.join(_dir(root), "token")


def _alive(pid: int) -> bool:
    try:
        # Reap the server if it's our own child, so it isn't a zombie
        os.waitpid(pid, os.WNOHANG)
    except ChildProcessError:
        pass
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def status(root: str) -> dict | None:
    """The running server's server.json, or None (a stale file is removed)."""
    try:
        with open(_info_path(root), encoding="utf-8") as f:
            info = json.load(f)
        pid = int(info["pid"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if _alive(pid):
        return info
    _remove_info(root)
    return None


def _remove_info(root: str) -> None:
    try:
        os.remove(_info_path(root))
    except OSError:
        pass


def token(root: str) -> str:
    """The root's UI token, made (0600) when missing."""
    path = _token_path(root)
    try:
        with open(path, encoding="utf-8") as f:
            value = f.read().strip()
        if value:
            return value
    except OSError:
        pass
    os.makedirs(_dir(root), exist_ok=True)
    value = secrets.token_urlsafe(24)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(value + "\n")
    os.chmod(path, 0o600)
    return value


def url(root: str, info: dict) -> str:
    """The server's URL with the token."""
    return f"{info['url']}?token={token(root)}"


def _settings(root: str, path, host, port) -> tuple[str, str | None, int | None]:
    ui = config.table(config.load(root), "ui")
    path = path or ui.get("path")
    if not path:
        raise ValueError("No UI path: set `path` in the [ui] table of "
                         ".meta-notes or pass --path")
    host = host or ui.get("host")
    port = port if port is not None else ui.get("port")
    if port is not None and (isinstance(port, bool) or not isinstance(port, int)):
        raise ValueError("[ui] port must be an integer")
    return os.path.abspath(os.path.expanduser(str(path))), host, port


def start(root: str, path=None, host=None, port=None) -> dict:
    """
    Start the server detached and wait for it to listen.

    Returns:
        The new server.json.

    Raises:
        ValueError: If one is already running, or the setup is missing
            (no [ui] path, no dist/, no node), or the server fails to start.
    """
    running = status(root)
    if running:
        raise ValueError(f"The UI is already running at {running['url']} "
                         f"(pid {running['pid']})")
    clone, host, port = _settings(root, path, host, port)
    entry = os.path.join(clone, ENTRY)
    if not os.path.isfile(entry):
        raise ValueError(f"No {ENTRY} in {clone}: run `npm ci && npm run "
                         "build` there")
    node = shutil.which("node")
    if not node:
        raise ValueError("node not found on PATH; the UI needs Node.js")

    token(root)
    cmd = [node, entry, "--root", root, "--token-file", _token_path(root)]
    if host:
        cmd += ["--host", str(host)]
    if port is not None:
        cmd += ["--port", str(port)]
    log_path = os.path.join(_dir(root), "server.log")
    with open(log_path, "ab") as log:
        proc = subprocess.Popen(cmd, cwd=root, stdin=subprocess.DEVNULL,
                                stdout=log, stderr=log,
                                start_new_session=True)
    deadline = time.monotonic() + START_TIMEOUT
    while time.monotonic() < deadline:
        info = status(root)
        if info and info["pid"] == proc.pid:
            return info
        if proc.poll() is not None:
            raise ValueError(f"The UI server exited with code "
                             f"{proc.returncode}; see {log_path}")
        time.sleep(0.05)
    raise ValueError(f"The UI server did not start within "
                     f"{START_TIMEOUT:.0f}s; see {log_path}")


def stop(root: str) -> bool:
    """SIGTERM the server and wait; False when none was running."""
    info = status(root)
    if not info:
        return False
    pid = int(info["pid"])
    os.kill(pid, signal.SIGTERM)
    deadline = time.monotonic() + STOP_TIMEOUT
    while time.monotonic() < deadline:
        if not _alive(pid):
            _remove_info(root)
            return True
        time.sleep(0.05)
    raise ValueError(f"The UI server (pid {pid}) did not stop within "
                     f"{STOP_TIMEOUT:.0f}s")


def open_url(link: str) -> None:
    """Open the URL in the default browser."""
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    if not shutil.which(opener):
        raise ValueError(f"{opener} not found; open {link} yourself")
    subprocess.Popen([opener, link], stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
