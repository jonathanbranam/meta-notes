# Meta-Notes Requirements

## Overview

A life management system for vim/neovim based on the PARA methodology (Projects, Areas, Resources, Archive). Uses plain text markdown files with wiki-style [[links]] for navigation and organization.

## PARA Folder Structure

The system maintains four top-level folders:

- `project/` - Active projects with specific goals and end dates
- `area/` - Areas of ongoing responsibility
- `resource/` - Resources and reference materials on various topics
- `archive/` - Archived items from projects, areas, and resources
  - `archive/project/`
  - `archive/area/`
  - `archive/resource/`

Note: Folder names are singular.

## Template System

### Standard Templates

Located in `resource/template/`:
- `daily.md` - Daily note template
- `weekly.md` - Weekly plan template
- `quarterly.md` - Quarterly plan template
- `yearly.md` - Yearly plan template

Templates use YAML frontmatter for metadata, including customizable filename patterns.

### Folder-Specific Templates

Any folder can contain a visible `template.md` file that will be used when creating new notes in that folder.

## Plan & Note Structure

### File Locations

**Daily Notes:**
- Path: `resource/plan/daily/YY-QQQ/YYYY-mm-dd ddd.md`
- Example: `resource/plan/daily/26-Q1/2026-02-13 Thu.md`
- YY = two-digit year
- QQQ = quarter (Q1, Q2, Q3, Q4)
- YYYY-mm-dd = full date
- ddd = three-letter day abbreviation

**Weekly Plans:**
- Path: `resource/plan/week/YY-QQ/YYYY-mm-dd.md`
- Date is the Monday of the week
- YY = two-digit year
- QQ = quarter (Q1, Q2, Q3, Q4)
- Example: `resource/plan/week/26-Q1/2026-02-09.md`

**Quarterly Plans:**
- Path: `resource/plan/quarter/YYYY-QQ.md`
- Example: `resource/plan/quarter/2026-Q1.md`

**Yearly Plans:**
- Path: `resource/plan/year/YYYY.md`
- Example: `resource/plan/year/2026.md`

### Linking Hierarchy

Plans and notes are linked in the following structure:

- Daily note → Weekly plan (daily links to its week)
- Weekly plan ↔ Quarterly plan (bidirectional)
- Quarterly plan ↔ Yearly plan (bidirectional)
- Quarterly plans do NOT link to individual weeks
- Weekly plans link UP to quarterly plan

## Task Organization

- **Project tasks** live within project folders/notes
- **Daily notes** organize the day's work
- Tasks from projects can be copied or referenced in daily notes with wiki-links back to the source project
- Task status tracking: incomplete, completed, rescheduled, canceled
- Task dates use emojis:
  - 🛫 YYYY-MM-DD for start_date
  - 🗓 or 📆 YYYY-MM-DD for due_date
  - ✅ YYYY-MM-DD for completed_date

## Commands

### Note Creation & Opening

- `:MetaNotesOpen` - Open/create note from wiki-link under cursor
- `:MetaNotesDaily [YYYY-MM-DD]` - Open/create today's daily note or specific date
- `:MetaNotesWeekPlan [YYYY-MM-DD]` - Open/create current week plan or specific week
- `:MetaNotesQuarterPlan` - Open/create current quarter plan
- `:MetaNotesYearPlan` - Open/create current year plan

### Navigation

- `:MetaNotesDailyPrev` - Jump to previous existing daily note
  - If at oldest note, show message
- `:MetaNotesDailyNext` - Jump to next existing daily note
  - If at newest note, prompt to create next day's note
- `:MetaNotesJumpToWeek` - Navigate from daily note to its corresponding weekly plan

These navigation commands scan the filesystem for existing notes and skip over missing dates.

### File Operations

- `:MetaNotesArchive [path]` - Move folder or note to archive
  - Single item: `project/kitchen-remodel` → `archive/project/kitchen-remodel`
  - Batch with wildcards: `:MetaNotesArchive project/kitchen-remodel/*`
  - Updates all wiki-links referencing archived items
  - Future: May add interactive selection interface

- `:MetaNotesRename [new-name]` - Rename current note
  - Updates all wiki-links across entire system that reference this note

**Link Update Requirements:**
- When moving folders or renaming notes, scan entire system for wiki-link references
- Update all [[old/path]] → [[new/path]] references
- Must be reliable and complete
- Can be implemented in Python or Bash

## Task Discovery & Search

### Task Finding Script

The `scripts/find_tasks.py` script finds tasks across all notes and supports filtering:

**Filter by location:**
- `--folder project/kitchen-remodel` - Find tasks in specific folder
- Includes subfolders by default

**Filter by date:**
- `--due-on YYYY-MM-DD` - Tasks due on specific date
- `--due-by YYYY-MM-DD` - Tasks due on or before date
- `--due-between YYYY-MM-DD YYYY-MM-DD` - Tasks due within date range

