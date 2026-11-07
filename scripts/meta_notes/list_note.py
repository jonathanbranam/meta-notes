"""
List notes: read and edit a shopping (or any) list kept as a note.

A list is `resource/lists/<YY-Qn>/<YYYY-MM-DD> <name>.md`: a `# ` title, then
ordered groups (`## ` headings) holding ordered items. Items before the first
group belong to no group (a flat list). An item is a plain checkbox line
(`- [ ]` open, `- [x]` done, `- [-]` canceled) with no date emoji, so it is a
checklist item and never a task. Indented bullets under an item hold its
source task (`* source:`) and, once the list closed that task, the closed
line (`* closed:`); other lines under an item are kept as they are.

Edits work on the parsed ListNote and write the whole file back in the
canonical layout: blank lines between groups, none between items.
"""

import os
import re
from dataclasses import dataclass, field
from datetime import date

import tasks
from meta_notes import task_update, template

LISTS_DIR = 'resource/lists'
STATES = {' ': 'open', 'x': 'done', '-': 'canceled'}
CHAR_OF = {'open': ' ', 'done': 'x', 'canceled': '-'}

_ITEM = re.compile(r'^- \[([ xX-])\] (.*\S)\s*$')
_GROUP = re.compile(r'^## (.*\S)\s*$')
_SOURCE = re.compile(r'^  \* source: \[\[(.+?)\]\] line (\d+): (.*\S)\s*$')
_CLOSED = re.compile(r'^  \* closed: line (\d+): (.*\S)\s*$')
_NAME_FILE = re.compile(r'^(\d{4}-\d{2}-\d{2}) (.+)\.md$')
# Markers that would make an item line a task or carry task state
_TASK_MARKERS = (task_update.START_EMOJI, task_update.COMPLETED_EMOJI,
                 task_update.RECUR_EMOJI, task_update.TIME_EMOJI,
                 *tasks.DUE_EMOJIS)


class ListError(Exception):
    """A list command failed; nothing was written."""


@dataclass
class Item:
    state: str  # open, done or canceled
    text: str
    source: dict | None = None  # file (a note link), line, text
    closed: dict | None = None  # line, text: the task as the list closed it
    extra: list[str] = field(default_factory=list)


@dataclass
class Group:
    name: str | None  # None: items before the first heading
    items: list[Item] = field(default_factory=list)
    lead: list[str] = field(default_factory=list)


@dataclass
class ListNote:
    path: str
    head: list[str]
    groups: list[Group]  # groups[0] is always the unnamed one

    def items(self) -> list[tuple[Group, Item]]:
        return [(g, i) for g in self.groups for i in g.items]


def _bad_item_text(text: str) -> str | None:
    text = text.strip()
    if not text or re.search(r'[\r\n]', text):
        return 'The item text must be one non-empty line'
    if any(m in text for m in _TASK_MARKERS):
        return ('The item text has a date, time, recurrence or completion '
                'emoji, which would make it a task')
    return None


def check_item_text(text: str) -> str:
    """The trimmed text of a new or edited item, or ListError."""
    if (message := _bad_item_text(text)) is not None:
        raise ListError(message)
    return text.strip()


def _check_group_name(name: str) -> str:
    name = name.strip()
    if not name or re.search(r'[\r\n]', name):
        raise ListError('The group name must be one non-empty line')
    return name


# Paths

def list_path(day: date, name: str) -> str:
    name = name.strip()
    if not name or re.search(r'[\r\n/\\]', name) or name in ('.', '..'):
        raise ListError('The list name must be one non-empty line with no '
                        'slash')
    return (f'{LISTS_DIR}/{day:%y}-{template.quarter(day)}/'
            f'{day.isoformat()} {name}.md')


def split_path(path: str) -> tuple[str, str]:
    """(date, name) from a list path; ('', basename) if it doesn't fit."""
    base = os.path.basename(path)
    m = _NAME_FILE.match(base)
    return (m.group(1), m.group(2)) if m else ('', base.removesuffix('.md'))


def all_lists() -> list[str]:
    """Every list path, oldest first."""
    found = []
    for folder, _, files in os.walk(LISTS_DIR):
        found += [os.path.join(folder, f) for f in files
                  if f.endswith('.md')]
    return sorted(found, key=lambda p: (split_path(p)[0], p))


def resolve(ref: str) -> str:
    """
    The path a LIST argument means: a path to a list note (with or without
    `.md`), or a name such as `Walmart` (the newest list with that name,
    or with that `<date> <name>`).
    """
    if '/' in ref:
        path = ref if ref.endswith('.md') else ref + '.md'
        if not os.path.isfile(path):
            raise ListError(f'No such list: {path}')
        return path
    want = ref.removesuffix('.md').strip().lower()
    hits = [p for p in all_lists()
            if want in (split_path(p)[1].lower(),
                        os.path.basename(p)[:-3].lower())]
    if not hits:
        raise ListError(f'No list named {ref!r} (see meta-notes list ls)')
    return hits[-1]


# Reading and writing

def parse(path: str, lines: list[str]) -> ListNote:
    head: list[str] = []
    groups = [Group(None)]
    for line in lines:
        line = line.rstrip()
        if m := _GROUP.match(line):
            groups.append(Group(m.group(1)))
        elif not line:
            continue
        elif m := _ITEM.match(line):
            groups[-1].items.append(Item(STATES[m.group(1).lower()],
                                         m.group(2)))
        elif groups[-1].items:
            item = groups[-1].items[-1]
            if m := _SOURCE.match(line):
                item.source = {'file': m.group(1), 'line': int(m.group(2)),
                               'text': m.group(3)}
            elif m := _CLOSED.match(line):
                item.closed = {'line': int(m.group(1)), 'text': m.group(2)}
            else:
                item.extra.append(line)
        elif groups[-1].name is None:
            head.append(line)
        else:
            groups[-1].lead.append(line)
    return ListNote(path, head, groups)


