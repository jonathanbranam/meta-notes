"""
Tag parsing shared by tasks and time logs.

A tag is # followed by letters, digits, _, or -. Known abbreviations map to
a canonical name (#mtg is #meeting). Tags are compared ignoring case.
"""

import re

# Tag aliases: abbreviations expanded to their canonical (full) tag text.
# Keys are lowercase. Note: #off-task is NOT aliased to #personal because it
# has different boundary semantics in time tracking (non-work time within the
# work window, not a boundary marker).
TAG_ALIASES: dict[str, str] = {
    '#mtg': '#meeting',
    '#pers': '#personal',
    '#per': '#personal',
    '#waiting': '#wait',
}

TAG_PATTERN = re.compile(r'#([\w-]+)')


def canonical_tag(name: str) -> str:
    """
    Return the canonical name of a tag, without the leading #.

    Args:
        name: Tag name, with or without #.

    Returns:
        The alias target when the name is a known alias (ignoring case),
        otherwise the name as given.
    """
    bare = name[1:] if name.startswith('#') else name
    alias = TAG_ALIASES.get('#' + bare.lower())
    return alias[1:] if alias else bare


def parse_tags(text: str) -> list[str]:
    """
    Extract the tags in text.

    Args:
        text: Text to search.

    Returns:
        Canonical tag names without #, in order of appearance, with
        duplicates (ignoring case) removed.
    """
    tags: list[str] = []
    seen: set[str] = set()
    for match in TAG_PATTERN.findall(text):
        tag = canonical_tag(match)
        if tag.lower() not in seen:
            seen.add(tag.lower())
            tags.append(tag)
    return tags
