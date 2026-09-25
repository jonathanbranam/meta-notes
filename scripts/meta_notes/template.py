"""
Template discovery and rendering.

Ported from autoload/meta_notes/template.vim. Output matches the Vimscript
for the shipped templates, including its quirks: a line containing `{{%` is
replaced entirely by its command's output, and output ending in a newline
leaves a trailing empty line. Differences from the Vimscript: variables are
substituted in one pass, date arithmetic uses calendar days (no DST drift),
names are English whatever the locale, and only a `---` block starting on
the first line is frontmatter.

Paths are relative to the current directory, which the CLI sets to the notes
root. Command blocks run there.
"""

import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE_FOLDER = "resource/template"

# Plan folders and their standard templates
PLAN_TEMPLATES = (
    ("plan/daily/", "daily"),
    ("plan/week/", "weekly"),
    ("plan/quarter/", "quarterly"),
    ("plan/year/", "yearly"),
)

DATE_VARIABLES = ("date", "today", "week_start", "week_end")

VARIABLE_RE = re.compile(r"\{\{([^}]+)\}\}")
ARITHMETIC_RE = re.compile(r"([^+-]+)([+-])(\d+)")
COMMAND_RE = re.compile(r"\{\{%\s*(\w+)\s+(.+)\s*%\}\}")
FRONTMATTER_RE = re.compile(r"---\s*$")

# English names for strftime, so output doesn't depend on LC_TIME
DAY_ABBRS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
DAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
             "Saturday", "Sunday")
MONTH_ABBRS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
               "Oct", "Nov", "Dec")
MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December")


@dataclass
class Rendered:
    """A rendered template: its lines, warnings, and whether vim blocks remain."""
    lines: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    has_vim_blocks: bool = False


def quarter(d: date) -> str:
    """The quarter of a date, 'Q1' to 'Q4'."""
    return f"Q{(d.month - 1) // 3 + 1}"


def week_start(d: date) -> date:
    """The Monday of the date's week."""
    return d - timedelta(days=d.weekday())


def day_abbr(d: date) -> str:
    """English three-letter day abbreviation, 'Mon' to 'Sun'."""
    return DAY_ABBRS[d.weekday()]


def strftime(d: date, fmt: str) -> str:
    """strftime with English day and month names."""
    # Replace the name directives first, leaving `%%` alone; names contain
    # no `%`, so they pass through d.strftime unchanged
    def name(m: re.Match) -> str:
        directive = m.group(1)
        if directive == "a":
            return DAY_ABBRS[d.weekday()]
        if directive == "A":
            return DAY_NAMES[d.weekday()]
        if directive in ("b", "h"):
            return MONTH_ABBRS[d.month - 1]
        if directive == "B":
            return MONTH_NAMES[d.month - 1]
        return m.group(0)
    fmt = re.sub(r"%([%aAbBh])", name, fmt)
    return d.strftime(fmt)


def build_context(note_date: date, filepath: str,
                  today: date | None = None) -> dict:
    """
    Build the template variables for a note.

    Args:
        note_date: The note's template date.
        filepath: The note's path relative to the notes root.
        today: Today's date (default: date.today()).

    Returns:
        Dict of variable name to value: date variables are dates, the rest
        strings.
    """
    today = today or date.today()
    start = week_start(note_date)
    stem, _ = os.path.splitext(filepath)
    filename = os.path.basename(filepath)
    parts = [p for p in filepath.split("/") if p]
    in_project = filepath.startswith("project/") and len(parts) >= 2
    return {
        "date": note_date,
        "today": today,
        "week_start": start,
        "week_end": start + timedelta(days=6),
        "quarter": quarter(note_date),
        "week_quarter": quarter(start),
        "filepath": filepath,
        "note_path": stem,
        "note_name": os.path.splitext(filename)[0],
        "filename": filename,
        "project_name": parts[1] if in_project else "",
    }


