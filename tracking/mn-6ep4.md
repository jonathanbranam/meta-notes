+++
id = "mn-6ep4"
title = "time-block skill and conventions use 'bridle' as an example project name"
kind = "fix"
state = "integrated"
created_at = "2026-11-05T14:04:30.177Z"
updated_at = "2026-11-17T12:20:23.883522443Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
commit = "a8c8333"
summary = "'website' replaces 'bridle' as the example project name in skills/time-block/SKILL.md and conventions.md (v3.1.1). a8c8333."
ticket = "6ep4"
+++

## The ask

Found by the mn-h7fb worker (via manager, m-0172, 2026-11-05): the time-block skill and the conventions name 'bridle' as an example of a lowercase project name. Rule works-without-bridle says the product never mentions bridle. Swap the example for a neutral project name. Filed by orchestrator@vesta.

## Brief (orchestrator@vesta, acting PM, 2026-11-17)

Change "(bridle, meta-notes)" to a neutral example such as "(kitchen, meta-notes)" in:
- skills/time-block/SKILL.md:39
- scripts/meta_notes/conventions.md:151 (keep the paragraph's line wrapping tidy)

If the prime guide's output or a test snapshot embeds conventions.md, update it to match. Also check scripts/meta_notes/__init__.py, which mentions bridle: change it only if it is user-facing text (help, output, docs); leave it if it is a code comment about the dev workflow, and say which in your report.

Files: skills/time-block/SKILL.md, scripts/meta_notes/conventions.md, possibly scripts/meta_notes/__init__.py and a test fixture.

Verify: `grep -rn bridle skills scripts/meta_notes/conventions.md` prints nothing; the project's check is green.

Model: Haiku.

Out of scope: bridle mentions in docs/, design/ and .bridle/ (dev workflow, not product).

## Thread

### note · external:aide · 2026-11-17T12:02:03.176Z
readied by external:aide

### note · external:aide · 2026-11-17T12:02:03.411Z
Readied by aide under rule ready-without-asking (kind chore/fix/bug, ask is self-evident); it had been pending since it was filed as not scheduled.

### note · agent:manager · 2026-11-17T12:03:07.587Z
Manager: open, not planned, not in bridle queue. Please plan and queue it; I will spawn a worker once startable.

### note · external:orchestrator · 2026-11-17T12:13:21.916Z
Planned and queued by orchestrator@vesta (acting PM); the brief is in the ticket body.

### note · external:orchestrator · 2026-11-17T12:16:26.426Z
Verified by orchestrator@vesta: a8c8333 (v3.1.1); 'website' replaces 'bridle' in the skill and conventions; no bridle left in skills/ or conventions.md.

### note · external:orchestrator · 2026-11-17T12:20:18.613Z
integrated: a8c8333
