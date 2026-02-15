# meta-notes readme

## Purpose

This repository hosts a personal implementation of a note-tasking system that
operates as a notes, tasks, planning, and organization for my life. It is based
on the ideas of Tiago Forte's second brain and the PARA folder structure. Some
of the concepts are borrowed from wikis and Obsidian.

## PARA Folder Structure

The top level has exactly four folders:

- project: holds currently active projects
- area: holds areas of responsibility
- resource: holds resources about various topics
- archive: contains an archive of projects, areas, and resources that are no
  longer currently relevant
  * project
  * area
  * resource

NOTE: The folder names are singular.

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
├── plugin/           # Main vim plugin files (auto-loaded by vim)
│   └── meta_notes.vim
├── autoload/         # Functions loaded on-demand
│   └── meta_notes/
│       ├── para.vim      # PARA folder operations
│       ├── notes.vim     # Note management
│       └── tasks.vim     # Task management
├── ftplugin/         # Filetype-specific settings
│   └── markdown.vim
├── syntax/           # Custom syntax highlighting
├── scripts/          # Python helper scripts
│   ├── link_parser.py
│   ├── task_processor.py
│   └── para_tools.py
├── test/             # Vader.vim tests
│   ├── para.vader
│   ├── notes.vader
│   ├── tasks.vader
│   └── fixtures/     # Test data/files
├── doc/              # Vim documentation
│   └── meta-notes.txt
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

