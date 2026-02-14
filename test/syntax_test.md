# Syntax Highlighting Test

This file demonstrates the syntax highlighting for time tracking features.

## Time Log

### Log

- arrived: 8:00 am
- email review (#admin, #communication) 8:15 am - 8:45 am
- standup meeting (#mtg, #team) 9:00 am - 9:30 am
- coding session (#dev, #project-alpha) 9:30 am - 11:00 am
- [lunch break] 12:00 pm - 1:00 pm
- ~~off-plan: emergency meeting~~ (#mtg) 1:00 pm - 2:00 pm
- personal time (#pers) 5:00 pm - 6:00 pm

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
