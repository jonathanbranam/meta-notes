"""
Project list: every project in project/ with its status, dates, and warnings.

Fields come from the home note (see project.py). A project's tasks are the
tasks in its note or folder plus tasks anywhere carrying its tag, found in
one pass over the notes root. Dates come only from what is written in the
notes: no git history and no file modification times. Nothing is written.
"""

import os
import re
from dataclasses import dataclass, field
from datetime import date, timedelta

import find_tasks
from notes import find_all_markdown_files
from tags import canonical_tag
from tasks import Task, TaskStatus
from meta_notes import project

PROJECT_FOLDER = "project"

# Days without activity or review before a warning
THRESHOLD_DAYS = 30

WARNINGS = ("no-home-note", "no-next", "no-recent-activity", "review-overdue")

_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_HEADING = re.compile(r"^#{1,6}(\s|$)")


@dataclass
class Project:
    """One project and what the list reports about it."""
    path: str                   # project/foo.md or project/foo/
    home: str | None
    status: str = "active"
    tag: str | None = None
    fields: dict[str, str] = field(default_factory=dict)
    tasks: list[Task] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    last_review: date | None = None
    latest_date: date | None = None
    warnings: list[str] = field(default_factory=list)


def has_tag(task: Task, tag: str) -> bool:
    return any(t.lower() == tag.lower() for t in task.tags)


def list_projects(root_dir: str = ".") -> list[Project]:
    """
    The projects directly in project/, sorted by path, with their fields.

    Args:
        root_dir: Notes root.

    Returns:
        A Project per note and folder, with home, status, tag, and files set.
    """
    folder = os.path.join(root_dir, PROJECT_FOLDER)
    try:
        names = sorted(os.listdir(folder))
    except FileNotFoundError:
        return []

    projects = []
    for name in names:
        if name.startswith("."):
            continue
        p = load_project(f"{PROJECT_FOLDER}/{name}", root_dir)
        if p is not None:
            projects.append(p)
    return projects


def load_project(rel: str, root_dir: str = ".") -> Project | None:
    """
    One project, with its home note, fields, and files.

    Args:
        rel: A note or folder in project/ or archive/project/, relative to
            the notes root (a folder with or without a trailing /).

    Returns:
        The Project, or None if rel is neither a folder nor a markdown note.
    """
    rel = rel.rstrip("/")
    full = os.path.join(root_dir, rel)
    if os.path.isdir(full):
        files = sorted(os.path.relpath(f, root_dir) for f in _walk_files(full))
        home = os.path.join(full, project.HOME_NOTE)
        p = Project(rel + "/", f"{rel}/{project.HOME_NOTE}"
                    if os.path.isfile(home) else None, files=files)
    elif rel.endswith(".md") and os.path.isfile(full):
        p = Project(rel, rel, files=[rel])
    else:
        return None

    if p.home is None:
        p.warnings.append("no-home-note")
    else:
        p.fields = project.read_fields(os.path.join(root_dir, p.home))
        p.status = p.fields.get("status") or "active"
        p.tag = canonical_tag(p.fields["tag"]) if p.fields.get("tag") else None
    return p


def _walk_files(folder: str) -> list[str]:
    found = []
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        found.extend(os.path.join(dirpath, f) for f in filenames
                     if not f.startswith("."))
    return found


def _owns(p: Project, rel: str) -> bool:
    """Whether a root-relative file is in a project's note or folder."""
    return rel.startswith(p.path) if p.path.endswith("/") else rel == p.path


def assign_tasks(projects: list[Project], tasks: list[Task],
                 root_dir: str = ".") -> None:
    """
    Give each project its tasks: those in its note or folder, and those
    anywhere with its tag, each once.
    """
    for task in tasks:
        rel = os.path.relpath(task.filename, root_dir)
        for p in projects:
            if _owns(p, rel) or (p.tag and has_tag(task, p.tag)):
                p.tasks.append(task)


def last_review(tasks: list[Task]) -> date | None:
    """The latest completion date among completed #review tasks."""
    days = [t.effective_due for t in tasks
            if t.status == TaskStatus.COMPLETED and has_tag(t, "review")
            and t.effective_due]
    return max(days, default=None)


def _dates(text: str, today: date) -> list[date]:
    found = []
    for match in _DATE.findall(text):
        try:
            day = date.fromisoformat(match)
        except ValueError:
            continue
        if day <= today:
            found.append(day)
    return found


def _heading_lines(path: str) -> list[str]:
    try:
        with open(path, encoding="utf-8") as f:
            return [line for line in f if _HEADING.match(line)]
    except (OSError, UnicodeDecodeError):
        return []


def latest_date(p: Project, today: date, root_dir: str = ".") -> date | None:
    """
    The latest valid date, on or before today, in the project's file paths,
    its markdown heading lines, and its tasks other than #review tasks.
    """
    days: list[date] = []
    parent = os.path.dirname(p.path.rstrip("/")) + "/"
    for rel in p.files:
        # Only the part inside the project's folder counts, not the folder
        # it's in (project/ or archive/project/)
        days += _dates(rel.removeprefix(parent), today)
        if rel.endswith(".md"):
            for line in _heading_lines(os.path.join(root_dir, rel)):
                days += _dates(line, today)
    for task in p.tasks:
        if not has_tag(task, "review"):
            days += _dates(task.text, today)
    return max(days, default=None)


def _older_than(day: date | None, today: date) -> bool:
    return day is None or today - day > timedelta(days=THRESHOLD_DAYS)


def warnings(p: Project, today: date) -> list[str]:
    """The warnings that apply to a project, in WARNINGS order."""
    found = set(p.warnings)
    active = p.status.lower() == "active"
    if active and not any(t.status == TaskStatus.INCOMPLETE and has_tag(t, "next")
                          for t in p.tasks):
        found.add("no-next")
    if active and _older_than(p.latest_date, today):
        found.add("no-recent-activity")
    if p.status.lower() != "done" and _older_than(p.last_review, today):
        found.add("review-overdue")
    return [w for w in WARNINGS if w in found]


def collect(root_dir: str = ".", today: date | None = None) -> list[Project]:
    """List projects and fill in their tasks, dates, and warnings."""
    today = today or date.today()
    projects = list_projects(root_dir)
    files = find_all_markdown_files(root_dir)
    assign_tasks(projects, find_tasks.collect_tasks(files, root_dir, status="all"),
                 root_dir)
    for p in projects:
        p.last_review = last_review(p.tasks)
        p.latest_date = latest_date(p, today, root_dir)
        p.warnings = warnings(p, today)
    return projects


def _iso(day: date | None) -> str | None:
    return day.isoformat() if day else None


def to_dict(p: Project) -> dict:
    return {
        "path": p.path,
        "home": p.home,
        "status": p.status,
        "tag": p.tag,
        "last_review": _iso(p.last_review),
        "latest_date": _iso(p.latest_date),
        "open_tasks": sum(t.status == TaskStatus.INCOMPLETE for t in p.tasks),
        "completed_tasks": sum(t.status == TaskStatus.COMPLETED for t in p.tasks),
        "warnings": p.warnings,
    }


def format_projects(entries: list[dict]) -> list[str]:
    """One text line per project: path, status, dates, and warnings."""
    if not entries:
        return ["No projects."]
    width = max(len(e["path"]) for e in entries)
    status_width = max(len(e["status"]) for e in entries)
    lines = []
    for e in entries:
        line = (f"{e['path']:<{width}}  {e['status']:<{status_width}}  "
                f"latest {e['latest_date'] or 'none':<10}  "
                f"review {e['last_review'] or 'never':<10}")
        if e["warnings"]:
            line += "  " + ", ".join(e["warnings"])
        lines.append(line.rstrip())
    return lines


def run(root_dir: str = ".", warnings_only: bool = False,
        today: date | None = None) -> tuple[list[str], list[dict]]:
    """
    The project list.

    Args:
        root_dir: Notes root.
        warnings_only: Only projects with at least one warning.
        today: Reference date (default: today).

    Returns:
        (text lines, project dicts).
    """
    entries = [to_dict(p) for p in collect(root_dir, today)]
    if warnings_only:
        entries = [e for e in entries if e["warnings"]]
    return format_projects(entries), entries
