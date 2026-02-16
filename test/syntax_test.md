# Syntax Highlighting Test

This file demonstrates the syntax highlighting for time tracking features.

## Time Log

### Log

- arrived:
  * end:   2026-02-15 Sun 08:00
- check #email
  * start: 2026-02-15 Sun 08:00
  * end:   2026-02-15 Sun 08:45
- #standup #mtg
  * start: 2026-02-15 Sun 08:45
  * end:   2026-02-15 Sun 09:12
- coding on #feat #dev
  * start: 2026-02-15 Sun 09:12
  * end:   2026-02-15 Sun 10:06
- lunch #break
  * start: 2026-02-15 Sun 10:06
  * end:   2026-02-15 Sun 10:44

## Time Block

| Time    | Plan                                 | Actual                      |
| ------- | ------------------------------------ | --------------------------- |
|  8:00am | email #admin                         | arrived: 8:05 am            |
|  8:15am | email #admin                         | email #admin                |
|  8:30am | standup #mtg                         | ~~off-plan: incident~~ #dev |
|  8:45am | coding #dev                          | coding #dev                 |
|  9:00am | coding #dev                          | coding #dev                 |
|  9:15am | [break]                              | [break]                     |
|  9:30am | code review #dev                     | code review #dev            |

## Special Tags

Different tag types should have different colors:

- Meeting tags: #mtg #meeting
- Development tags: #dev #code #coding
- Personal tags: #pers #personal
- Admin tags: #admin #administrative
- Break tags: #break
- Activity tags: #project-alpha #sprint-2 #urgent

## Special Entries

- Normal text with [break] entry
- Off-plan entry: ~~this was not planned~~
- Time stamps: 8:00 am, 2:30 pm, 12:00 pm
- Arrived: - arrived: 8:05 am
