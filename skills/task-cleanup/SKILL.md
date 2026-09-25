---
name: task-cleanup
description: Work through stale, overdue, and undated tasks across a meta-notes notes root in short batches, 5–10 minutes by default. Use when the user asks to clean up stale tasks, triage old or overdue tasks, work the task backlog, or says "task cleanup". The only skill that walks old tasks; it doesn't review projects (project-review) or plan a day (daily-plan).
---

# Task Cleanup

Work down the backlog of old tasks, oldest first, in batches that fit the
time the user has. Stopping at any point is safe.

## Time budget

Ask how much time the user has; default to 5–10 minutes. Say the budget
in one line. Plan on about one minute per 3–5 tasks.

## Start

1. Run `command -v meta-notes`. If it prints nothing, stop and tell the
   user: "`meta-notes` isn't on your PATH. Link the plugin's
   `bin/meta-notes` into a directory on your PATH, for example
   `ln -s <plugin>/bin/meta-notes ~/bin/meta-notes`." Don't read or edit
   any note.
2. Run `meta-notes conventions` and follow it for everything below.

## Hard rules

- Every change is a `meta-notes task update` call with `file`, `line`,
  and `text` from the query that listed the task. Never rewrite a task
  line by hand.
- If `task update` says the line changed, re-run the query and retry
  with the current text, or skip the task. Never guess.
- Don't use git history, `git blame`, or file modification times. Age
  is the task's due date, or the dates in its note.
- If the user says stop, go to "Stopping early".

## Steps

### 1. Query

- Overdue: `meta-notes tasks --overdue --json`. Sort by `due`, oldest
  first.
- Undated: `meta-notes tasks --undated --json`. Group by `file`.

Work overdue tasks first, then undated ones note by note.

### 2. Batches

Show a batch sized to the time left (5–10 tasks), one line each: its
due date (or "undated"), text, and note. Number them.

For each task, the user chooses:

| Choice | Command options |
|---|---|
| keep | none |
| date it | `--due <YYYY-MM-DD>` |
| later | `--add-tag later` |
| cancel | `--status -` |
| done | `--status x` |

Accept answers in short form ("1 done, 2 later, 3–5 cancel"). For the
whole batch, also offer **cancel all** and **later all**. Apply each as
one call per line:

```sh
meta-notes task update '<file>:<line>' --expect '<text>' --add-tag later
```

Line numbers from one query stay valid across these updates, so a whole
batch uses the lines and text from the same query. Five tasks with later
all are five `--add-tag later` calls.

### 3. Next batch

After each batch, say how many are left and how much time is used. Run
the next batch from the same query, or re-query if the user edited notes
in between.

## Stopping early

When the user says stop or time is up: apply the choices already made,
report how many tasks were handled and how many remain, and end without
further questions. The next run starts again from the oldest tasks.
