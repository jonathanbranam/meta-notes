# Agentic AI

## Project

This is a life management solution that works in vim / neovim and uses plain
text markdown files to manage all aspects of personal organization.

Scripts should generally be written in vimscript for compatibility. Larger, more
complicated work can be written in Python and executed by the shell. Avoid using
Python libraries.

## Issue Tracking

This project uses `br` (Beads) for issue tracking. See @br-guide.md for a guide
on how to use `br` effectively.

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

See existing tests in `test/` for more examples.

When writing vader tests that operate on the file system, always follow this
pattern. First create a temporary directory and cd to it. At the end of the
test, remove the temporary directory and cd back to the project root.

At the beginning of the .vader script:

```vim
Execute (Setup - Create temporary test directory):
  let g:test_dir = tempname()
  call mkdir(g:test_dir, 'p')
  " Store original directory and change to test root
  let g:original_dir = getcwd()
  execute 'cd' g:test_dir
```

In a test use `g:test_root` and be sure to create all necessary folders before
writing files.

```vim
Execute (Test that writes a file):
  " Create a sample note file
  call mkdir('note/path', 'p')
  call writefile(['# Sample Note', '', 'This is a test note.'],
        \ g:test_root . '/note/path/Filename.md')
```

Cleanup at the end of the vader script:

```vim
Execute (Cleanup):
  " Restore original directory
  execute 'cd' g:original_dir

  " Clean up test files
  call delete(g:test_root, 'rf')

  " Clean up variables
  unlet g:test_root
  unlet g:original_dir
```

## Python Unit Testing

Python scripts in the `scripts/` directory use pytest for unit testing.

### Test Organization

Tests are organized in `test/unit/` with one test file per module:
- `test/unit/test_tasks.py` - Tests for `scripts/tasks.py`
- `test/unit/test_notes.py` - Tests for `scripts/notes.py`
- `test/unit/test_find_tasks.py` - Tests for `scripts/find_tasks.py`

### Test Style

**Use bare functions instead of test classes:**

```python
# Good - bare functions with descriptive names
def test_find_tasks_in_file_simple_uncompleted_task(tmp_path):
    """Test finding a simple uncompleted task."""
    test_file = tmp_path / "test.md"
    test_file.write_text("- [ ] Simple task\n")

    tasks = tasks_module.find_tasks_in_file(str(test_file))

    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.PENDING

# Bad - don't use test classes
class TestFindTasksInFile:  # Avoid this
    def test_simple_uncompleted_task(self, tmp_path):
        ...
```

### Naming Conventions

Test functions should follow this pattern:
- `test_<module>_<function>_<scenario>`
- Example: `test_find_tasks_in_file_with_start_date`

Use comments to group related tests:
```python
# Tests for find_tasks_in_file function

def test_find_tasks_in_file_simple_task(tmp_path):
    ...

def test_find_tasks_in_file_with_dates(tmp_path):
    ...


# Tests for _extract_date function

def test_extract_date_valid(tmp_path):
    ...
```

### Running Python Tests

```bash
# Run all Python unit tests
pipenv run pytest test/unit/

# Run specific test file
pipenv run pytest test/unit/test_tasks.py

# Run with verbose output
pipenv run pytest test/unit/ -v

# Run specific test function
pipenv run pytest test/unit/test_tasks.py::test_find_tasks_in_file_simple_uncompleted_task
```

### Benefits of Bare Functions

- **Simplicity** - No unnecessary class structure
- **Clarity** - Function names are fully descriptive
- **Discovery** - pytest finds all `test_*` functions automatically
- **Flexibility** - No `self` parameter needed, cleaner fixtures
- **Focus** - Tests are organized by file, not by class hierarchy


## Beads Task Management Workflow

This project uses [Beads](https://github.com/steveyegge/beads) (`br`) for persistent task tracking across AI sessions. See @agent-tasks.md for complete installation and usage instructions.

### Session Start

### During Development

**View available tasks:**
```bash
br ready           # Show unblocked tasks ready to work on
br list            # Show all tasks
br search "river"  # full-text search
```

### Essential Workflow

```
1. br show <id>              # read the task
2. br update <id> --claim    # mark in_progress + assign to self
3. ... do the work ...
4. br close <id> -r "reason" # mark closed with a reason
5. br sync --flush-only      # export DB → JSONL (commit JSONL with your code changes)
```

**Always close with `-r` / `--reason`** — a one-sentence summary of what was done.

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   br sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
