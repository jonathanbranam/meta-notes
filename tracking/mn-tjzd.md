+++
id = "mn-tjzd"
title = "Opt-in migrations are pending in this project"
kind = "chore"
state = "integrated"
created_at = "2026-11-14T12:05:23.405Z"
updated_at = "2026-11-22T01:00:11.944884782Z"
created_by = "human"
watchers = ["human"]
commit = "adf2232"
+++

These migrations are opt-in: bridle does not run them at start-up, because they rewrite this project's files and want a review first. Decide whether this project needs each one, and if so run it on the trial or integration branch and commit the result:

- 0002-standard-ticket-fields: Rename ticket frontmatter fields to the standard names and qualify ticket ids with the project prefix (ticket syqn).
- 0004-ticket-links-in-frontmatter: Carry the daemon's blocks, parent and related edges between tickets into their frontmatter and drop the `tasks:` list (ticket 3v75).
- 0005-a-ticket-for-every-active-task: Give every active task without a ticket a stub ticket, and every extra task of a ticket a child ticket, so each piece of work has one (ticket 72t9).

Run one with `bridle migrate --only <id>` (add --dry-run to see what it would change).

## Thread

### note · human · 2026-11-14T12:05:23.791Z
Opt-in migrations are pending in this project

These migrations are opt-in: bridle does not run them at start-up, because they rewrite this project's files and want a review first. Decide whether this project needs each one, and if so run it on the trial or integration branch and commit the result:

- 0002-standard-ticket-fields: Rename ticket frontmatter fields to the standard names and qualify ticket ids with the project prefix (ticket syqn).
- 0004-ticket-links-in-frontmatter: Carry the daemon's blocks, parent and related edges between tickets into their frontmatter and drop the `tasks:` list (ticket 3v75).
- 0005-a-ticket-for-every-active-task: Give every active task without a ticket a stub ticket, and every extra task of a ticket a child ticket, so each piece of work has one (ticket 72t9).

Run one with `bridle migrate --only <id>` (add --dry-run to see what it would change).

### note · external:aide · 2026-11-22T01:00:11.631Z
The human, via aide (2026-11-21): "Run the migration you suggest". Ran 0002-standard-ticket-fields (68 tickets, 82eb8cf) and 0004-ticket-links-in-frontmatter (56 tickets, adf2232) on main; skipped 0005 (it would only stub a ticket for mn-tjzd itself). Unit tests green.

### note · external:aide · 2026-11-22T01:00:11.944Z
integrated: adf2232
