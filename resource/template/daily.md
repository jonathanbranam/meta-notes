---
filename_pattern: "resource/daily-notes/{{date:%y}}-{{date:Q{{((date.month-1)//3)+1}}}}/{{date:%Y-%m-%d %a}}.md"
---

# Daily Note - {{date:%A, %B %d, %Y}}

Week Plan: [[resource/plan/week/Plan {{week_start}}]]

## Tasks Due Today
{{% python scripts/find_tasks.py --due-on {{date}} --status incomplete %}}

## Overdue Tasks
{{% python scripts/find_tasks.py --due-by {{date-1}} --status incomplete %}}

## Notes

## Time Tracking

### Log

- activity name #tag-1 #tag-2
  * start: {{date:%Y-%m-%d %a}} 08:00
  * end:   {{date:%Y-%m-%d %a}} 09:00

### Time Block

| Time    | Plan                                 | Actual                      |
| ------- | ------------------------------------ | --------------------------- |
|  8:00am |                                      |                             |
|  8:15am |                                      |                             |
|  8:30am |                                      |                             |
|  8:45am |                                      |                             |
|  9:00am |                                      |                             |
|  9:15am |                                      |                             |
|  9:30am |                                      |                             |
|  9:45am |                                      |                             |
| 10:00am |                                      |                             |
| 10:15am |                                      |                             |
| 10:30am |                                      |                             |
| 10:45am |                                      |                             |
| 11:00am |                                      |                             |
| 11:15am |                                      |                             |
| 11:30am |                                      |                             |
| 11:45am |                                      |                             |
| 12:00pm |                                      |                             |
| 12:15pm |                                      |                             |
| 12:30pm |                                      |                             |
| 12:45pm |                                      |                             |
|  1:00pm |                                      |                             |
|  1:15pm |                                      |                             |
|  1:30pm |                                      |                             |
|  1:45pm |                                      |                             |
|  2:00pm |                                      |                             |
|  2:15pm |                                      |                             |
|  2:30pm |                                      |                             |
|  2:45pm |                                      |                             |
|  3:00pm |                                      |                             |
|  3:15pm |                                      |                             |
|  3:30pm |                                      |                             |
|  3:45pm |                                      |                             |
|  4:00pm |                                      |                             |
|  4:15pm |                                      |                             |
|  4:30pm |                                      |                             |
|  4:45pm |                                      |                             |
|  5:00pm |                                      |                             |
|  5:15pm |                                      |                             |
|  5:30pm |                                      |                             |
|  5:45pm |                                      |                             |
|  6:00pm |                                      |                             |
