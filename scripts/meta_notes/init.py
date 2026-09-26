"""
Initialize a notes root: PPARA folders, templates, sentinel, skills, the
cache folder, .gitignore entries, and the virtualenv.

Replaces meta_notes#notes#Init in autoload/meta_notes/notes.vim. Templates
ship in the plugin's templates/ and are copied byte for byte. Skills ship in
the plugin's skills/ and are linked into <root>/.claude/skills/, so updating
the plugin updates them. The virtualenv, <root>/.venv, holds the libraries
in the plugin's requirements.txt; bin/meta-notes runs the CLI with it. Re-running
only creates what is missing.
"""

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from meta_notes.root import SENTINEL, find_root

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = PLUGIN_ROOT / "bin" / "meta-notes"
TEMPLATES_DIR = PLUGIN_ROOT / "templates"
SKILLS_DIR = PLUGIN_ROOT / "skills"
REQUIREMENTS = PLUGIN_ROOT / "requirements.txt"

FOLDERS = (
    "project",
    "area",
    "resource",
    "resource/template",
    "plan",
    "plan/daily",
    "plan/week",
    "plan/quarter",
    "plan/year",
    "archive",
    "archive/project",
    "archive/area",
    "archive/resource",
    ".meta-notes-cache",
    ".meta-notes-cache/ics",
    ".meta-notes-cache/calendar",
)

TEMPLATES = ("daily.md", "weekly.md", "quarterly.md", "yearly.md")
TEMPLATE_FOLDER = "resource/template"
SKILLS_FOLDER = ".claude/skills"
CACHE_README = ".meta-notes-cache/README.md"
CACHE_README_SOURCE = "cache-README.md"
VENV = ".venv"
VENV_PYTHON = ".venv/bin/python3"
MIN_PYTHON = (3, 11)
GITIGNORE = ".gitignore"
IGNORED = (".venv", ".meta-notes-cache")

SENTINEL_CONTENT = (
    "# meta-notes notes root. Created by `meta-notes init`; keep and commit it.\n")


class InitError(Exception):
    """Init failed; the message is shown to the user."""


@dataclass
class Item:
    """One thing init created or checked."""
    kind: str    # folder, template, sentinel, skill, cache-readme, venv,
                 # gitignore
    path: str    # relative to the notes root; for gitignore, the entry
    status: str  # created, exists, overwritten, repointed, skipped,
                 # replaced, rebuilt


@dataclass
class InitResult:
    root: str
    items: list[Item] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _nearest_existing(path: str) -> str:
    while not os.path.isdir(path):
        path = os.path.dirname(path)
    return path


def check_not_nested(target: str, home: str | None) -> None:
    """
    Fail if target would be a notes root inside another one.

    The search starts at the nearest existing ancestor of target's parent;
    a missing directory would fail the permission check and end it early.
    """
    parent = os.path.dirname(os.path.abspath(target))
    root = find_root(_nearest_existing(parent), home)
    if root is not None:
        raise InitError(f"Cannot initialize inside existing notes root: {root}")


def shipped_skills() -> list[str]:
    """Names of skill directories (containing SKILL.md) the plugin ships."""
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(p.name for p in SKILLS_DIR.iterdir()
                  if (p / "SKILL.md").is_file())


def _install_skill(name: str, force: bool, result: InitResult) -> None:
    path = os.path.join(SKILLS_FOLDER, name)
    expected = str(SKILLS_DIR / name)

    if os.path.islink(path):
        if os.path.realpath(path) == os.path.realpath(expected):
            result.items.append(Item("skill", path, "exists"))
            return
        os.remove(path)
        os.symlink(expected, path)
        result.items.append(Item("skill", path, "repointed"))
    elif os.path.lexists(path):
        if not force:
            result.items.append(Item("skill", path, "skipped"))
            result.warnings.append(
                f"{path} exists and is not a link; left alone "
                "(use --force to replace)")
            return
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        os.symlink(expected, path)
        result.items.append(Item("skill", path, "replaced"))
    else:
        os.symlink(expected, path)
        result.items.append(Item("skill", path, "created"))


def _copy_shipped(kind: str, source: str, path: str, force: bool,
                  result: InitResult) -> None:
    """Copy a file shipped in templates/ unless it exists (or force)."""
    existed = os.path.exists(path)
    if existed and not force:
        result.items.append(Item(kind, path, "exists"))
        return
    shutil.copyfile(TEMPLATES_DIR / source, path)
    result.items.append(Item(kind, path, "overwritten" if existed else "created"))


def _ignores(line: str, name: str) -> bool:
    """Whether a .gitignore line ignores the top-level directory name."""
    return line.strip() in (name, f"{name}/", f"/{name}", f"/{name}/")


def _update_gitignore(result: InitResult) -> None:
    """Append .venv/ and .meta-notes-cache/ to .gitignore when missing."""
    if not os.path.isfile(GITIGNORE):
        for name in IGNORED:
            result.items.append(Item("gitignore", f"{name}/", "skipped"))
        result.warnings.append(
            "No .gitignore in the notes root; add "
            + " and ".join(f"{name}/" for name in IGNORED)
            + " to your git ignores so the virtualenv and calendar exports "
            "aren't committed")
        return

    text = Path(GITIGNORE).read_text()
    lines = text.splitlines()
    added = []
    for name in IGNORED:
        if any(_ignores(line, name) for line in lines):
            result.items.append(Item("gitignore", f"{name}/", "exists"))
        else:
            added.append(f"{name}/")
            result.items.append(Item("gitignore", f"{name}/", "created"))
    if added:
        prefix = "" if text == "" or text.endswith("\n") else "\n"
        with open(GITIGNORE, "a") as f:
            f.write(prefix + "".join(f"{line}\n" for line in added))


