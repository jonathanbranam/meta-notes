"""
Notes root configuration, read from the .meta-notes sentinel as TOML.

Settings are grouped in tables named for the command that uses them, such as
[calendar]. Unknown tables and keys are ignored. Only commands that use
settings call load(), so a TOML error can't break unrelated commands.
"""

import os
import tomllib

from meta_notes.root import SENTINEL


def load(root: str) -> dict:
    """
    Read the notes root's config.

    Args:
        root: The notes root directory.

    Returns:
        The parsed TOML; {} for a sentinel with only comments or blank lines.

    Raises:
        ValueError: If .meta-notes is not valid TOML or can't be read; the
            message names .meta-notes and, for a parse error, its line.
    """
    path = os.path.join(root, SENTINEL)
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        # tomllib's message ends with "(at line N, column M)"
        raise ValueError(f"{SENTINEL} is not valid TOML: {e}") from None
    except OSError as e:
        raise ValueError(f"Cannot read {SENTINEL}: {e.strerror or e}") from None


def table(config: dict, name: str) -> dict:
    """A table from the config, or {} when it's missing or not a table."""
    value = config.get(name)
    return value if isinstance(value, dict) else {}
