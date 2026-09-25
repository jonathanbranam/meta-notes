"""
Project brief: one project's fields, files, tasks, and dates.

The project, its tasks, latest date, last review, and warnings are computed
by the same code as the project list (projects.py), so the two agree. File
modification dates are reported but never used for any date. Nothing is
written.
"""

import os
from datetime import date, timedelta

import find_tasks
from notes import find_all_markdown_files
from tasks import Task, TaskStatus
from meta_notes import project, projects, query

# Days of completed tasks listed by default
COMPLETED_DAYS = 90


def resolve(root_dir: str, path: str) -> str:
    """
    The project a path names, relative to the notes root.

    Args:
        root_dir: Notes root.
        path: Root-relative or absolute path inside the root; `.md` and a
            trailing `/` are optional.

    Returns:
        `project/foo.md` or `project/foo` (or the same in archive/project/).

    Raises:
        ValueError: If the path isn't a project.
    """
    rel = path
    if os.path.isabs(path):
        rel = os.path.relpath(path, os.path.abspath(root_dir))
    rel = os.path.normpath(rel) if rel else rel
    found = None if rel.startswith("..") else project.project_for(rel, root_dir)
    if found is None:
        raise ValueError(f"{path} is not a project (a note or folder directly "
                         f"in {' or '.join(d + '/' for d in project.PROJECT_FOLDERS)})")
    return found


def _sort_key(task: Task, root_dir: str) -> tuple[str, int]:
    return os.path.relpath(task.filename, root_dir), task.line_no


def _iso(day: date | None) -> str | None:
    return day.isoformat() if day else None


def _task_dict(task: Task, root_dir: str) -> dict:
    d = query.task_to_dict(task, root_dir, "")
    del d["section"]
    return d


def _file_dict(rel: str, root_dir: str) -> dict:
    st = os.stat(os.path.join(root_dir, rel))
    return {"path": rel, "size": st.st_size,
            "modified": date.fromtimestamp(st.st_mtime).isoformat()}


def build(root_dir: str, path: str, since: date | None = None,
          today: date | None = None) -> dict:
    """
    The brief for one project, as a JSON-ready dict.

    Raises:
        ValueError: If the path isn't a project.
    """
    today = today or date.today()
    since = since or today - timedelta(days=COMPLETED_DAYS)
    p = projects.load_project(resolve(root_dir, path), root_dir)
    if p is None:
        raise ValueError(f"{path} is not a project")

    files = find_all_markdown_files(root_dir)
    projects.assign_tasks([p], find_tasks.collect_tasks(files, root_dir, status="all"),
                          root_dir)
    p.tasks.sort(key=lambda t: _sort_key(t, root_dir))
    p.last_review = projects.last_review(p.tasks)
    p.latest_date = projects.latest_date(p, today, root_dir)
    p.warnings = projects.warnings(p, today)

    has = projects.has_tag
    pending = [t for t in p.tasks if t.status == TaskStatus.INCOMPLETE]
    done = [t for t in p.tasks if t.status == TaskStatus.COMPLETED]

    def dicts(selected: list[Task]) -> list[dict]:
        return [_task_dict(t, root_dir) for t in selected]

    return {
        "path": p.path,
        "home": p.home,
        "status": p.status,
        "tag": p.tag,
        "fields": p.fields,
        "latest_date": _iso(p.latest_date),
        "last_review": _iso(p.last_review),
        "has_next": any(has(t, "next") for t in pending),
        "warnings": p.warnings,
        "files": [_file_dict(rel, root_dir) for rel in p.files],
        "open": dicts([t for t in pending if not has(t, "later")]),
        "later": dicts([t for t in pending if has(t, "later")]),
        "deadlines": dicts([t for t in pending if has(t, "deadline")]),
        "scheduled_reviews": dicts([t for t in pending
                                    if has(t, "review") and t.due_date]),
        "completed": dicts([t for t in done
                            if t.effective_due and t.effective_due >= since]),
        "completed_total": len(done),
        "since": since.isoformat(),
    }


def _task_lines(tasks: list[dict]) -> list[str]:
    return [f"  {t['file']}:{t['line']}  {t['text']}" for t in tasks]


def format_brief(b: dict) -> list[str]:
    """The brief as text: header, warnings, then each non-empty section."""
    tag = f"#{b['tag']}" if b["tag"] else "no tag"
    lines = [f"{b['path']}  {b['status']}  {tag}",
             f"latest {b['latest_date'] or 'none'}  "
             f"review {b['last_review'] or 'never'}"]
    if b["warnings"]:
        lines.append("warnings: " + ", ".join(b["warnings"]))

    width = max((len(str(f["size"])) for f in b["files"]), default=0)
    sections = [
        ("Files", [f"  {f['size']:>{width}}  {f['modified']}  {f['path']}"
                   for f in b["files"]]),
        ("Deadlines", _task_lines(b["deadlines"])),
        ("Scheduled reviews", _task_lines(b["scheduled_reviews"])),
        ("Open", _task_lines(b["open"])),
        ("Later", _task_lines(b["later"])),
        (f"Completed ({len(b['completed'])} of {b['completed_total']} "
         f"since {b['since']})", _task_lines(b["completed"])),
    ]
    for heading, body in sections:
        if body:
            lines += ["", heading, *body]
    return lines


def run(root_dir: str, path: str, since: date | None = None,
        today: date | None = None) -> tuple[list[str], dict]:
    """
    The project brief.

    Args:
        root_dir: Notes root.
        path: The project (see resolve).
        since: Start of the completed-task window (default: today minus
            COMPLETED_DAYS).
        today: Reference date (default: today).

    Returns:
        (text lines, brief dict).

    Raises:
        ValueError: If the path isn't a project.
    """
    b = build(root_dir, path, since, today)
    return format_brief(b), b
