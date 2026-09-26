"""
Entry point for the meta-notes CLI.

Run as `python3 scripts/meta_notes/__main__.py` (what bin/meta-notes does) or
`python3 -m meta_notes` with scripts/ on sys.path. This file must stay
parseable by old Pythons so the version check below can report clearly.
"""

import os
import sys

MIN_VERSION = (3, 11)

if sys.version_info < MIN_VERSION:
    message = "meta-notes requires Python %d.%d or newer (found %d.%d)" % (
        MIN_VERSION + tuple(sys.version_info[:2]))
    if "--json" in sys.argv[1:]:
        import json
        print(json.dumps({"ok": False, "error": message, "warnings": []}))
    else:
        sys.stderr.write("Error: " + message + "\n")
    sys.exit(1)

# Put scripts/ first on sys.path (replacing this file's directory, or the
# current directory under -m) so a notes root can't shadow our modules and
# the flat imports (`import find_tasks`) work.
_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys.path and os.path.abspath(sys.path[0] or ".") in (
        os.path.dirname(os.path.abspath(__file__)), os.getcwd()):
    sys.path[0] = _scripts_dir
else:
    sys.path.insert(0, _scripts_dir)

from meta_notes import cli  # noqa: E402

if __name__ == "__main__":
    sys.exit(cli.main())
