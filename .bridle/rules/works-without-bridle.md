---
id: works-without-bridle
severity: must
roles: [manager, worker]
---
The human uses meta-notes at work, where they can't and won't run bridle,
but do run Claude Code agents and skills. So the product (the Vim plugin,
`bin/meta-notes`, `skills/`, `templates/`, and what `meta-notes init`
installs) never needs bridle: no `bridle` commands, no `.bridle/` files, no
bridle daemon, rules or roles. Skills and the CLI work with only the
meta-notes checkout, Python and Claude Code.

Bridle is how this repo is developed, not part of what it ships.

Why: the human, 2026-10-04: "i cannot and will not run bridle at work, but
i will run agents and skills there."
