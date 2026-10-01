+++
id = "mn-23fd"
title = "Done is written as lowercase x, an existing X is kept (ticket done-status-lowercase-x-keeps-case-ngp4)"
kind = "bug"
state = "integrated"
created_at = "2026-10-01T23:47:42.462Z"
updated_at = "2026-10-01T23:52:10.700231912Z"
commit = "ee6f6d5"
+++

See docs/tickets/open/done-status-lowercase-x-keeps-case-ngp4.md. task update --status X writes x; --status x/X on an X task leaves it X. PATCH bump. git mv the ticket to resolved/ when done.

## Thread

### note · agent:manager · 2026-10-01T23:52:10.700Z
integrated: ee6f6d5