def _render_variable(expr: str, context: dict) -> str:
    """Render the expression inside one {{...}}."""
    expr_part, _, fmt = expr.partition(":")

    name = expr_part
    days = 0
    if re.search(r"[+-]", expr_part):
        m = ARITHMETIC_RE.search(expr_part)
        if m:
            name = m.group(1)
            days = int(m.group(3)) if m.group(2) == "+" else -int(m.group(3))

    if name not in context:
        return f'<!-- ERROR: Unknown variable "{name}" -->'

    value = context[name]
    if name not in DATE_VARIABLES:
        return str(value)

    value = value + timedelta(days=days)
    if fmt:
        return strftime(value, fmt)
    return f"{value.isoformat()} {day_abbr(value)}"


def render_line(line: str, context: dict) -> str:
    """
    Substitute the variables in a line.

    Date variables (`date`, `today`, `week_start`, `week_end`) take day
    arithmetic and a strftime format, as in `{{date+1:%Y-%m-%d}}`, and
    default to `YYYY-MM-DD ddd`. Other variables are substituted as-is. An
    unknown variable becomes an error comment.
    """
    return VARIABLE_RE.sub(lambda m: _render_variable(m.group(1), context), line)


def find_template(filepath: str) -> str | None:
    """
    Find the template for a note.

    Args:
        filepath: The note's path relative to the notes root.

    Returns:
        `<dir>/template.md` if it exists; otherwise, for a note in a plan
        folder, its standard template in resource/template/ if it exists;
        otherwise None.
    """
    folder_template = os.path.join(os.path.dirname(filepath), "template.md")
    if os.path.isfile(folder_template):
        return folder_template

    for prefix, kind in PLAN_TEMPLATES:
        if filepath.startswith(prefix):
            standard = f"{TEMPLATE_FOLDER}/{kind}.md"
            return standard if os.path.isfile(standard) else None
    return None


def read_lines(path: str) -> list[str]:
    """Read a file's lines as Vim's readfile() does."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        text = f.read()
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return [line[:-1] if line.endswith("\r") else line for line in lines]


def strip_frontmatter(lines: list[str]) -> list[str]:
    """Drop a `---`-delimited block that starts on the first line."""
    if not lines or not FRONTMATTER_RE.match(lines[0]):
        return lines
    for i in range(1, len(lines)):
        if FRONTMATTER_RE.match(lines[i]):
            return lines[i + 1:]
    return []


def _run(command: str) -> tuple[int, str]:
    """Run a shell command with stderr merged and no stdin."""
    proc = subprocess.run(command, shell=True, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout


def run_command_block(line: str, context: dict) -> tuple[str, str | None, bool]:
    """
    Run the command block in a template line.

    Args:
        line: A template line containing `{{%`.
        context: Template variables, substituted into the command.

    Returns:
        (output, warning, is_vim): the text that replaces the line, a warning
        if the command failed, and whether it is a vim block left for Vim.
    """
    m = COMMAND_RE.search(line)
    if not m:
        return line, None, False

    cmd_type = m.group(1)
    cmd = render_line(m.group(2), context)

    if cmd_type == "vim":
        return f"{{{{% vim {cmd.strip()} %}}}}", None, True
    if cmd_type == "python":
        if re.match(r"\s*scripts/", cmd):
            cmd = re.sub(r"^\s*scripts/",
                         lambda _: shlex.quote(SCRIPTS_DIR + "/"), cmd)
        command = f"{shlex.quote(sys.executable)} {cmd}"
    elif cmd_type == "shell":
        command = cmd
    else:
        return f"<!-- Unknown command type: {cmd_type} -->", None, False

    try:
        code, output = _run(command)
    except OSError as e:
        code, output = 1, str(e)
    if code != 0:
        return (f"<!-- Command failed: {line}\nError: {output} -->",
                f"Command failed: {line}", False)
    return output, None, False


def render(template_path: str, context: dict) -> Rendered:
    """
    Render a template file.

    Frontmatter is stripped. A line containing `{{%` is replaced by its
    command's output split into lines; other lines have their variables
    substituted.
    """
    result = Rendered()
    for line in strip_frontmatter(read_lines(template_path)):
        if "{{%" in line:
            output, warning, is_vim = run_command_block(line, context)
            result.lines.extend(output.split("\n"))
            if warning:
                result.warnings.append(warning)
            result.has_vim_blocks = result.has_vim_blocks or is_vim
        else:
            result.lines.append(render_line(line, context))
    return result
