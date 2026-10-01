+++
id = "mn-23fd"
title = "Done is written as lowercase x, an existing X is kept (ticket done-status-lowercase-x-keeps-case-ngp4)"
kind = "bug"
state = "planned"
created_at = "2026-10-01T23:47:42.462Z"
updated_at = "2026-10-01T23:47:43.374504006Z"
+++

See docs/tickets/open/done-status-lowercase-x-keeps-case-ngp4.md. task update --status X writes x; --status x/X on an X task leaves it X. PATCH bump. git mv the ticket to resolved/ when done.
