# Agentic AI

## Project

This is a life management solution that works in vim / neovim and uses plain
text markdown files to manage all aspects of personal organization.

Scripts are written in Vimscript for compatibility; larger work is in Python
(3.11 or newer, standard library only) run by the shell. The details, and the
exception for commands that need a pinned library, are in
`.bridle/rules/languages.md`.

## Layout

- `plugin/meta_notes.vim`: the auto-loaded entry point; defines commands and
  `<localleader>` mappings (`.bridle/rules/key-mappings.md`).
- `autoload/meta_notes/`: on-demand Vimscript modules (cli, file_ops, notes,
  template, time_tracking).
- `after/syntax/`: markdown syntax extensions.
- `bin/meta-notes`: the CLI, which runs the `scripts/meta_notes/` package.
  Older helpers the plugin calls are `scripts/*.py`.
- `skills/`, `templates/`: product files installed into a notes root by
  `meta-notes init` (`.bridle/rules/product-skills.md`).
- `openspec/specs/<capability>/spec.md`: the behaviour specs
  (`.bridle/rules/specs.md`). `openspec/changes/archive/` is history.
- `doc/meta-notes.txt`: the Vim help file.

## Work Tracking

Work is tracked as bridle tasks (`bridle task`), run by bridle's agents on
the `bridle-adopt` trial branch. Project settings and agent rules are in
`.bridle/`: `config.toml`, and `rules/` for the conventions agents follow.
Beads, and later OpenSpec's change workflow, were used before.

## Testing

The plugin uses [vader.vim](https://github.com/junegunn/vader.vim) for testing.

### Setup

Install vader.vim (one-time):
```bash
mkdir -p ~/.vim/pack/testing/start
git clone https://github.com/junegunn/vader.vim.git ~/.vim/pack/testing/start/vader.vim
```

### Running Vimscript plugin Tests

Use the provided test script:

```bash
# Run all tests (default: clean output without vim startup noise)
./run_tests.sh

# Run specific test file
./run_tests.sh test/open_note.vader

# Run with quiet output (summary only)
./run_tests.sh --quiet

# Run with full vim debug output
./run_tests.sh --debug

# Run in interactive mode
./run_tests.sh --interactive

# Show help
./run_tests.sh --help
```

### From Vim

You can also run tests from within vim after loading the plugin:

```vim
:TestMetaNotes              " Run all tests
:Vader test/open_note.vader " Run specific test file
```

### Writing Tests

Tests are located in the `test/` directory with `.vader` extension. Example:

```vader
Execute (Setup):
  " Test setup code here

Given markdown (Description):
  # Sample content
  [[note/path]]

Execute (Test case):
  call cursor(2, 5)
  MetaNotesOpen
  AssertEqual expected, actual
```

See existing tests in `test/` for more examples. Tests that touch the file
system work in a temporary directory (`g:test_dir`); the setup and cleanup
pattern is in `.bridle/rules/vader-tests.md`.

## Python Unit Testing

Python code in `scripts/` is tested with pytest in `test/unit/`, one test file
per module, as bare functions named `test_<module>_<function>_<scenario>`
(`.bridle/rules/python-tests.md`).

```bash
# Run all Python unit tests
pipenv run pytest test/unit/

# Run specific test file
pipenv run pytest test/unit/test_tasks.py

# Run specific test function
pipenv run pytest test/unit/test_tasks.py::test_find_tasks_in_file_simple_uncompleted_task
```

## Versioning

The version lives in `scripts/meta_notes/__init__.py` (`__version__`) and is
reported by `meta-notes --version` and `:MetaNotesVersion`. Each
behaviour change bumps it (PATCH, MINOR or MAJOR) and is tagged `v<version>`;
who does which is in `.bridle/rules/versioning.md`.