def run_command(argv: list[str]) -> subprocess.CompletedProcess:
    """Run a command, capturing stdout and stderr together as text."""
    return subprocess.run(argv, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True)


def _command_text(argv: list[str]) -> str:
    return " ".join(argv)


def _output_tail(output: str | None, lines: int = 10) -> str:
    """The last lines of a command's output, for a warning."""
    kept = (output or "").strip().splitlines()[-lines:]
    return "\n".join(kept) if kept else "(no output)"


def _unavailable(reason: str) -> str:
    return f"Calendar support is not available: {reason}"


def _setup_venv(python: str | None, force: bool, result: InitResult) -> None:
    """
    Build .venv with python and install requirements.txt into it.

    An existing .venv is left alone unless force. Failures are warnings, not
    errors: every command but calendar works without the virtualenv.
    """
    existed = os.path.lexists(VENV)
    if existed and not force:
        result.items.append(Item("venv", VENV, "exists"))
        return

    python = python or "python3"
    check = [python, "-c",
             "import sys; print('%d.%d' % sys.version_info[:2])"]
    try:
        proc = run_command(check)
    except OSError as e:
        result.items.append(Item("venv", VENV, "skipped"))
        result.warnings.append(_unavailable(
            f"cannot run {python}: {e.strerror or e}. Install Python "
            f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer, or pass --python PATH"))
        return
    found = proc.stdout.strip() if proc.returncode == 0 else ""
    try:
        version = tuple(int(part) for part in found.split("."))
    except ValueError:
        version = ()
    if len(version) != 2:
        result.items.append(Item("venv", VENV, "skipped"))
        result.warnings.append(_unavailable(
            f"`{_command_text(check)}` failed:\n{_output_tail(proc.stdout)}"))
        return
    if version < MIN_PYTHON:
        result.items.append(Item("venv", VENV, "skipped"))
        result.warnings.append(_unavailable(
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer is required, and "
            f"{python} is Python {found}. Pass --python PATH to use another "
            "interpreter"))
        return

    if existed:
        if os.path.isdir(VENV) and not os.path.islink(VENV):
            shutil.rmtree(VENV)
        else:
            os.remove(VENV)

    create = [python, "-m", "venv", "--prompt", "meta-notes", VENV]
    proc = run_command(create)
    if proc.returncode != 0:
        # Don't leave a partial .venv that a re-run would leave alone
        shutil.rmtree(VENV, ignore_errors=True)
        result.items.append(Item("venv", VENV, "skipped"))
        result.warnings.append(_unavailable(
            f"`{_command_text(create)}` failed:\n{_output_tail(proc.stdout)}"))
        return

    install = [VENV_PYTHON, "-m", "pip", "install", "-r", str(REQUIREMENTS)]
    try:
        proc = run_command(install)
        failed = proc.returncode != 0
        output = proc.stdout
    except OSError as e:
        failed = True
        output = str(e.strerror or e)
    if failed:
        # Kept: the shim can still run every other command with it
        result.items.append(Item("venv", VENV, "skipped"))
        result.warnings.append(_unavailable(
            f"`{_command_text(install)}` failed:\n{_output_tail(output)}\n"
            "Run `meta-notes init --force` once the problem is fixed"))
        return

    result.items.append(Item("venv", VENV, "rebuilt" if existed else "created"))


def cli_on_path() -> bool:
    """Whether a `meta-notes` command is on PATH, where skills call it."""
    return shutil.which("meta-notes") is not None


def init(target: str, force: bool = False, home: str | None = None,
         python: str | None = None) -> InitResult:
    """
    Initialize target as a notes root.

    Args:
        target: Directory to initialize; created, with parents, if missing.
        force: Overwrite templates and the cache README, replace non-link
            skill targets, and rebuild the virtualenv.
        home: $HOME, bounding the nesting check's upward search.
        python: Interpreter to build the virtualenv with (default: python3
            on PATH).

    Returns:
        What was created or found, with paths relative to target.

    Raises:
        InitError: If target is inside another notes root, or a file
            operation fails.
    """
    target = os.path.abspath(os.path.expanduser(target))
    check_not_nested(target, home)

    try:
        os.makedirs(target, exist_ok=True)
        os.chdir(target)
        result = InitResult(root=target)

        for folder in FOLDERS:
            status = "exists" if os.path.isdir(folder) else "created"
            os.makedirs(folder, exist_ok=True)
            result.items.append(Item("folder", folder, status))

        for name in TEMPLATES:
            _copy_shipped("template", name, os.path.join(TEMPLATE_FOLDER, name),
                          force, result)

        if os.path.isfile(SENTINEL):
            result.items.append(Item("sentinel", SENTINEL, "exists"))
        elif os.path.lexists(SENTINEL):
            raise InitError(f"{SENTINEL} exists and is not a file")
        else:
            Path(SENTINEL).write_text(SENTINEL_CONTENT)
            result.items.append(Item("sentinel", SENTINEL, "created"))

        skills = shipped_skills()
        if skills:
            os.makedirs(SKILLS_FOLDER, exist_ok=True)
        for name in skills:
            _install_skill(name, force, result)

        _copy_shipped("cache-readme", CACHE_README_SOURCE, CACHE_README, force,
                      result)
        _update_gitignore(result)
        _setup_venv(python, force, result)
    except OSError as e:
        where = f": {e.filename}" if e.filename else ""
        raise InitError(f"{e.strerror or e}{where}")

    if not cli_on_path():
        result.warnings.append(
            "meta-notes is not on PATH, and the skills call it; link it into "
            f"a directory on PATH, for example: ln -s {CLI_PATH} "
            "~/bin/meta-notes")

    return result
