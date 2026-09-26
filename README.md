# meta-notes readme

## Purpose

This repository hosts a personal implementation of a note-tasking system that
operates as a notes, tasks, planning, and organization for my life. It is based
on the ideas of Tiago Forte's second brain and the PARA folder structure. Some
of the concepts are borrowed from wikis and Obsidian.

## PPARA Folder Structure

The system maintains five top-level folders:

- `plan/` - Planning notes (daily, weekly, quarterly, yearly)
  - `daily/`
  - `week/`
  - `quarter/`
  - `year/`
- `project/` - Active projects with specific goals and end dates
- `area/` - Areas of ongoing responsibility
- `resource/` - Resources and reference materials on various topics
- `archive/` - Archived items from projects, areas, and resources
  - `project/`
  - `area/`
  - `resource/`

Note: Folder names are singular.

### Plans

This folder contains planning notes for Cal Newport's multi-scale planning.
Notes are organized into folder by the timescale they are planning for. Daily
notes contain a daily time block and time log as well as a list of tasks to
complete for the day. Daily and weekly notes further contain a YY-QQ folder with
the two digit year and quarter to keep the folders from becoming excessively
large.

### Projects

You have projects you're actively working on – short-term efforts (in your work
or personal life) that you take on with a certain goal in mind. A project may
exist as a single note [[project/Order Christmas Presents]] or a folder for a
larger project [[project/kitchen-remodel/Tasks]].

### Areas

You have areas of responsibility – important parts of your work and life that
require ongoing attention. 

### Resources

Then you have resources on a range of topics you're interested in and learning about

### Archives

Finally, you have archives, which include anything from the previous three
categories that is no longer active, but you might want to save for future
reference.

## Project Structure

This plugin follows standard vim plugin conventions:

```
meta-notes/
├── bin/                 # Command line interface
│   └── meta-notes           # Shim that runs scripts/meta_notes
├── plugin/              # Main vim plugin files (auto-loaded by vim)
│   └── meta_notes.vim
├── autoload/            # Functions loaded on-demand
│   └── meta_notes/
│       ├── cli.vim          # Runs bin/meta-notes and decodes its JSON
│       ├── file_ops.vim     # File operations (archive, rename) via the CLI
│       ├── notes.vim        # Note navigation; opens notes via the CLI
│       ├── template.vim     # Runs {{% vim %}} blocks in rendered notes
│       └── time_tracking.vim # Time tracking functionality
├── after/               # After-directory for syntax highlighting
│   └── syntax/
│       └── markdown.vim
├── scripts/             # Python helper scripts
│   ├── meta_notes/          # meta-notes CLI package
│   │   ├── __main__.py          # Entry point (Python version check)
│   │   ├── brief.py             # Project brief
│   │   ├── ceremony.py          # Ceremony status
│   │   ├── calendar.py          # Agenda from a Google Calendar export
│   │   ├── changes.py           # Notes changed in a period, from git
│   │   ├── cli.py               # Subcommands, root resolution, output
│   │   ├── config.py            # .meta-notes read as TOML config
│   │   ├── conventions.md       # Conventions text for skills
│   │   ├── conventions.py       # Conventions, generated parts filled in
│   │   ├── init.py              # Notes root setup
│   │   ├── note.py              # Note paths and creation
│   │   ├── ops.py               # Move, rename, archive
│   │   ├── prime.md             # Agent guide text
│   │   ├── prime.py             # Agent guide, generated parts filled in
│   │   ├── project.py           # Project home notes and fields
│   │   ├── projects.py          # Project list and warnings
│   │   ├── query.py             # Task query
│   │   ├── time.py              # Time report
│   │   ├── root.py              # Sentinel search for the notes root
│   │   ├── task_update.py       # Task line edits
│   │   └── template.py          # Template discovery and rendering
│   ├── find_tasks.py        # Task selection and report
│   ├── notes.py             # Note utilities
│   ├── period.py            # --date day and period parsing
│   ├── tags.py              # Tag parsing and aliases
│   ├── tasks.py             # Task parsing and processing
│   ├── time_report.py       # Time tracking reports
│   ├── time_tracking.py     # Time log parsing
│   └── update_links.py      # Wiki-link updating
├── test/                # Tests
│   ├── *.vader              # Vimscript integration tests
│   ├── unit/                # Python unit tests
│   │   ├── test_brief.py
│   │   ├── test_calendar.py
│   │   ├── test_ceremony.py
│   │   ├── test_changes.py
│   │   ├── test_cli.py
│   │   ├── test_config.py
│   │   ├── test_conventions.py
│   │   ├── test_find_tasks.py
│   │   ├── test_init.py
│   │   ├── test_note.py
│   │   ├── test_notes.py
│   │   ├── test_period.py
│   │   ├── test_project.py
│   │   ├── test_projects.py
│   │   ├── test_ops.py
│   │   ├── test_prime.py
│   │   ├── test_query.py
│   │   ├── test_root.py
│   │   ├── test_shim.py
│   │   ├── test_tags.py
│   │   ├── test_task_update.py
│   │   ├── test_tasks.py
│   │   ├── test_template.py
│   │   ├── test_time_report.py
│   │   ├── test_time_tracking.py
│   │   └── test_update_links.py
│   └── fixtures/            # Test data/files
│       └── templates/           # Vim renderings of the shipped templates
├── doc/                 # Vim documentation
├── skills/              # Claude Code skills, linked into notes roots by init
├── templates/           # Planning templates and the cache README, copied by init
├── requirements.txt     # Pinned libraries for calendar, installed into .venv by init
├── run_tests.sh         # Test runner script
└── README.md
```

