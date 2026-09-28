---
id: languages
severity: must
roles: [manager, worker]
---
Vimscript first; Python for larger work. Python is standard library only.

- Plugin logic is Vimscript (`plugin/`, `autoload/meta_notes/`,
  `after/syntax/`), so it runs in any Vim or Neovim with nothing to install.
  Work too big or awkward for Vimscript goes in Python, run by the shell
  (`bin/meta-notes` runs `scripts/meta_notes/`; older helpers are
  `scripts/*.py`).
- Python must run on **3.11 or newer**, using only the standard library. The
  3.11 floor is what users are promised; development runs on 3.14 through
  pipenv (`Pipfile`), so don't use anything newer than 3.11 without saying
  so in your report.
- The exception is a command whose spec needs a third-party library. Pin it
  in `requirements.txt`, and import it lazily, inside that command only. It's
  installed only into the notes root's `.venv` (by `meta-notes init`), never
  globally, so every other command must keep working without it.

Why: most users only have the system Python. An import that isn't lazy
would break every command for a notes root without that `.venv`, not just
the one command that needs the library.
