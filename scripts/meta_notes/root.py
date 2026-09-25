"""
Find a notes root by its sentinel file.

A notes root is a directory containing SENTINEL, which `meta-notes init`
creates. The upward search is bounded: it checks each directory only for the
sentinel (never listing contents), stops after $HOME, and stops quietly at the
first directory the user can't read, write, and search, since a notes root
needs all three.
"""

import os

SENTINEL = ".meta-notes"


def find_root(start: str, home: str | None) -> str | None:
    """
    Search upward from start for the nearest directory containing SENTINEL.

    Args:
        start: Directory to start from; it is checked first.
        home: $HOME; the search stops after checking it. None for no bound.

    Returns:
        Absolute real path of the notes root, or None if the search stopped
        without finding one.
    """
    path = os.path.realpath(start)
    home = os.path.realpath(home) if home else None
    while True:
        if not os.access(path, os.R_OK | os.W_OK | os.X_OK):
            return None
        try:
            if os.path.isfile(os.path.join(path, SENTINEL)):
                return path
        except OSError:
            return None
        if path == home:
            return None
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent
