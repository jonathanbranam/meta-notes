# Agentic AI

## Project

This is a life management solution that works in vim / neovim and uses plain
text markdown files to manage all aspects of personal organization.

Scripts should generally be written in vimscript for compatibility. Larger, more
complicated work can be written in Python and executed by the shell. Avoid using
Python libraries.

## Testing

The plugin uses [vader.vim](https://github.com/junegunn/vader.vim) for testing.

### Setup

Install vader.vim (one-time):
```bash
mkdir -p ~/.vim/pack/testing/start
git clone https://github.com/junegunn/vader.vim.git ~/.vim/pack/testing/start/vader.vim
```

### Running Tests

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


