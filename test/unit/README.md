# Unit Tests for Python Scripts

This directory contains unit tests for Python scripts in the `scripts/` folder.

## Setup

Install pytest (if not already installed):

```bash
pip install pytest
```

Or using pip3:

```bash
pip3 install pytest
```

## Running Tests

From the project root directory:

```bash
# Run all unit tests
pytest test/unit/

# Run with verbose output
pytest -v test/unit/

# Run specific test file
pytest test/unit/test_find_tasks.py

# Run specific test class
pytest test/unit/test_find_tasks.py::TestFindTasksInFile

# Run specific test method
pytest test/unit/test_find_tasks.py::TestFindTasksInFile::test_find_simple_uncompleted_task

# Run with coverage report
pytest --cov=scripts test/unit/

# Run with output showing print statements
pytest -s test/unit/
```

## Test Structure

Tests follow pytest conventions:
- Test files are named `test_*.py`
- Test classes are named `Test*`
- Test functions are named `test_*`
- Fixtures use pytest's built-in fixtures like `tmp_path`, `capsys`, etc.

## Writing New Tests

When adding new Python scripts to the `scripts/` folder:

1. Create a corresponding test file: `test/unit/test_<script_name>.py`
2. Import the script module (add scripts dir to path if needed)
3. Write test classes for each function/class in the script
4. Use pytest fixtures for file system operations and output capture
5. Run tests to verify functionality

Example:

```python
import sys
from pathlib import Path

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

import your_script

def test_your_function(tmp_path):
    # Test code here
    assert your_script.your_function() == expected_value
```
