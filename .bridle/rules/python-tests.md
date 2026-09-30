---
id: python-tests
severity: must
roles: [manager, worker]
---
Python is tested with pytest in `test/unit/`, one file per module, run with
`uv run pytest test/unit/` (or `uv run pytest test/unit/test_<x>.py`).

- Bare test functions, no test classes.
- Name them `test_<module>_<function>_<scenario>`, e.g.
  `test_find_tasks_in_file_with_start_date`.
- Group related tests under a comment header (`# Tests for find_tasks_in_file`).
- Use the `tmp_path` fixture for any files; never touch the repo or a real
  notes root.

Why: the name alone says what broke, and flat functions keep 1,000+ tests
easy to grep and run one at a time.
