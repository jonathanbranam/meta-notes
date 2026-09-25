"""
Initialize a notes root: PPARA folders, templates, sentinel, and skills.

Replaces meta_notes#notes#Init in autoload/meta_notes/notes.vim. Templates
ship in the plugin's templates/ and are copied byte for byte. Skills ship in
the plugin's skills/ and are linked into <root>/.claude/skills/, so updating
the plugin updates them. Re-running only creates what is missing.
"""

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from meta_notes.root import SENTINEL, find_root

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = PLUGIN_ROOT / "bin" / "meta-notes"
TEMPLATES_DIR = PLUGIN_ROOT / "templates"
SKILLS_DIR = PLUGIN_ROOT / "skills"

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
)

TEMPLATES = ("daily.md", "weekly.md", "quarterly.md", "yearly.md")
TEMPLATE_FOLDER = "resource/template"
SKILLS_FOLDER = ".claude/skills"

SENTINEL_CONTENT = (
    "# meta-notes notes root. Created by `meta-notes init`; keep and commit it.\n")


class InitError(Exception):
    """Init failed; the message is shown to the user."""


@dataclass
class Item:
    """One thing init created or checked."""
    kind: str    # folder, template, sentinel, skill
    path: str    # relative to the notes root
    status: str  # created, exists, overwritten, repointed, skipped, replaced


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


def cli_on_path() -> bool:
    """Whether a `meta-notes` command is on PATH, where skills call it."""
    return shutil.which("meta-notes") is not None


def init(target: str, force: bool = False, home: str | None = None) -> InitResult:
    """
    Initialize target as a notes root.

    Args:
        target: Directory to initialize; created, with parents, if missing.
        force: Overwrite templates and replace non-link skill targets.
        home: $HOME, bounding the nesting check's upward search.

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
            path = os.path.join(TEMPLATE_FOLDER, name)
            existed = os.path.exists(path)
            if existed and not force:
                result.items.append(Item("template", path, "exists"))
                continue
            shutil.copyfile(TEMPLATES_DIR / name, path)
            result.items.append(
                Item("template", path, "overwritten" if existed else "created"))

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
    except OSError as e:
        where = f": {e.filename}" if e.filename else ""
        raise InitError(f"{e.strerror or e}{where}")

    if not cli_on_path():
        result.warnings.append(
            "meta-notes is not on PATH, and the skills call it; link it into "
            f"a directory on PATH, for example: ln -s {CLI_PATH} "
            "~/bin/meta-notes")

    return result
