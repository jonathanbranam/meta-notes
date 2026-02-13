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