## Installation

### For Development (Recommended)

Add to your `.vimrc`:

```vim
" Add plugin to runtimepath
set runtimepath+=/Volumes/Data/work/meta-notes

" Optional: Quick mapping for reloading during development
nnoremap <leader>r :MetaNotesReload<CR>
```

### For Production Use

**Option 1: Symlink**
```bash
ln -s /Volumes/Data/work/meta-notes ~/.vim/pack/meta-notes/start/meta-notes
```

**Option 2: Plugin Manager**

This structure is compatible with vim-plug, Vundle, and Pathogen.

## Command Line

`bin/meta-notes` performs the plugin's setup (`init`), note creation from
templates (`note`), file operations (`move`, `rename`, `archive`), task
query (`tasks`), task edits (`task update`), time reports (`time`), changed
notes (`changes`), calendar agendas (`calendar`, `cache clear`), the
project list (`projects`), ceremony status (`ceremony status`), and the
skills' shared conventions (`conventions`), and a guide to the notes root
for agents (`prime`) outside Vim, for shells, agents, and other tools. The Vim
commands call it. Every command accepts `--json`. It needs Python 3.11 or newer as `python3`. See
`:help meta-notes-cli`.

`bin/meta-notes` runs the CLI with the notes root's virtualenv,
`<root>/.venv/bin/python3`, when it's executable, and falls back to the
`python3` on `PATH` otherwise. `meta-notes init` builds the virtualenv and
always runs on `python3` itself. Only `calendar` needs the virtualenv; every
other command works on either.

`meta-notes --version` (or `:MetaNotesVersion` in Vim) shows the installed
version and, for a git checkout, its commit.

Link it into a directory on your `PATH`; the shipped Claude Code skills call
`meta-notes` by name, and `init` warns if it isn't found. For example, with
the plugin installed by vim-plug into `~/.vim/bundle`:

```bash
ln -s ~/.vim/bundle/meta-notes/bin/meta-notes ~/bin/meta-notes
```

Set up a notes root by running `init` in its top-level directory. It creates
the PPARA folders, templates, a `.meta-notes` sentinel, and links the shipped
Claude Code skills into `.claude/skills/`. It also creates
`.meta-notes-cache/` (with `ics/` for calendar exports, `calendar/` for
parsed calendars, and a README), adds `.venv/` and `.meta-notes-cache/` to
the root's `.gitignore` (or warns when there isn't one), and builds `.venv`
with `python3 -m venv` and `pip install -r requirements.txt`. Pass
`--python PATH` to build it with another interpreter (3.11 or newer). If
the virtualenv can't be built, init still succeeds and warns that calendar
support isn't available. Re-running is safe and leaves an existing `.venv`
alone; `init --force` rebuilds it.