**Filter by status:**
- `--status incomplete|completed|rescheduled|canceled` - Filter by task status
- Multiple filters can be combined

**Output formats:**

1. **Standard format** (default):
   ```markdown
   ## [[path/to/note]]
   - [ ] Task text from original file
   - [x] Another task
   ```
   - H2 markdown header with wiki-link to the note
   - Tasks appear verbatim from their original files

2. **Condensed format** (flag-controlled):
   ```markdown
   - [[path/to/note]]
     - [ ] Task text from original file
     - [x] Another task
   ```
   - First level bullet with wiki-link: `- [[path/to/note]]`
   - Tasks indented with two spaces below the link

The output format is controlled by command-line flags. Can be used standalone or called from templates.

## Dynamic Template Content

Templates can include commands that execute when a note is created. The command output replaces the markup in the final note.

### Command Execution Syntax

Use wrapped command syntax:

```markdown
{{% vim MetaNotesListTasks %}}
{{% python scripts/find_tasks.py --due-on {{today}} %}}
{{% shell echo "Hello World" %}}
```

**Command types:**
- `vim` - Execute vim command
- `python` - Execute Python script
- `shell` - Execute shell command

### Template Variables

Templates support variable substitution with optional date formatting:

**Core variables:**
- `{{date}}` - The date of the note being created (for daily notes, this is the daily note's date)
- `{{today}}` - Today's actual date
- `{{week_start}}` - Monday of the week
- `{{week_end}}` - Sunday of the week

**Date arithmetic:**
- `{{today+1}}` - Tomorrow
- `{{today-1}}` - Yesterday
- `{{date+7}}` - One week from note date
- `{{week_start-7}}` - Previous week's Monday
- Any variable can use +/- with number of days

**Date formatting:**
- `{{today:%Y-%m-%d}}` - Custom format using strftime syntax
- `{{week_start:%B %d, %Y}}` - "February 09, 2026"
- `{{date:%A}}` - Day name
- Default format is `YYYY-MM-DD ddd` (e.g., "2026-02-13 Thu")

All date formatting uses Python strftime format specifiers.

**Variable scope:**
- Template variables work in any template file anywhere
- Supported in both standard templates (`resource/template/`) and folder-specific `template.md` files

### Command Execution Behavior

**Timing:**
- Commands execute only when a note is created
- Commands do NOT execute when opening an existing note
- Markup is replaced with command output in the created note

**Output handling:**
- Command output is included verbatim in the note
- No trimming, formatting, or indentation adjustments
- Raw output from command appears in final note

**Error handling:**
- If a command fails, include error details in HTML comment
- Error comment includes:
  - Original command text
  - Note that command failed
  - Any error output from the command
- Example: `<!-- Command failed: {{% python script.py %}} \n Error: File not found -->`
- Note creation continues despite command failures

### Example Template

```markdown
# Daily Note - {{date}}

Week Plan: [[resource/plan/week/Plan {{week_start}}]]

## Tasks Due Today
{{% python scripts/find_tasks.py --due-on {{date:%Y-%m-%d}} --status incomplete --condensed %}}

## Overdue Tasks
{{% python scripts/find_tasks.py --due-by {{date-1:%Y-%m-%d}} --status incomplete --condensed %}}

## Notes

## Time Tracking

### Log

### Time Block

| Time    | Plan                                 | Actual                      |
| ------- | ------------------------------------ | --------------------------- |
| 8:00am  |                                      |                             |
| 8:15am  |                                      |                             |
| 8:30am  |                                      |                             |
| 8:45am  |                                      |                             |
| 9:00am  |                                      |                             |
```

## Note Management

### Wiki-Style Links

- Link format: `[[path/to/note]]`
- Links do not include `.md` extension
- Links are relative to the repository root
- Following a link opens or creates the note

### Note Creation

- When creating a note from a link, apply appropriate template:
  - Use folder-specific `template.md` if present
  - Use standard template for daily/weekly/quarterly/yearly notes
  - Create basic header if no template exists
- New notes get a header: `# path/to/note`

### YAML Frontmatter

Notes can include YAML frontmatter to alter behavior. Frontmatter is optional and used sparingly.

**Format:**
```markdown
---
key: value
---

# Note content begins here
```

**Current use cases:**

- `encrypted: true` - Encrypts the entire note body (below frontmatter)
  ```markdown
  ---
  encrypted: true
  ---

  [encrypted content here]
  ```

**Future use cases:**

- Section-level encryption/decryption
- Content delimited by `---` or `***` could be encrypted/decrypted independently
- Other note-specific behavior modifications as needed

## Technical Requirements

### Platform & Compatibility

- Must work in vim and neovim
- Scripts written in vimscript for compatibility
- Larger/complex operations can use Python (avoid external libraries) or Bash
- Plain text markdown files only

### Testing

- Vimscript plugin tests use vader.vim
- Python scripts use pytest with bare functions (not test classes)
- Test organization:
  - Vimscript: `test/*.vader`
  - Python: `test/unit/test_*.py`

### Plugin Structure

Follow standard vim plugin conventions:
- `plugin/` - Main plugin files (auto-loaded)
- `autoload/` - Functions loaded on-demand
- `ftplugin/` - Filetype-specific settings
- `scripts/` - Python/Bash helper scripts
- `test/` - Test files
- `doc/` - Vim documentation

## Time Tracking

Daily notes include a comprehensive time tracking system with activity logging and time block planning.

### Time Log

Located under `### Log` within the `## Time Tracking` section of daily notes.

**Format:**
```markdown
### Log

- arrived:
  * end:   2026-02-13 Fri 08:00
- #setup at desk
  * start: 2026-02-13 Fri 08:00
  * end:   2026-02-13 Fri 08:08
- bio #break
  * start: 2026-02-13 Fri 08:08
  * end:   2026-02-13 Fri 08:20
- #plan the day
  * start: 2026-02-13 Fri 08:20
  * end:   2026-02-13 Fri 08:45
- check #slack and #email
  * start: 2026-02-13 Fri 08:45
  * end:   2026-02-13 Fri 09:00
- #personal appointment
  * start: 2026-02-13 Fri 09:00
  * end:   2026-02-13 Fri 10:00
```

**Structure:**
- Top-level bullet: Activity description (can include tags anywhere)
- Sub-bullets: `start:` and `end:` timestamps
- Timestamp format: `YYYY-MM-DD ddd HH:MM`
- Special case: `arrived:` entry only has `end:` timestamp

### Time Block Table

Located under `### Time Block` within the `## Time Tracking` section of daily notes.

**Format:**
```markdown
### Time Block

| Time    | Plan                                 | Actual                      |
| ------- | ------------------------------------ | --------------------------- |
| 8:00am  | plan: review day                     | plan: review day            |
| 8:15am  | dev: feature work                    | [coffee break]              |
| 8:30am  | dev: feature work                    | ~~email: inbox~~            |
| 9:00am  | mtg: standup                         | mtg: standup                |
| 9:15am  | mtg: standup                         | mtg: standup                |
| 9:30am  | dev: feature store                   |                             |
| 9:45am  | pers: appointment                    |                             |
| 10:00am | mtg: with Bob                        |                             |
| 10:15am | ~schedule the day~                   | talked to Mary              |
```

**Structure:**
- 80-character width table
- Three columns: Time | Plan | Actual
- Time increments: 15 minutes from 8:00am to 6:00pm
- Time format: `H:MMam` or `HH:MMam`

**Entry format:**
- `name: details` - Standard entry (e.g., "mtg: Feature Store", "pers: pickup kids", "dev: feature work")
- `[entry]` - Break or non-productive period
- `~~entry~~` - Time not spent on-plan (off-plan)
- Empty cells allowed (not yet executed or recorded)

**Vim syntax highlighting:**
- Different highlighting for different entry types (mtg, dev, pers, etc.)
- Visual distinction for `[breaks]` and `~~off-plan~~` entries

### Tags

Tags use `#tag` syntax and can appear in:
- Time log entries
- Time block entries
- Task items

**Tag categories:**

**Special meaning tags (non-work time):**
- `#break` - Break time
- `#personal` - Personal time
- `#off-task` - Off-task time
- `#off-plan` - Time block not according to plan (also use `~~...~~` marker)

**Activity tags:**
- `#meeting` - All meetings
- `#recruiting` - Interviews and recruiting activities
- `#setup` - Setup activities
- `#plan` - Planning activities
- `#slack` - Slack communication
- `#email` - Email communication

**Project tags:**
- Each large project gets a tag (e.g., `#feature-store`, `#kitchen-remodel`)
- Free-form based on active projects

Tags are free-form with the above special cases having specific meanings for time calculations.

### Time Report

**Command:**
- Opens readonly buffer with time calculations
- Only available when inside a daily note
- Analyzes time log entries

**Calculations (general requirements):**
- Total time by tag
- Work vs non-work breakdown (based on special meaning tags)
- Plan vs actual comparison
- Time blocks on-plan vs off-plan percentage

**Implementation:**
- Written in Python due to complexity
- Parses time log entries
- Calculates durations from start/end timestamps
- Aggregates by tags
- Displays in readable format in readonly buffer

**Further details to be defined:**
- Specific output format
- Additional breakdowns and metrics
- Filtering options

## Areas for Further Definition

The following areas need additional requirements definition:

- Content structure for weekly/quarterly/yearly plan templates
- Additional search and filtering features
- Integration with external tools (calendar, etc.)
- Time report detailed output format and metrics
