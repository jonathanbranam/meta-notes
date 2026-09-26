# Tasks

## 1. Record entries without activity text

- [x] 1.1 In `scripts/time_tracking.py` `_create_time_log_entry`, keep an entry when it has activity text, tags, or a start/end time; drop only a bare bullet with none. Verify with new tests in `test/unit/test_time_tracking.py` for the tag-only, empty-with-times, and stray-bullet scenarios of the `time-log` delta.
- [x] 1.2 Verify with a test that a tag-only entry's `activity` is `''` and its 60 min appear in `calculate_total_time_by_tag` under `#proj-01` and, with a work tag such as `#code`, in work vs. non-work. Run `pipenv run pytest test/unit/test_time_tracking.py`.

## 2. Day report

- [x] 2.1 Add a test in `test/unit/test_time_report.py` for the "Tag-only entry" scenario of the `time-report` delta: `- #proj-01 #research` listed with `time: 1 hr 0 min` and `tags: proj-01 research`, no `*GAP`, `total duration` 2 hr 0 min, no `*missing time*`. It passes with no change to `scripts/time_report.py`.

## 3. Integration

- [ ] 3.1 Run `pipenv run pytest test/unit/` and `./run_tests.sh --quiet`; both pass.
- [x] 3.2 In a scratch notes root, log `- #proj-01 #research` between two titled entries and run `meta-notes time --date <day>`; confirm the listing and totals match the spec.