init also checks that the root's `CLAUDE.md` loads the agent guide (see
[Agents](#agents)) and prints the line to add when it doesn't. It never
edits `CLAUDE.md`.

```bash
mkdir notes && cd notes && git init && touch .gitignore
meta-notes init
meta-notes init --python ~/.pyenv/versions/3.12.4/bin/python3  # another interpreter
meta-notes note daily                    # create today's daily note, print its path
meta-notes note weekly 2026-04-02 --render --json
meta-notes note new "project/trip/Packing" --template checklist
bin/meta-notes archive 'project/2024-*'
bin/meta-notes move project/foo area/foo --json
bin/meta-notes tasks --all --folder project --status all
meta-notes tasks --overdue --due          # overdue and due today
meta-notes tasks --scheduled --date 2026-11 --group-by tag
meta-notes task update project/foo.md:3 --expect '- [ ] call Sam 📅 2026-09-22' --status x
meta-notes time                           # today's time report
meta-notes time --date 2026-09 --json     # a month's time summary
meta-notes changes --date 2026-09-21..2026-09-25  # notes changed this week
meta-notes projects --warnings            # stalled or unreviewed projects
meta-notes project brief project/kitchen/  # one project's files, tasks, dates
meta-notes ceremony status --date 2026-09-25
meta-notes calendar --date 2026-09-28..2026-10-02  # agenda from the latest export
meta-notes calendar --ics ~/Downloads/export.zip --json
meta-notes calendar --date 2026-09 --with zach --search 1:1  # filtered
meta-notes cache clear                    # delete parsed calendars, keep exports
meta-notes conventions                    # syntax and rules the skills follow
meta-notes prime                          # guide to the notes root for agents
```

Other commands find the notes root by walking up from the current directory
to the nearest `.meta-notes`, stopping after `$HOME`. Notes roots created
before the sentinel existed need `meta-notes init` run once (and the new
`.meta-notes` committed); until then, pass `--root` or set
`META_NOTES_ROOT`.

### Calendar

`meta-notes calendar` reads meetings from a Google Calendar export (Settings,
Import & export, Export). Save the downloaded `.zip` into
`.meta-notes-cache/ics/`; each run uses the newest, keeps the latest 5, and
caches what it parses in `.meta-notes-cache/calendar/`. Settings go in a
`[calendar]` table in `.meta-notes`, which is read as TOML:

```toml
[calendar]
email = "me@example.com"        # hide events you declined
timezone = "America/New_York"   # display timezone (default: system)
stale_days = 3                  # warn when the export is older
calendars = ["me@example.com"]  # zip calendars to load (default: all)
```

See `:help meta-notes-cli-calendar` and `:help meta-notes-config`.

### Agents

`meta-notes prime` prints a guide to the notes root for an agent: the
folders and naming, where the plan notes are (with today's paths), the
working day, projects, the archive, the commands for finding things, the
skills, and the conventions. Add this line to the notes root's
`CLAUDE.md`:

```markdown
Run `meta-notes prime` at the start of every session and follow it.
```

Keep your personal preferences (routines, habits, other working hours)
in `CLAUDE.md` too; they override the guide. See
`:help meta-notes-cli-prime`.

## Planning Skills

The Claude Code skills in `skills/` run the planning ceremonies in
`docs/planning-system.md`. `meta-notes init` links them into a notes root;
re-run it after updating the plugin to link new ones. Each starts from
`meta-notes conventions` and edits notes only through the CLI. The
`calendar` skill answers questions about your meetings and is read-only.

| Skill | When |
|-------|------|
| `daily-shutdown` | End of each workday; offers `daily-plan` |
| `daily-plan` | After shutdown, or the next morning |
| `weekly-review` | Friday morning; summary for your manager |
| `weekly-plan` | Friday afternoon; next week's priorities |
| `task-cleanup` | Anytime, 5–10 minutes of stale tasks |
| `project-review` | One project at a time |
| `calendar` | Anytime: meetings with someone, about a topic, or free time |

Daily notes carry `- [ ] plan complete` and `- [ ] shutdown complete`,
weekly notes `- [ ] review complete` and `- [ ] plan complete`. The skills
check them, and `meta-notes ceremony status` reports them.

## Key Mappings

All plugin mappings are defined in the plugin (not in the user's `.vimrc`) and
use `<localleader>` so they don't conflict with global mappings. Filetype-specific
mappings live in `after/ftplugin/<filetype>.vim` and are buffer-local.

### Global mappings

| Key | Command | Description |
|-----|---------|-------------|
| `<localleader>mr` | `:MetaNotesReload` | Reload plugin (development) |

### Markdown mappings

| Key | Command | Description |
|-----|---------|-------------|
| `<localleader>l` | `:MetaNotesOpen` | Follow wiki link under cursor |
| `<localleader>n` | `:MetaNotesDaily` | Open today's daily note |
| `<localleader>np` | `:MetaNotesDailyPrev` | Navigate to previous daily note |
| `<localleader>nn` | `:MetaNotesDailyNext` | Navigate to next daily note |

## Development Workflow

1. Edit your vim or Python scripts
2. In vim, run `:MetaNotesReload` (or press `<leader>r` if mapped)
3. Test immediately - no vim restart needed!

For individual file changes, you can also `:source %` while editing the file.

## Testing

### Setup

Install [vader.vim](https://github.com/junegunn/vader.vim):

```bash
git clone https://github.com/junegunn/vader.vim.git ~/.vim/pack/testing/start/vader.vim
```

Or add to `.vimrc` with your plugin manager.

### Running Tests

**From within vim:**
```vim
:TestMetaNotes
```

**From command line:**
```bash
vim -u NONE -c 'source ~/.vim/pack/testing/start/vader.vim/plugin/vader.vim' \
    -c 'Vader! test/*.vader'
```

### Writing Tests

Tests use vader.vim syntax and live in the `test/` directory. Example:

```vader
Execute (Test PARA folder detection):
  let folders = meta_notes#para#GetFolders()
  AssertEqual 4, len(folders)
  Assert index(folders, 'project') >= 0
```

