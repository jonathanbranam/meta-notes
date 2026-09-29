---
name: checkin
description: Stay-on-task check-ins during the workday for a meta-notes notes root. Use when the user says "check in", "check-ins", "keep me on task", "help me stay focused", or "remind me to log my time". Wakes every 30 minutes or so, asks what the user has done and whether they are on plan, and fills the daily note's Time Block Actual column. It does not plan the day (daily-plan) or close it (daily-shutdown).
---

# Check-ins

Keep the user on task through the workday. Every so often you ask what they
have done since the last update, note it in the daily note's Time Block
Actual column, and help them pick the next thing when they switch tasks.
Needs no hooks: a background command sleeps and wakes you when it exits.

## Start

1. Run `command -v meta-notes`. If it prints nothing, stop and tell the
   user: "`meta-notes` isn't on your PATH. Link the plugin's
   `bin/meta-notes` into a directory on your PATH, for example
   `ln -s <plugin>/bin/meta-notes ~/bin/meta-notes`." Don't read or edit
   any note.
2. Run `meta-notes conventions` and follow it for everything below.
3. Run `meta-notes checkin status --json`. If `note_exists` is false or
   `current` is null and there are no rows, tell the user there is no Time
   Block to fill (run `daily-plan` first) and stop.
4. Tell the user in one line that you will check in about every 30 minutes,
   and that "stop" or "snooze N" changes that. Ask what they are working on
   now, and start the first wait.

## Hard rules

- Wait only by running `meta-notes checkin wait --json` as a background
  command (Bash `run_in_background`), then end your turn. Never poll,
  sleep in the foreground, or start a second wait while one is running.
- Change the Time Block only with `meta-notes checkin actual`. Don't edit
  any other part of a note during a check-in, and don't change tasks.
- Ask one short question at a time. Never nag: if the user doesn't answer,
  or says "not now", skip that check-in and start the next wait.
- Accept rough answers. "Email and Slack" is a fine Actual.
- If the user says stop, go to "Stopping".

## The loop

### 1. Wait

Run `meta-notes checkin wait --json` in the background. Pass `--every N`
when the user asked for another interval. End your turn; you are woken
when the command exits.

### 2. Check in

Read the command's output: `reason`, `current` (the row's `plan`), and
`unfilled` (earlier rows still empty). If `reason` is `end`, go to
"Stopping". Otherwise ask one question, naming the plan:

> It's 10:30. The plan says "write spec". Are you on it, and what have you
> done since 10:00?

### 3. Record

From the answer, write the Actual with `meta-notes checkin actual`:

- one line of what happened, in the user's words, under 40 characters
- `checkin actual <first unfilled time> "<text>" --through <current time>`
  when the whole stretch was one activity; separate calls for separate
  activities
- never `--force` unless the user asks to correct a cell

### 4. Task switching

When the answer shows the user is off plan or switched tasks, don't judge.
Ask once: "Is that a deliberate switch?" Then either help them name the
one next step for the plan's task and return to it, or note the switch in
the Actual and ask what they are on now. When a switch left something
unfinished, offer one line for `## Follow Up` in today's note, but only
add it if they agree.

### 5. Wait again

Start the next wait (step 1). Say nothing more.

## Stopping

When the user says stop, or `reason` is `end`:

- Don't start another wait.
- If a wait is still running, stop it.
- Say how many rows are still empty (`checkin status`), and offer
  `daily-shutdown`. Don't start it yourself.
