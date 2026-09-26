# meta-notes guide

This is a meta-notes notes root: notes, tasks, and plans as markdown.
Follow this guide and the conventions below. The user's preferences are
in the root's `CLAUDE.md` and override this guide.

## Folders

- `plan/`: daily, weekly, quarterly, and yearly plan notes
- `project/`: active projects, short-term efforts with a goal
- `area/`: ongoing responsibilities; may hold or link to projects
- `resource/`: reference material, including notes from general
  meetings; `resource/template/` holds the note templates
- `archive/`: inactive projects, areas, and resources

Folders are lowercase with dashes (`kitchen-remodel/`). Notes are Title
Case with spaces (`Meetings & Notes.md`). Other files can sit beside the
notes that use them.

## Plan notes

Today's plan notes (`YY-QN` is year and quarter; a week is named for its
Monday):

<!-- generated: today-paths -->

`meta-notes note daily [YYYY-MM-DD]` (or `weekly`, `quarterly`, `yearly`)
creates one if needed and prints its path.

Notes about a project, area, or resource go in that item's notes,
linked from the daily note.

Work runs 08:00 to 17:00, Monday to Friday; don't plan work after 17:00.
The time block runs to 18:00 so the last rows can hold after-work
personal events. Keep them, and keep meetings and personal time the user
placed in the time block.

Time log entries go under the daily note's `### Log`, times as `HH:MM`:

```markdown
- Kitchen quotes #kitchen #meeting
  * start: 09:30
  * end:   10:15
```

<!-- generated: tag-groups -->

The `### Time Block` table has 15-minute rows: Plan is what was planned,
Actual a short summary of what happened.

## Projects

Besides `Home.md` (see conventions), a folder project usually has
`Tasks.md` and `Meetings & Notes.md`, the latter with dated headings,
newest first (`## 2026-09-25 Fri Kickoff`). Keep `Home.md` short: fields,
key links, people, and dates. `meta-notes projects` is the project list;
there is no hand-kept one. A project that becomes ongoing moves to an
area with `meta-notes move project/<name> area/<name>`.

## Archive

`meta-notes archive <path>` moves an item to `archive/<original path>`
(`archive/project/kitchen-remodel/`), sets `status: archived` and
`archived: YYYY-MM-DD` on a project, and updates links. Archived notes
stay searchable and in task queries.

## Commands

```
meta-notes tasks --overdue --due --json
meta-notes projects --warnings
meta-notes project brief project/kitchen-remodel/
meta-notes changes --date 2026-09-21..2026-09-25
meta-notes calendar --date 2026-09-28 --json
meta-notes ceremony status --date 2026-09-25
meta-notes time --date 2026-09 --json
```

Every command takes `--json` and `--help`.

<!-- generated: skills -->

<!-- generated: conventions -->