def render(note: ListNote) -> str:
    out = list(note.head)

    def block(lines: list[str]):
        if out and lines:
            out.append('')
        out.extend(lines)

    for group in note.groups:
        lines = [] if group.name is None else [f'## {group.name}']
        lines += group.lead
        for item in group.items:
            lines.append(f'- [{CHAR_OF[item.state]}] {item.text}')
            if item.source:
                s = item.source
                lines.append(f"  * source: [[{s['file']}]] line {s['line']}: "
                             f"{s['text']}")
            if item.closed:
                lines.append(f"  * closed: line {item.closed['line']}: "
                             f"{item.closed['text']}")
            lines += item.extra
        block(lines)
    return '\n'.join(out) + '\n'


def load(path: str) -> ListNote:
    try:
        with open(path, encoding='utf-8') as f:
            return parse(path, f.read().split('\n'))
    except FileNotFoundError:
        raise ListError(f'No such list: {path}')
    except (OSError, UnicodeDecodeError) as e:
        raise ListError(f'Could not read {path}: {e}')


def save(note: ListNote) -> None:
    tmp = note.path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(render(note))
    os.replace(tmp, note.path)


def create(day: date, name: str) -> str:
    """Make an empty list; returns its path."""
    path = list_path(day, name)
    if os.path.lexists(path):
        raise ListError(f'The list already exists: {path}')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    title = f'# {day.isoformat()} {name.strip()}'
    with open(path, 'x', encoding='utf-8') as f:
        f.write(title + '\n')
    return path


# Edits

def _group(note: ListNote, name: str) -> Group:
    for g in note.groups:
        if g.name is not None and g.name == name.strip():
            return g
    names = ', '.join(g.name for g in note.groups if g.name) or 'none'
    raise ListError(f'No group {name!r} in {note.path} (groups: {names})')


def _insert(seq: list, value, position: int | None) -> None:
    """Insert at a 1-based position; None or past the end appends."""
    if position is not None and position < 1:
        raise ListError('Positions count from 1')
    if position is None or position > len(seq):
        seq.append(value)
    else:
        seq.insert(position - 1, value)


def group_add(note: ListNote, name: str, position: int | None = None):
    name = _check_group_name(name)
    if any(g.name == name for g in note.groups):
        raise ListError(f'The group already exists: {name}')
    named = [g for g in note.groups if g.name is not None]
    _insert(named, Group(name), position)
    note.groups = [note.groups[0]] + named


def group_rename(note: ListNote, old: str, new: str):
    new = _check_group_name(new)
    group = _group(note, old)
    if new != group.name and any(g.name == new for g in note.groups):
        raise ListError(f'The group already exists: {new}')
    group.name = new


def group_move(note: ListNote, name: str, position: int):
    group = _group(note, name)
    named = [g for g in note.groups if g.name is not None and g is not group]
    _insert(named, group, position)
    note.groups = [note.groups[0]] + named


def item_at(note: ListNote, number: int,
            expect: str | None = None) -> tuple[Group, Item]:
    """The item numbered as `show` numbers them (from 1, file order)."""
    items = note.items()
    if not 1 <= number <= len(items):
        raise ListError(f'No item {number}: {note.path} has {len(items)}')
    group, item = items[number - 1]
    if expect is not None and item.text != expect.strip():
        raise ListError(f'Item {number} has changed; it is now: {item.text}')
    return group, item


def item_add(note: ListNote, text: str, group: str | None = None,
             position: int | None = None, source: dict | None = None) -> Item:
    item = Item('open', check_item_text(text), source=source)
    target = _group(note, group) if group else note.groups[0]
    _insert(target.items, item, position)
    return item


def item_edit(note: ListNote, number: int, text: str,
              expect: str | None = None) -> Item:
    _, item = item_at(note, number, expect)
    item.text = check_item_text(text)
    return item


def item_move(note: ListNote, number: int, group: str | None,
              position: int | None, expect: str | None = None) -> Item:
    src, item = item_at(note, number, expect)
    dest = _group(note, group) if group else src
    src.items.remove(item)
    _insert(dest.items, item, position)
    return item


def set_state(note: ListNote, number: int, state: str,
              expect: str | None = None) -> Item:
    _, item = item_at(note, number, expect)
    item.state = state
    return item


# Reading out

def _source_data(item: Item) -> dict | None:
    return item.source and dict(item.source)


def to_json(note: ListNote) -> dict:
    day, name = split_path(note.path)
    groups, number = [], 0
    for g in note.groups:
        if g.name is None and not g.items:
            continue
        items = []
        for item in g.items:
            number += 1
            items.append({'number': number, 'text': item.text,
                          'state': item.state,
                          'source': _source_data(item),
                          'closed_task': item.closed and dict(item.closed)})
        groups.append({'name': g.name, 'items': items})
    return {'list': note.path, 'date': day, 'name': name, 'groups': groups}


def to_text(note: ListNote) -> list[str]:
    day, name = split_path(note.path)
    out = [f'{note.path}']
    number = 0
    for g in note.groups:
        if g.name is None and not g.items:
            continue
        if g.name is not None:
            out.append(g.name)
        for item in g.items:
            number += 1
            box = CHAR_OF[item.state]
            line = f'  {number}. [{box}] {item.text}'
            if item.source:
                line += f"  (task {item.source['file']}:{item.source['line']})"
            out.append(line)
    if number == 0:
        out.append('(empty)')
    return out
