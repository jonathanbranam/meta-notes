---
name: daily-shutdown
description: End-of-workday shutdown for a meta-notes notes root, about 15 minutes. Use when the user says "shutdown", "daily shutdown", "close out today", or "end my day". Collects loose items into tasks, checks PRs, records next steps, fixes today's time log, writes a Follow up list, commits, and marks shutdown complete. It does not plan tomorrow (that is daily-plan).
---

# Daily Shutdown

Close out today's daily note so nothing is left in your head or inbox.
It does not plan the next day; it ends by offering `daily-plan`.

## Time budget

About 15 minutes. Say so in one line when you start. Keep each step short
and ask one thing at a time.

## Start

1. Run `command -v meta-notes`. If it prints nothing, stop and tell the
   user: "`meta-notes` isn't on your PATH. Link the plugin's
   `bin/meta-notes` into a directory on your PATH, for example
   `ln -s <plugin>/bin/meta-notes ~/bin/meta-notes`." Don't read or edit
   any note.
2. Run `meta-notes conventions` and follow it for everything below.
3. Run `meta-notes note daily` to get today's note path (it creates the
   note if it's missing). Call it TODAY_NOTE.

## Hard rules

- Change existing task lines only with `meta-notes task update`, with
  `file`, `line`, and `text` from `meta-notes tasks --json` (or `grep -n`
  for checklist lines, such as markers). Never rewrite a task line.
- If `task update` says the line changed, re-query and retry with the
  current text, or ask the user. Never guess.
- New lines (tasks, Follow up items) are written directly: tags before
  dates, within 80 columns.
- Don't plan tomorrow and don't walk old tasks (that is `task-cleanup`).
- Don't read git history or file modification times.
- Commit only after the user confirms. Never push.
- If the user says stop, go to "Stopping early".

## Steps

The next workday is the next Monday to Friday after today (Friday's is
Monday). Call it NEXT_DAY.

### 1. Collect

Ask the user to paste or name anything still loose: starred email, saved
Slack threads, anything promised or thought of today. For each item,
propose one task line and where it goes:

- a project it belongs to: that project's home note (see
  `meta-notes projects --json` for paths and tags)
- otherwise the matching area note, or TODAY_NOTE under `## Notes`

Write it as `- [ ] <what> [#tag] 📅 [<date>]`, with a link to the thread
when there is one. Confirm the list, then write the lines. Remind the user
to unstar or unsave what was captured.

### 2. PR check

Ask which open PRs need the user (reviews requested, repos they own), or
if `gh` is available and the user agrees, run
`gh search prs --review-requested=@me --state=open`. Each PR that needs
action becomes `- [ ] Review <repo>#<number> <title> 📅 <NEXT_DAY>` in
TODAY_NOTE under `## Notes`, unless a task for it already exists
(`meta-notes tasks --all --json` filtered on the PR link).

### 3. Next step per project

Find the projects worked on today: the tags in `meta-notes time --json`
(`by_tag`) matched against the `tag` of each project in
`meta-notes projects --json`, plus projects linked from TODAY_NOTE. Confirm
the list with the user.

For each, check its open `#next` tasks with
`meta-notes tasks --all --tag next --json` (a project's tasks are those in
its note or folder plus those with its tag). Ask for the next step:

- still right: leave it
- done: `task update ... --status x`
- replaced: mark the old one done or `--remove-tag next`, then write the
  new step in the home note as `- [ ] <step> #next 📅 [<date>]`

### 4. Time log

Run `meta-notes time --json` for today. Look at `entries`:

- each `gap` entry (for example 13:00 to 14:30)
- each entry of 60 minutes or more with no tags and no `[[link]]`

Ask about each in one question: what happened, and which project or work
item it belongs to. Update the `### Log` in TODAY_NOTE from the answers:
add an entry for a gap (text, tag, `* start:`, `* end:`), or add a tag or
link to an unclear entry. Log entries aren't tasks; edit them directly.
A rough log beats none; accept "don't know".

### 5. Follow up

Draft a short list for NEXT_DAY: unfinished work, promised replies, and
the first thing to do. Use today's unfinished time blocks and step 1–3
answers. Write it under `## Follow Up` in TODAY_NOTE as checklist lines
without dates (`- [ ] reply to Sam`), adding the heading after `## Notes`
if the note lacks it. `daily-plan` turns items into tasks when needed.

### 6. Commit and mark

1. Find the marker with `grep -n 'shutdown complete' "<TODAY_NOTE>"`. If
   it's missing, add `- [ ] shutdown complete` under the Week Plan link.
2. Check it:
   `meta-notes task update "<TODAY_NOTE>:<line>" --expect '<text>'
   --status x`.
3. Show `git status --short` and the proposed command,
   `git add -A && git commit -m "Shutdown <YYYY-MM-DD>"`. Run it only when
   the user confirms. If they decline, leave the changes uncommitted.

### 7. Offer daily planning

Say shutdown is done and ask: "Plan <NEXT_DAY> now with `daily-plan`?"
Don't start it yourself. Declining is normal; planning then happens in
the morning.

## Stopping early

When the user says stop:

- Save everything decided so far (tasks, log edits, Follow up lines).
- List the steps not done.
- Leave `shutdown complete` unchecked.
- Offer to commit what is there, with the same confirmation.
- End without further questions.
