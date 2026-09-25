## Context

`scripts/find_tasks.py` has two code paths today. With no filters it prints
the week-bucketed report (`generate_report`, `collect_categorized_tasks`),
and with any filter it prints a flat report grouped by file
(`generate_filtered_report`). `is_filtered` picks between them.
`scripts/meta_notes/query.py` calls both paths to build the text and JSON
for `meta-notes tasks`, and `cli.py` mirrors the `find_tasks.py` options.

`scripts/tasks.py` treats every `- [?]` line as a task and recognizes only
🗓 and 📆 as due dates. Tags are parsed only in `scripts/time_tracking.py`,
whose `Tag` class applies `TAG_ALIASES` on construction.

The standalone scripts import each other as top-level modules from
`scripts/`, and the CLI puts `scripts/` first on `sys.path`
(`meta_notes/__main__.py`), so a new top-level module in `scripts/` is
importable from both. Everything is stdlib only.

Templates run `find_tasks.py` through `{{% python ... %}}` blocks. A
non-zero exit already renders as a `<!-- Command failed: ... -->` comment
with the error text, plus a CLI warning (`template` spec).

## Goals / Non-Goals

**Goals:**
- One selection pipeline in `find_tasks.py` that both the script and
  `meta-notes tasks` use, so their text output can't drift apart.
- Shared tag and period parsing that `time-report-enhancements` and
  `planning-skills` import without changes.

**Non-Goals:**
- Task age and blame (`task-age`).
- Editing task lines (`task-update`).
- Tag groups (`TAG_GROUPS`) for tasks. They stay a time tracking concept.
- Keeping the removed options as aliases.

## Decisions

### Shared modules: `scripts/tags.py` and `scripts/period.py`

`tags.py` holds the tag pattern `#([\w-]+)` (`\w` already covers `_`),
`TAG_ALIASES`, and two functions: `canonical_tag(name)`, which maps a tag
name with or without `#` to its canonical name without `#`, and
`parse_tags(text)`, which returns canonical names in order of appearance
with duplicates removed. Matching is case-insensitive, and names keep the
case of their first occurrence except where an alias replaces them.
`time_tracking.Tag.__post_init__` calls `canonical_tag` and re-adds the `#`,
so time tracking's behavior and its `TAG_ALIASES` name (re-exported) don't
change.

`period.py` holds `parse_period(text) -> (start, end)`, raising
`ValueError` with a message that lists the accepted forms. It is a small
set of anchored regexes, one per form, tried in order. A range whose start
is after its end is an error.

*Alternatives:* putting both in `meta_notes/` (the standalone scripts
couldn't import them without path hacks), or keeping tags in
`time_tracking.py` (tasks would import a time tracking module to parse a
tag).

### Task model changes stay in `tasks.py`

- `_parse_task_dates` accepts 📅, 📆, and 🗓 for the due date.
- `find_tasks_in_file` keeps a checkbox line only when it contains a due
  emoji (dated or bare) or a `🛫` followed by a valid date. A due emoji
  followed by no date, or by an invalid one, makes the task undated. `Task`
  gains `undated: bool` so "bare due emoji" is explicit and doesn't have to
  be inferred from `due_date is None`.
- `Task` gains `tags: list[str]` from `tags.parse_tags`, and a property
  `effective_due`: the ✅ date for a completed task that has one, otherwise
  `due_date`. Every mode compares against `effective_due`, never
  `due_date` directly.

### One selection function with section priority

`find_tasks.select(tasks, modes, start, end, later)` returns
`(section, task)` pairs. For each task it walks the fixed order `overdue`,
`due`, `scheduled`, `ready`, `future`, `undated`, and keeps the first
selected mode whose predicate matches, so overlapping modes print each task
once. `--all` expands to `ready`, `future`, `undated`. No mode means
`ready`. `#later` tasks (tag `later`, any case) are dropped before selection
unless `later` is set. `--status`, `--folder`, and `--tag` filter before
selection.

Predicates, with `d = effective_due` and `s = start_date`:

| Mode | Match |
|---|---|
| overdue | `d < START` |
| due | `START <= d <= END` |
| scheduled | `START <= d <= END` or `START <= s <= END` |
| ready | `d <= END` or `s <= END` |
| future | has `d` or `s`, and not ready |
| undated | `undated` and no `s` |

*Alternative:* one pass per mode, then removing duplicates. It is more code
and the output order is harder to state in the spec.

### Output layout

- **One mode selected** (including the default): no section heading, which
  is the same shape as today's filtered report. The daily template's two
  blocks render the same as today, apart from the tasks they now leave out.
- **Several modes:** a `# <Section>` heading per non-empty section
  (`# Overdue`, `# Due`, `# Scheduled`, `# Ready`, `# Future`, `# Undated`).
- Within a section, files are sorted by path and tasks keep file order.
  Standard format uses a `## [[link]]` heading per file and condensed format
  a `- [[link]]` item, as today.
- **`--group-by tag`:** within each section, a `## <tag>` heading per tag
  (sorted ignoring case, `Not tagged` last). In standard format, file
  headings under a tag drop to `###`. Condensed format is unchanged under
  the tag heading.
- The standard-format summary line stays, counting unique tasks.
- The empty-result messages stay as they are ("No markdown files found.",
  "No tasks found matching the criteria.").

This replaces `generate_report`, `collect_categorized_tasks`,
`categorize_task_by_date`, `is_filtered`, `filter_tasks_by_due_date`, and
`parse_date_filters`. `notes.calculate_week_end` loses its last caller and
is removed.

### CLI and JSON

`cli.py` and `find_tasks.py` declare the same options: `--date`,
`--scheduled`, `--due`, `--overdue`, `--ready`, `--future`, `--undated`,
`--all`, `--later`, `--tag` (repeatable), `--group-by {tag}`, and the kept
`--folder`, `--status`, `--format`, and `--condensed`. `query.run` calls
`select` once and builds the text lines and the JSON list from the same
pairs. Each JSON task gains `tags` and `section` and loses `category`. A
task under several tags in `--group-by tag` appears once in JSON. Grouping
is presentation only.

An invalid `--date` is a usage error: `find_tasks.py` prints it to stderr
and exits 1, as for invalid dates today, and the CLI reports it through its
normal error path (a JSON `error` with `--json`).

## Risks / Trade-offs

- [Existing notes roots keep old daily templates that call `--due-on` and
  `--due-by`] → Those blocks render as the failed-command comment with the
  usage error, and the note is still created. The release notes and
  `:help` give the two-line replacement.
- [Plain checkboxes vanish from task lists] → Intended. A checklist item
  that should be tracked gets a bare 📆.
- [Aliases now apply to tasks: `#mtg` shows as `meeting` in tag groups] →
  The line itself is printed unchanged, so only the grouping heading and
  JSON `tags` change.
- [JSON `category` is removed] → The only consumer is the CLI's own
  callers. No shipped skill reads `category`.
- [The ✅ rule changes `--overdue` for completed tasks] → Only with
  `--status completed` or `all`. The default `incomplete` is unaffected.

## Migration Plan

Ship as one release, with a MINOR version bump on archive. Users replace
`--due-on {{date:%Y-%m-%d}}` with `--due --date {{date:%Y-%m-%d}}` and
`--due-by {{date-1:%Y-%m-%d}}` with `--overdue --date {{date:%Y-%m-%d}}`
in their copied `resource/template/daily.md`, or re-run `meta-notes init --force` if
they haven't edited the templates. Rollback means reverting the release. No
note content changes.
