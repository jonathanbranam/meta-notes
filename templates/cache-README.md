# meta-notes cache

Created by `meta-notes init`. Not committed (see .gitignore).

- `ics/` - Google Calendar exports (.zip or .ics). Save new exports here;
  `meta-notes calendar` reads the newest and keeps the latest 5.
- `calendar/` - parsed calendars built from the exports. Safe to delete;
  `meta-notes cache clear` empties it.
