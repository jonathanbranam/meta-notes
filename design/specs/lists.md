# lists Specification

## Purpose
Specifies list notes (a shopping list, a packing list) and the `meta-notes list` commands that make and run them, so an agent can build a list from the user's tasks and a UI can show and check it, both through the same commands. A list item is a checklist item, never a task.

## Requirements

### Requirement: List note format  {#r-8128}
A list SHALL be one note at `resource/lists/<YY-Qn>/<YYYY-MM-DD> <name>.md`, the quarter folder named as daily notes are. It SHALL start with a `# <YYYY-MM-DD> <name>` title, then hold ordered groups, each a `## <group name>` heading (a store section, for example) followed by ordered items. Items before the first heading SHALL belong to no group, so a list with no headings is a flat list. File order SHALL be display order. An item SHALL be a plain checkbox line, `- [ ]` open, `- [x]` done or `- [-]` canceled, with brief text and no date, time, recurrence or completion emoji, so it is never a task. A guessed or unclear item SHOULD end its text with `?`. Other lines in the file SHALL be kept when a command rewrites it.

#### Scenario: A list is never a task  {#s-613c}
*Verification*: **non-executable**
- **WHEN** a list holds open, done and canceled items
- **THEN** `meta-notes tasks --status all --all` SHALL list none of them

#### Scenario: A list written by hand  {#s-2f5c}
*Verification*: **non-executable**
- **WHEN** a user edits a list in an editor, adding a group and reordering items
- **THEN** `meta-notes list show` SHALL show the groups and items in file order

### Requirement: Make and read lists  {#r-5ec2}
`meta-notes list new <name> [--date DAY]` SHALL create an empty list dated today (or DAY) and print its path; it SHALL fail, writing nothing, when the list exists or the name is empty or has a slash. `meta-notes list ls` SHALL list every list, oldest first, with its item and open-item counts (`lists` with `--json`). `meta-notes list show <list>` SHALL print the groups and the items numbered from 1 in file order, with each item's state and source; with `--json` it SHALL return `list`, `date`, `name` and `groups`, each with `name` (null for items before the first heading) and `items` (`number`, `text`, `state` of `open`, `done` or `canceled`, `source` and `closed_task`, each null when absent). A `<list>` argument SHALL be a path to a list note, or a name, meaning the newest list with that name.

#### Scenario: Show a list  {#s-3e14}
*Verification*: **non-executable**
- **WHEN** a list has the group `Produce` holding `milk?` and the user runs `meta-notes list show Walmart --json`
- **THEN** the output SHALL have the group `Produce` with the item numbered 1, state `open`, text `milk?`

#### Scenario: Unknown list  {#s-f461}
*Verification*: **non-executable**
- **WHEN** no list is named `Costco`
- **THEN** `meta-notes list show Costco` SHALL fail naming `meta-notes list ls`

### Requirement: Groups  {#r-b186}
`meta-notes list group-add <list> <name> [--position N]` SHALL add a group (last by default), `group-rename <list> <old> <new>` SHALL rename one, and `group-move <list> <name> <position>` SHALL move one among the groups; positions count from 1. A command naming a missing group, or making a duplicate, SHALL fail and write nothing. Items stay with their group.

#### Scenario: Reorder groups  {#s-dca9}
*Verification*: **non-executable**
- **WHEN** a list has `Produce` then `Dairy` and the user runs `group-move <list> Dairy 1`
- **THEN** the file SHALL have `Dairy` before `Produce`, each with its items

### Requirement: Items  {#r-d08f}
`meta-notes list item-add <list> <text> [--group NAME] [--position N]` SHALL add an open item to the group (default: the items before the first heading), at the position (default: last). `item-edit <list> <n> --text TEXT` SHALL change an item's text; `item-move <list> <n> [--group NAME] [--position N]` SHALL move an item within or between groups. Items SHALL be addressed by their number in `list show`. Each item command SHALL accept `--expect TEXT` and, when given, fail without writing if the item's text differs. Text with a date, time, recurrence or completion emoji, or over more than one line, SHALL be refused: no command SHALL write such an emoji on an item line. Every command SHALL print the list as `list show` does.

#### Scenario: Reject a task-like item  {#s-64a8}
*Verification*: **non-executable**
- **WHEN** the user runs `item-add <list> 'soup 📅 2026-11-08'`
- **THEN** the command SHALL fail and write nothing

#### Scenario: Stale item number  {#s-806b}
*Verification*: **non-executable**
- **WHEN** item 2 is `milk?` and the user runs `item-edit <list> 2 --expect 'eggs' --text 'eggs x2'`
- **THEN** the command SHALL fail naming the item's current text and write nothing

#### Scenario: Order round-trips  {#s-a254}
*Verification*: **non-executable**
- **WHEN** items are added, moved between groups and reordered
- **THEN** the file SHALL hold them in the order `list show` numbers them

### Requirement: Check, uncheck and cancel  {#r-2914}
`meta-notes list check <list> <n>` SHALL mark an item done, `uncheck` SHALL reopen it and `cancel` SHALL mark it canceled, each accepting `--expect TEXT` as the item commands do. Setting an item to the state it has SHALL change nothing.

#### Scenario: Check an item  {#s-c817}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes list check Walmart 1`
- **THEN** item 1 SHALL be `- [x]` and no other line SHALL change
