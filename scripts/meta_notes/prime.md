# meta-notes guide

This directory is a meta-notes notes root: the user's notes, tasks, and
plans as plain markdown. Read this guide before working here, and follow
the conventions at the end for every edit. Run `meta-notes` from anywhere
inside the root; paths are relative to it.

The user's own preferences (routines, habits, exceptions to anything
below) are in the root's `CLAUDE.md` and override this guide.

## Folders

| Folder | Holds |
|---|---|
| `plan/` | Daily, weekly, quarterly, and yearly plan notes |
| `project/` | Active projects: short-term efforts with a goal and an end |
| `area/` | Areas: ongoing responsibilities with no end date |
| `resource/` | Reference material on any topic |
| `archive/` | Inactive projects, areas, and resources |

- An area may hold projects or link to projects in `project/`, and may
  link to related resources.
- A resource may relate to a project or area, or to none. Notes from
  general meetings, not tied to one project or area, go in `resource/`.
- `resource/template/` holds the note templates.

Naming:

- Folders are lowercase, with dashes instead of spaces:
  `project/kitchen-remodel/`.
- Notes are Title Case, with spaces, ending in `.md`:
  `project/kitchen-remodel/Meetings & Notes.md`.
- Plan notes are named by date (below).
- Other files (images, PDFs, CSV, JSON) can sit beside the notes that
  use them.

## Plan notes

| Kind | Path | Today |
|---|---|---|
<!-- generated: today-paths -->

`YY-QN` is the two-digit year and quarter; a week's note is named for its
Monday and filed by that Monday's quarter. Create or find one with
`meta-notes note daily|weekly|quarterly|yearly [YYYY-MM-DD]`, which
prints its path and never overwrites. Each daily note links its week, and
each week its quarter.

Daily note sections:

<!-- generated: daily-sections -->

Weekly note sections:

<!-- generated: weekly-sections -->

How they're used:

- The daily note's Notes and Follow Up sections hold the day's notes and
  what to pick up next workday. Notes about a project, area, or resource
  go in that item's own notes, linked from the daily note.
- The weekly note's Review holds the week's summary; its Plan holds next
  week's priorities.
- Daily and weekly notes carry ceremony markers (`- [ ] plan complete`
  and others; see conventions) that the planning skills check off.

### Working day

Work runs 08:00 to 17:00, Monday to Friday. Don't plan work after 17:00.
The time block runs to 18:00 on purpose: the last rows hold after-work
personal events as reminders, and occasional late work. Don't remove or
fill them with work. Meetings and personal time the user has placed in
the time block stay where they are.

### Time tracking

Under `### Log`, each entry is a bullet naming the activity, with tags,
and `start:` and `end:` sub-bullets:

```markdown
- Kitchen quotes #kitchen #meeting
  * start: 9:30
  * end:   10:15
  * any other sub-bullet is a note
```

Times are `9:30`, `3:20pm`, or a full `2026-09-26 08:00`; a bare time
takes the date of the note. `meta-notes time [--date PERIOD]` reports
time by tag and by these groups:

<!-- generated: tag-groups -->

`### Time Block` is a table of 15-minute rows: Plan is what was planned,
Actual a short summary of what happened. The log is the record; Actual
repeats it briefly.

## Projects

A project is a note directly in `project/` (`project/Make Bread.md`) or a
folder directly in `project/` with a home note `Home.md`
(`project/kitchen-remodel/Home.md`). Everything under the folder belongs
to the project.

- `Home.md` is short: the project fields, key links, people, and dates.
  Details live in other notes.
- `Tasks.md` holds the project's tasks; done tasks may move to a
  `## Completed` section.
- `Meetings & Notes.md` holds meeting and other notes under dated
  headings, newest first: `## 2026-09-25 Fri Kickoff`. Dated headings
  count as project activity.
- Other notes are free-form, linked from `Home.md`.

Fields, status, and the `#next`, `#review`, and `#deadline` tags are in
the conventions below. Every active project should have an open `#next`
task. `meta-notes projects` is the project list, with each project's
status, latest date, last review, and warnings; there is no hand-kept
list. `meta-notes project brief <path>` reports one project's files,
tasks, and dates. The `project-review` skill reviews one project at a
time.

A project that becomes an ongoing responsibility is converted to an area
with `meta-notes move project/<name> area/<name>`, after the user
confirms.

## Archive

Finished or inactive projects, areas, and resources move to `archive/`
under their original path: `project/kitchen-remodel/` becomes
`archive/project/kitchen-remodel/`. Archiving a project also sets
`status: archived` and `archived: YYYY-MM-DD` in its home note. Links to
archived notes are updated, so they keep resolving, and archived notes
stay searchable and in task queries (`--folder` narrows a query).
Archive only with `meta-notes archive <path>`, after the user confirms;
never with `mv`.

## Finding things

| Command | Example |
|---|---|
| `tasks` | `meta-notes tasks --overdue --due --json` |
| `projects` | `meta-notes projects --warnings` |
| `project brief` | `meta-notes project brief project/kitchen-remodel/` |
| `changes` | `meta-notes changes --date 2026-09-21..2026-09-25` |
| `calendar` | `meta-notes calendar --date 2026-09-28 --json` |
| `ceremony status` | `meta-notes ceremony status --date 2026-09-25` |
| `time` | `meta-notes time --date 2026-09 --json` |

Every command takes `--json` and `--help`. Otherwise use `rg` over the
root; plan notes are the fastest way to find what happened on a day.

## Skills

The plugin's skills, in `.claude/skills/`, run the planning ceremonies
and answer calendar questions. Use them when the user asks for a
ceremony:

<!-- generated: skills -->

<!-- generated: conventions -->
