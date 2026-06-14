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
├── plugin/              # Main vim plugin files (auto-loaded by vim)
│   └── meta_notes.vim
├── autoload/            # Functions loaded on-demand
│   └── meta_notes/
│       ├── file_ops.vim     # File operations (archive, rename)
│       ├── notes.vim        # Note management and navigation
│       ├── template.vim     # Template processing
│       └── time_tracking.vim # Time tracking functionality
├── after/               # After-directory for syntax highlighting
│   └── syntax/
│       └── markdown.vim
├── scripts/             # Python helper scripts
│   ├── find_tasks.py        # Task discovery and filtering
│   ├── notes.py             # Note utilities
│   ├── tasks.py             # Task parsing and processing
│   ├── time_report.py       # Time tracking reports
│   ├── time_tracking.py     # Time log parsing
│   └── update_links.py      # Wiki-link updating
├── test/                # Tests
│   ├── *.vader              # Vimscript integration tests
│   ├── unit/                # Python unit tests
│   │   ├── test_find_tasks.py
│   │   ├── test_notes.py
│   │   ├── test_tasks.py
│   │   ├── test_time_tracking.py
│   │   └── test_update_links.py
│   └── fixtures/            # Test data/files
├── doc/                 # Vim documentation (future)
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

