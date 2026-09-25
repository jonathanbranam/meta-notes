# Planning System Conversation

Transcript of a claude.ai conversation (about 2026-09-20 to 2026-09-21) that set out
the requirements for the meta-notes planning system. It produced
[planning-system.md](planning-system.md), `openspec/changes/cli-core/`, and
`skills/project-review/SKILL.md`.

Source: https://claude.ai/share/b7bcbca4-20e6-4353-8d95-d8376ea80bc6

Tool calls from the original chat ("Ran N commands") are not included.

---

## User

Help me write requirements for a personal, work, and project management solution.

I currently manage things in a few different ways, and I want to unify those. I might keep aspects of my work and personal life separate. At work, I have a locked-down situation where I can access some personal information, like my calendar, but my work information cannot leave my work laptop, servers, or setups.

The solution for work has to be fully self-contained and not rely on any external services. We'll probably have few to no integration points, but for my personal solution, I could integrate with other services if necessary. At work, I can run an app. I could write and run an app on my desktop, certainly in a browser. I

My current solution primarily revolves around some concepts from Cal Newport on time blocking and project tracking. He suggests, in some cases, a Kanban-like approach, which I also favor, and I use Tiago Forte's PARA method of organization at work. I do most of my organization and planning with Markdown files in the PARA folder structure, and I manage all of that through a custom Vim plugin, which I could use and enhance for this. I also want, potentially, a little bit more structure to that.

What I'd like to do in this chat is set down the requirements and expectations for project planning. Work is the main priority, with the personal life coming second.

I think the main thing is that when I arrive at work, I have too many projects and too many loose ends. I've written most things down in my system, but I'm not very disciplined about reviewing what needs to be done or scheduling the week.

At a minimum, for this solution, I want a clearly defined way of defining my current set of projects, the next steps for each of those (similar to David Allen's Getting Things Done), and:
- Clearly what I am waiting for
- What's on my schedule
- Upcoming deadlines for projects
- A concept of last touched: when have I last worked on this?
- Is this something I need to come back to?

I want something where I'm clearly keeping track of commitments.

For example, if I tell somebody I'll review that document, or somebody sends me a design or proposal for review, if I have PR reviews that need to be done, I want to keep all of those managed and accessible. I need to plan my week and time in a more structured way so that I'm clearly able to look at what I have to do this week and the time that I have available. That way, I can make decisions to get the right things done and do the time blocking necessary to get them done.

I want:
- a weekly plan at the end of the week
- a daily plan every day
- a short daily review
- preparing for the next day
- a weekly review

I need more discipline in these things.

---

## Claude

Before drafting anything, one observation that should shape the requirements: your capture is already working. You've written things down. The failure is at review and commitment — you don't reliably look at what you wrote, and you don't decide what the week actually holds. So the system's primary product is the *cadence*, and the data model exists only to make each cadence step fast and honest. If a field doesn't feed a review, it doesn't get a field.

Here's a first cut.

**Entities**

- **Project** — anything needing more than one action. Fields: status (active / paused / waiting / done), outcome statement (one sentence: what's true when this is closed), deadline (hard or soft), last-touched date, PARA area.
- **Next action** — exactly one per active project, concrete and physically doable. Zero next actions on an active project is an error the system must surface.
- **Commitment** — something you owe someone or someone owes you. Fields: direction (I owe / owed to me), counterparty, what, promised-by date, source (verbal, Slack, PR, email). "Waiting for" is just the inbound direction of this.
- **Block** — a scheduled chunk of time, pointing at a project or a commitment.
- **Log entry** — append-only record of what you actually did in a block, which drives last-touched.

**The five cadences** (each is a defined ritual with an input view and a required output artifact)

1. **Weekly plan** (Friday): review every active project, confirm next action, confirm commitments, look at the coming week's calendar, block time against the top priorities. Output: a dated weekly plan file.
2. **Daily plan** (morning): pull today's blocks from the weekly plan, adjust against reality, commit to a small set.
3. **Daily review** (end of day): log what happened, update last-touched, capture new commitments made during the day.
4. **Next-day prep**: fold into the daily review — the last step is naming tomorrow's blocks.
5. **Weekly review**: the accountability pass — projects untouched for N days, commitments past their promised-by date, deadlines inside the horizon, plan-vs-actual on last week's blocks.

**Required views** — the system must answer these in one command, no scrolling:

- Everything I owe someone, sorted by promised date
- Everything I'm waiting on, with age
- Active projects with no next action
- Projects not touched in > 14 days
- Deadlines in the next 30 days
- This week: blocked hours vs. available hours

**Constraints** I'm taking as given: work instance is airgapped, plaintext Markdown in PARA on disk, no external services, no data leaving the machine. Personal instance may integrate. Same tool, two isolated stores — never one store with a partition.

---

Four forks I'd want you to settle before this goes further:

**1. Interface.** Does the Vim plugin stay the primary UI with added structure, or does the plugin become one of several clients over a defined file format? The second is more work but lets you build a dashboard/browser view for the reviews, where Vim is weakest. Reviews are exactly where you need a wide, scannable, read-only surface.

**2. Structure level.** Markdown-with-frontmatter (git-friendly, editable anywhere, but queries mean parsing every file) vs. Markdown for prose + SQLite index rebuilt from the files (fast views, single source of truth stays plaintext). Given your views list above, I lean toward the second — build it as a derived artifact, same as your materialized-CSV pattern.

**3. Time blocking source of truth.** Does the system own blocks and push to calendar, does it read the calendar and let you annotate, or is time blocking purely internal? At work you have calendar access; the question is whether meetings-as-constraints get read in automatically or you transcribe them during the weekly plan. Transcription is friction, but friction during planning is arguably fine — it forces you to look.

**4. Enforcement.** This is the one that actually decides whether you use it. With no external services, what makes you do the Friday review? Options: a check that blocks other commands until today's plan exists, a staleness banner, a streak, or nothing but a calendar appointment. My instinct is a soft gate — the tool refuses to show you anything but the review view when the review is overdue.

Which of these four do you want to work through first?

---

## User

I would like the backing data store to continue to be Markdown files. We can add a layer on top of what I do in Vim as needed, but I will primarily prefer to author and update the text in those files using Vim. I have tooling to create all of these files in a standard format.

You may be able to look at this. I think if you go to github.com/JonathanBranam/meta-notes, you can probably look at the repo.

I don't need the tool to block me if I haven't done a review, but certainly reminders would be good. In terms of a dashboard or local view, I can run a local server and then connect to it from a browser. I think that would be very valuable for live updates that would need either some kind of polling mechanism, or, I suppose, FS events. This is Mac OS only.

---

## Claude

I read through the repo. Most of what you want already has a home: `plan/week/` exists, templates run `find_tasks.py` at creation, the time block table already tracks plan vs. actual, and tags already flow through the time log. Your own requirements doc even lists "content structure for weekly plan templates" as undefined. So this is mostly filling specific gaps, not a new system.

**1. Project metadata.** Add frontmatter to project notes (a legitimate use of your "sparingly" rule):

```markdown
---
status: active        # active | paused | waiting | done
outcome: Feature store serving online features for card models
deadline: 2026-10-30
tag: feature-store
revisit: 2026-10-01   # "come back to this" date
---
```

Open question: for folder projects, which note carries this? I'd require one canonical note per folder (e.g. `index.md`).

**2. Next action.** A `#next` tag on one task. Rule: every active project has exactly one incomplete `#next`; zero or several is flagged.

**3. Commitments.** Tasks with a direction tag and a person, captured wherever they come up (usually the daily note). `find_tasks.py` already scans everywhere, so the aggregation is free.

```markdown
- [ ] Review Mary's scoring proposal #owe @mary 📆 2026-09-24
- [ ] PR #412 feature-store backfill #owe #pr @raj
- [ ] Bob's sign-off on rollout plan #waiting @bob 🛫 2026-09-21
```

For `#waiting`, 🛫 marks when you asked, so age is computable. `@person` is new syntax: parser plus highlighting.

**4. Last touched: derive it, don't author it.** Avoid file mtime: your rename and archive commands rewrite links across files, so mtime lies. Instead, a project was touched on the latest date that its `tag` or a `[[project/...]]` link appears in a daily note's Log or Actual column, or a task in it got a ✅ date. You already log `#feature-store`-style tags, so this mostly works with your existing habits.

**5. Rituals.** Each ritual needs a template section and a machine-checkable completion marker. Without the marker, reminders and the dashboard can't tell whether you did it. I'd merge weekly review and weekly plan into one Friday note, reviewing first and then planning. That note is created for the coming Monday.

- **Weekly note, generated at creation.** A frozen snapshot of last week's plan adherence, then a project table (status, next action, last touched, deadline) with flags for stale, missing-next-action and revisit-due. It also lists commitments in both directions and deadlines in the next 14 days. You then write 3–5 priorities and block them. Because the snapshot is frozen, you get history; the dashboard shows the live view.
- **Daily morning plan.** Uses what the daily template already does, plus open `#owe` items due this week.
- **Daily shutdown.** Log, capture any new commitments, then create tomorrow's note and fill its Plan column. Mark it done with `- [x] shutdown complete`.

**6. Dashboard.** Stdlib `http.server` bound to 127.0.0.1 only, reusing your existing parsers. For updates, poll mtimes every 1–2s and push to the browser with Server-Sent Events. Your scale (thousands of files, not millions) makes polling essentially free, and it avoids two FSEvents/kqueue problems. First, stdlib kqueue needs an open file descriptor per watched file. Second, Vim's write strategy can replace the file's inode, which silently breaks a per-file watch. Polling by path doesn't care. Keep v1 read-only, since Vim stays the authoring tool.

**7. Reminders.** A launchd agent runs `osascript` notifications that check the completion markers. For example: no weekly note for next Monday by Friday 3pm, or no shutdown marker by 5:30. The dashboard shows the same state as a banner.

**8. Work/personal separation.** Same code, two notes roots, two dashboard ports, no cross-root reads. The personal instance can later add integrations without that code ever running at work.

The biggest remaining gap is **capacity**: "hours available this week" needs your meetings before the daily notes exist. Can you get your work calendar out as an `.ics` export or file on disk, or would you be transcribing meetings into the weekly note by hand?

Once we've settled that, I can write this up as OpenSpec change proposals matching your repo's format.

---

## User

Not sure I want to add the @ sign for people. Let me think about that. I've been using # for everything. I'll have to think about it. I'm not sure I want to introduce any more syntax, but it's an interesting idea.

I think the main thing that I'm concerned with is less about changing the format or structure of the files and more about developing a set of skills and practices that make it easy to perform these rituals. One thing I don't want is the # next to enforcing something. I think a project without a # tag could be called out as a warning, but beyond that, I don't want anything further. I'm not sure the # tag could be waiting. I'm not sure if those are mutually exclusive. There are some things to think about here as I work through my projects.

I would like a skill that helps me talk through a project step by step, reads the project folder, and also searches outside the project folder using the tasks script to find any related tasks. It then helps me walk through the current project state, what needs to be done next, prompts me for additional tasks or things that I need to do, and asks me to review open tasks, particularly those that have been open for a long time, to determine whether they're stale.

The user interface for that is something I'm not sure how to build for my personal life. I would set up an AI harness for that, but that's not super easy to do at work. At work, I need to keep my AI interactions primarily within the agent. I can initiate a Claude-P, but beyond that, we're not supposed to be scripting or automating Claude.

The main thing that I've run into currently is that if I ask the agent to help me plan my day, my current set of projects and tasks is too out of date. The agent doesn't have the proper setup or context to help me plan effectively. That's one reason why a project review skill is a priority.

And then, something that I am continually failing at but intending to do is to keep track of how long things actually take. That's something that I would like as part of the weekly review. That could be automated to a degree, but I'd like to have an agent look back at my week, assuming that I've tracked my time, which is currently a problem. I don't always track my time, but look back at my week and summarize how I spent my time. There's the time log command that can help with that.

Also, looking at any other updated files throughout the last week can be informative about what I did and what I spent my time on. I think that would be a very useful additional tool. We could easily do this, probably using Git or potentially just write a script that would compute a diff of all the files that had changed this week. I don't know if we could automate some of the ignoring of structural changes, like moving files around and renaming things, or if the agent would need to look at the diff to determine that.

One thing I'd like from the UI: you said read-only for V1, but I could definitely use a better UI and a better experience for tracking my time. I have a time log, and the format is fine and effective, but it's a little bit of friction to update it in Vim. We could invest in better Vim tooling for that, which would be fine, or a better external tool for that. This is a very long message. I think the main thing I want to call out is that daily and weekly planning is really, really critical. Daily review should be short but is also very important, and the weekly review is very important.

To get us there, to get started with us and make it work properly, I need a skill or help to go through all of my projects and do a reconciliation of them one by one. It's overwhelming to me. I've tried to do this with the agent, and I just had to cancel it because I didn't have enough time to go through all projects. It presented me with 10 projects to review in one chat.

I just want to say: here is a project. I may have only 5 or 10 minutes between meetings. Here's a project to review:
- Here are the files.
- Here's the state of the project.
- Here are all the to-dos associated with it.
- Here's the last time these files were meaningfully modified.

What is the state of this project? What should we do with it?

And, as I mentioned earlier, I need perhaps a little more flexibility in how to organize active versus inactive projects and ways to reorganize and move things around.

For example, I have a project that started out with one name in the file system and then split into a different project and is now spawning multiple additional projects because it's been about 1.5 years since it started. There are essentially new projects associated with the same original thing. That original project is essentially finished, but archiving it feels like the wrong move because I'm still using some insights and information from it.

I'm not sure if I need better tooling here to either move it to inactive or, perhaps, turn it into an area. That strikes me as perhaps the right solution here: essentially, to convert a project into an area and potentially nest that within the area.

I need some more tooling around moving files around, keeping those links up to date, and fixing the links. I actually need those tools to be invocable by the agent because that's another issue that came up. I wanted to make some changes, but the agent was not able or suggested that I do it myself in Vim because the scripts were all written in Vim script. That needs to be solved as well, as a kind of high priority.

Both the agent and this web server (local server) should be able to perform essentially all of the actions that the MetaNotes Vim plugin can perform. MetaNotes either needs to be invocable from the command line or needs to migrate to being a CLI tool that the Vim plugin calls out to. I want a single source of code here.

I'm talking about things like:
- archiving
- moving notes
- renaming notes
- archiving a note, a folder, or a hierarchy
- moving a folder or a hierarchy

Things like that.

The main thing that I'm missing here is integration with some AI skills that help me do the planning, and maybe some easier ways to view my plan, update it, and add reminders. Possibly, I could allow reminders from the local web page. I think I don't know if that's allowed from localhost in Chrome, but if it is, I could turn that on for pop-ups.

I'm fine creating read-only vim buffers. I do that for tasks and my time log, and I think something else as well. That's fine, but those are a little tricky to update. The read-only buffers are great for looking at all my tasks, but I still have to go into the individual notes to update those tasks. The task description and tagging system works well, but again, I just tend to accumulate lots and lots of tasks that are not finished, and they clutter up my task list. Right now, I probably have dozens of unfinished tasks, most of which are abandoned, and I have lots of projects, most of which don't have any active work happening on them. I need a way to start fresh and consolidate.

In that meta notes solution, I also need a slightly better way to deal with archive. I have some significantly old projects that are in archive that really shouldn't be search hits any longer. If I have a recent project that I've completed and that moves to archive, it's still relevant, and I still want search hits on it. I don't know how to handle that currently. Maybe I should move certain projects to resource instead of archive, or if I need actually a deep archive, some sort of moving things completely out of my notes structure because they're just almost completely irrelevant.

---

## Claude

The plan reorders around what you described. The real blocker isn't file format. It's that your projects and tasks are stale, so neither you nor the agent can plan against them. That gives a clear sequence.

**Priority 1: a meta-notes CLI as the single source of code.** Nothing else works until the agent can do what Vim can. Move archive, move, rename, link rewriting, and task edits into Python (stdlib, as now). The Vim plugin then becomes a thin caller, and the agent and local server call the same commands. Minimum command set:

- `move <src> <dst>`: a note, a folder, or a whole hierarchy, with link updates. Archive and project-to-area conversion are just moves with conventions.
- `rename`, `archive`
- `task set-status <file>:<line> <char>`: checks the line text still matches before editing. `find_tasks.py` already records file and line number. This is also what makes your read-only task buffers editable: a mapping in the buffer calls this command on the source line.
- `project brief <path>`: described below.

**Priority 2: a single-project review skill, one project per sitting.** The failed attempt showed you ten projects at once. This skill takes one, fits in 5–10 minutes, and records that the project was reviewed, so your reconciliation spreads over days. Invoking it with no argument picks the project reviewed least recently.

1. **Gather via the CLI, not by reading every file.** `project brief` returns the files, the last meaningful change, open tasks inside the project, and related tasks elsewhere (by tag and link). It also returns time logged against the project tag. A script keeps this fast and cheap. The agent opens individual files only when it needs to.
2. **State in about ten lines:** what the project is, what's happened recently, and what's open.
3. **Disposition:** continue, pause, done, convert to area, split, or merge.
4. **Stale tasks, oldest first, batched to fit the time:** "these 8 are over 90 days old, cancel all or go through them?"
5. **Next action.** Missing one is a warning only, per your call. `#next` and `#waiting` can coexist.
6. **Capture anything new**, apply the edits via the CLI, and stamp `reviewed: <date>`. If you stop early, it saves whatever is done.

This runs inside interactive Claude Code, so it fits your work constraint.

**"Last meaningfully modified" and the weekly change summary** are the same problem. If your notes directory is a git repo, the cleanest approach is for structural CLI commands (move, rename, archive) to commit themselves with a recognizable prefix. "Meaningful changes this week" is then the diff that excludes those commits, and git's rename detection (`-M`) covers anything you move by hand. Without git, the fallback is a diff filter that drops changes affecting only `[[link]]` targets. That works but is fuzzier.

**Priority 3: a weekly review skill.** It runs `time_report` for the week, summarizes the meaningful changes, and compares both against last week's plan. Where time logs are missing, the file changes show roughly what you worked on. That makes the gaps in your time tracking visible without guilt, which may do more for the habit than any tooling.

**Priority 4: daily plan and shutdown skills.** These stay short and depend on reviewed projects to be useful.

**Priority 5: the local dashboard, now with writes.** Because it calls the CLI, it can offer a quick time-log entry (start and stop a timer on a tag), which is where Vim adds the most friction. Browser notifications do work from `localhost`: Chrome treats it as a secure context, but notifications only fire while the tab is open. A launchd plus `osascript` job covers the times the tab isn't open.

**Archive tiers.** Moving old material out of the tree breaks links. Keep it in place and exclude it from search instead:

- `archive` stamps an `archived:` date.
- Search tools skip anything archived more than about 12 months ago by default, with a flag to include it.
- The CLI regenerates a `.ignore` file that ripgrep respects, so your Vim grep gets the same behavior.

**Your 1.5-year project.** Converting it to an area is the right PARA answer: it's now an ongoing responsibility that spawns projects. Move it to `area/<name>/` with its history intact. The new projects then live in `project/` and link to the area, or nest under it if you prefer. With `move` in the CLI, either layout is a one-line operation.

One question decides how Priorities 2 and 3 get built: are your notes directories, work and personal, already git repos?

---

## User

Okay, good. I think there's some really good direction in that last set of priorities.

Yes, my notes folder is always a Git repo. My commits are not necessarily meaningful commits. They're generally time-based commits, which I think makes sense for what I do. I'll usually commit once a day or once every couple of days. There are not any fine-grained commits around particular projects, but if I have an end-of-day routine, that should always include committing at the end of the day, and that would be part of my routine.

I want to talk a little bit more about weekly planning, daily planning, and end-of-day tasks. One way to find things that I'm overlooking is, of course, to look for tasks that have been open for a long time and where I owe somebody something (whatever that means). A task that's been open a long time is an indication of something I've been putting off.

One thing in particular that I want to get better at is PR reviews. I don't review a lot of PRs, but it is something I tend to procrastinate on. I need a reminder to look for open PRs. They should be listed in GitHub and tagged to me. For any that are not, I have a small number of repositories that I'm responsible for. It wouldn't be hard to both automate and/or quickly check if any PRs need reviewing on those repositories. Probably, that doesn't need to be necessarily automated, but mostly it's the reminder to ask me if I have any open PRs.

What I want to do at the end of the day, as part of my shutdown routine, is to do the collect phase from Getting Things Done. It's also mentioned in Cal Newport's work, similarly: to be sure that I've written down the things that I need to do. I often get to the end of the day and forget to or neglect to write everything down that needs to be done to create tasks for that, or add some notes about what the next thing I need to do for a project is. Another specific area for that I need to go through my Slack and email, particularly saved Slack messages. I've been tagging and saving Slack messages to come back to or as a reminder to do something, and I have probably dozens of those as well, the vast majority of which are pointless.

I need to spend maybe 5 minutes a day just cleaning up a few of those until I get them down to zero, and then make it a habit to clean them up at the end of the day so it stays at zero. I need to essentially move that into my note system as some kind of a note, a follow-up, or a task. I can copy the contents of that message out if I feel like it's important, and keep a link to the thread if it's important.

Similarly, with email, I do not keep an Inbox Zero. I have a vast number of emails, many of which are unread. I would like to make some progress with that, although I receive dozens of emails a day that are largely ignorable. I should potentially archive all of them and then work to come up with a system for keeping my inbox cleaner. I also star emails for follow-up. That's another end-of-day thing where I should go through all my starred emails, record those as tasks, and unstar them, so that I keep that in my task list instead of in my email

In terms of the overwhelming number of tasks that I have, I have a current solution that should be in the meta notes repo, I believe. If not, it is something that I use, and I use #later as an indicator that is the same idea as David Allen's someday maybe list, someday maybe file. I just like "later" a little bit shorter. I could potentially rename it to "maybe," but "someday" has too many letters. I like to keep my tasks fitting on one 80-character line, and that can be challenging with a bunch of tags.

At any rate, those tasks: that's one mechanism where, if I tag things as #later, they fall out of my to-do list but are still tracked. I think that's useful.

I would also potentially like to improve the way I track tasks that do need to be done. I track everything as a Markdown list item or checklist item, and something that indicates it's a task is that it has a due date on it or a start date. That works pretty well, but sometimes I don't really have a date, or I want it to show up in my list. I might be willing to explore another indicator that something's a task without a due date. Maybe another emoji, or maybe if I include the calendar emoji even without a date, that could indicate something that's an actual task that needs to be done. That just hasn't had a due date assigned yet. I'm not sure, but it's something to consider.

---

## Claude

Git with daily commits works fine. Two small adjustments make it useful for "meaningful change" detection. First, have the CLI's structural commands (move, rename, archive) make their own commits with a `meta-notes:` prefix, so structural churn is separable from your daily commits. Second, make the commit the last step of shutdown. Your habit doesn't change otherwise.

### Task model

`#later` isn't in the repo; I checked. So it's a convention you use rather than something the tools filter on. Here's a model that formalizes it without adding syntax:

| Line | Meaning | Shows in task lists |
|---|---|---|
| `- [ ] text` | checklist item in a note | no |
| `- [ ] text 📆` | task, no date yet | yes, as undated |
| `- [ ] text 📆 2026-09-24` / `🛫 …` | dated task | yes |
| any of the above + `#later` | someday/maybe | only with `--later` |

A bare 📆 is a good choice. It reuses your existing marker, and it reads as "due: TBD", which invites you to assign a date during review. The parser change is small. One cost for your 80-column rule: most terminals render the emoji two columns wide.

**Task age comes free from git.** `git blame` on a task line gives the date it was last edited, at day granularity, which is enough. That's the right staleness signal anyway: a task nobody has touched in 60 days is being put off, whenever it was created. No created-date syntax needed.

### Shutdown (about 15 minutes)

1. **Collect.**

   Notes are the only inbox; Slack and email aren't.

   - **Starred email:** each becomes a task, then unstar it.
   - **Saved Slack:** clear a few per day, newest first, since those are most likely still live. Each becomes a task with a thread link, or gets unsaved. For the backlog, pick a cutoff date and bulk-unsave everything older. Dozens of mostly pointless items aren't worth five minutes each.
   - **Your head:** anything you promised or thought of today.

   The agent can cut friction here. Paste a Slack message or email subject and it writes the task line with the link into the right note.
2. **PR check.** Anything with a review requested from you, plus your own repos. Each open PR becomes a dated task for tomorrow. The check happens at shutdown; the review gets a block in the morning plan. That split is what beats procrastination.
3. **Projects touched today.** Write the next step for each while it's fresh.
4. **Backfill the time log** from memory. A rough log beats no log, and the weekly review depends on it.
5. **Tomorrow.** Create the note and rough out the time blocks.
6. **Commit**, then check off `- [x] shutdown complete`.

### Daily plan (about 10 minutes)

Start from yesterday's rough blocks. Add meetings, due and overdue tasks, and the PR tasks.

Then add a small forcing function: surface the **2–3 oldest untouched tasks** (by blame date, excluding `#later`). For each, decide: do it today, date it, `#later`, or cancel. A few a day works through the backlog without a bankruptcy session, and it directly targets what you're putting off.

Getting meetings into the daily note is still open: transcribing from your calendar is fine unless you find a way to export it.

### Weekly review and plan (Friday, 45–60 minutes)

1. **Look back:** the time report summary, meaningful file changes, and plan versus actual.
2. **Commitments:** anything owed to someone or waiting on someone, plus all tasks untouched for more than 30 days.
3. **Undated 📆 tasks:** date each or `#later` it.
4. **Projects:** run the single-project review on the 2–3 projects due next in the queue, not all of them.
5. **Scan `#later`:** promote anything that has become live.
6. **Plan next week:** 3–5 priorities, deadlines, and blocks placed against meetings.

### Email backlog

This is a one-time reset. Bulk-archive everything older than two weeks except starred mail, then let the shutdown routine keep starred at zero. Nothing is lost, and search still finds it.

Should I draft the shutdown skill's SKILL.md first, since it feeds everything else, or write the full set up as OpenSpec changes for the repo?

---

## User

This is looking good. A few notes for my calendar: I'm not sure if I can export it as a calendar for the week. I don't really know how that works. Everything is in Google Calendar, but we don't have connectors for it, and we're not allowed to use any APIs for an agent to connect to the calendar.

I've heard some people are taking a screenshot of their calendar and then giving that to the agent. We are allowed to share our calendar details with the agent, but there's no actual Google integration allowed. I do like subscribing to my calendar also from my Mac OS calendar application. I don't know if we could use an OSA script to pull through that somehow, or even to create events that way, because I'm authenticated with Google on my calendar app. 
The #later syntax is officially supported in the version of Meta Notes that I have on my work computer, but I must not have backported it to my personal GitHub implementation. That's something we can do.

I have some more improvements for the find task script as well that I haven't brought back. I can look through that and summarize them. I've added some command-line parameters to trim the results and control the date ranges of the script a little more easily. I don't know what part of that is here.

You can specify date ranges for due dates and also specify the tags that you're interested in. That way, the agent can get a focused list of tasks instead of seeing the entire dump. The #later tasks are excluded from that by default in the base script, and the base script sorts them completely separately in a separate section. That's something we can reconcile later.

On the daily shutdown, I do think it would be really beneficial to write a plan for the next day to create the note for tomorrow and write our first pass at a time block for tomorrow. I think that would really save me a lot of time in the morning deciding what to do next.

I generally hit my desk at 8 am every day, but that first hour is often not very productive. I'm trying to figure out my priorities and feeling overwhelmed with my list of tasks and projects, as well as trying to go look at my calendar and write a time block.

Similarly, the week shutdown at the end-of-week review: I think, ideally, that would be done early in the day on Friday. We have a process on our team where we write up what happened the week before, and across all of our teams, but I'm exempt from that because I'm not on a specific team. That may change in any way. I should probably just be doing it for myself and for my manager, but that needs to be done by about 11:00 on Friday.

I would schedule my weekly review early in the day on Friday, and then, as a second step, possibly a separate process:
- Do a plan for the following week.
- Go through my schedule for the following week.
- Look at how many hours of productive work I have.
- See if there are any meetings I need to schedule.
- Look at the week ahead.

It wouldn't be a detailed plan for every day, but having a list of things that I need to tackle on Monday would be really helpful for getting started on Monday morning.

---

## Claude

### Calendar

There are three options, in order of setup effort:

1. **Screenshot.** Allowed today, zero setup, and good enough for a week view. The agent reads meeting blocks and computes free time. Start here so the rituals don't wait on tooling.
2. **AppleScript via Calendar.app.** Your Google subscription syncs locally, so `osascript` can read events without touching a Google API. It's notoriously slow at querying events, so it only works if limited to one calendar and a one-week range.
3. **A small Swift script using EventKit.** Same local data, fast and reliable, and needs a one-time macOS permission prompt. This is what I'd build if option 2 proves too slow.

Creating events the same way also works, and they would sync back to Google.

Before building 2 or 3, check whether local scripted access fits the policy. It's not a Google API, but it is automated access, and writing events back is a bigger step than reading them.

### find_tasks reconciliation

This should come first in the CLI work, since the skills depend on focused queries: tags, date ranges, trimmed output, and `#later` separated out. That's exactly what keeps the agent's context small. When you summarize your work-side changes, I'll fold them into the spec.

### Shutdown as tomorrow's plan

Moving the first-pass time block to shutdown shifts the 8am overwhelm to the moment you have the most context. So the morning ritual shrinks to three steps: open the note, adjust for anything new, and start the first block by 8:15.

Make that first block a concrete task picked the night before, not "plan the day."

### Friday, split in two

**Weekly review, 9:00–10:30.** It produces a written summary by 11, for you now and for your manager if that becomes useful. The agent drafts it from:

- tasks completed this week (✅ dates)
- the week's time report
- meaningful file changes
- daily notes

You edit the draft and it goes into the weekly note. That makes the review worth doing even on a week when you feel behind.

**Week plan, Friday afternoon.**

- **Capacity.** Count free gaps of 90 minutes or more as productive hours. Scattered 30-minute gaps are real time, but not deep-work time, so list them separately.
- **Meetings to schedule**, and deadlines landing next week.
- **Priorities.** Pick 3–5 for the week and roughly place them.
- **Monday.** The plan ends with Friday's shutdown creating Monday's note, with a first-pass time block and a short list. That's the same mechanism as every other day, so Monday is no longer a cold start.

### Skill set

| Skill | When | Output |
|---|---|---|
| project-review | anytime, 5–10 min | one project reconciled, `reviewed:` stamped |
| shutdown | end of each day | inboxes cleared, tasks captured, tomorrow's note and blocks, commit |
| morning | 8:00 | adjusted blocks (light) |
| weekly-review | Friday AM | weekly summary |
| week-plan | Friday PM | next week's weekly note, Monday's note |

The prerequisites are the find_tasks reconciliation plus the CLI move, rename, archive and task commands.

I can consolidate everything we've settled into a single requirements doc whenever you're ready.

---

## User

What can we do from here? Do you have access to a GitHub repo, or can you produce a document that I can upload there?

---

## Claude

I can read your repo (I cloned it earlier since it's public) but I can't push to it, since I have no GitHub credentials here. What I can do is generate files laid out to match the repo's paths, so you unzip them at the repo root, review the diff, and commit yourself.

What I'd produce:

1. **`docs/planning-system.md`**: the umbrella requirements doc covering everything we settled. That's the task model, the five rituals with their outputs, the skill set, the CLI, the dashboard, archive tiers, calendar options, and open questions.
2. **An OpenSpec change for the CLI** (`openspec/changes/cli-core/`, with proposal, design and tasks), since that's the prerequisite for everything else and fits your spec-driven workflow. Your pending find_tasks reconciliation would be its first task.
3. **A draft `project-review` SKILL.md**, written against today's `find_tasks.py` so you can start reconciling projects before the CLI exists. It gets updated once `project brief` lands.

I'd hold off on OpenSpec changes for the other skills and the dashboard until your find_tasks changes are back in the repo, since their specs depend on that interface.

Want all three as a zip, or just the requirements doc for now?

---

## User

Sure. All three is good.

---

## Claude

Now the requirements doc.

Now the project-review skill, written against today's tools.

The zip unzips at the repo root: `docs/planning-system.md`, `openspec/changes/cli-core/`, and `skills/project-review/SKILL.md`. The doc and skill are also below on their own for reading on your phone.

A few decisions I made that you may want to push back on:

- **Skill location.** It's in `skills/`, not `.claude/skills/`, because the latter holds your OpenSpec dev skills and would load it while you're working on the plugin itself. You'd symlink it into the agent's skill directory wherever your notes live.
- **The skill works today.** It uses `find_tasks.py`, git and grep, and edits task lines directly, which the agent can already do. It defers move, rename and archive by writing them down as a task, since those are still Vim-only.
- **Safety on structural commits.** The CLI skips its structural commit if any file it touched already had uncommitted edits, so your in-progress work never lands in a `meta-notes:` commit.
- **Stale line numbers.** `task update` requires the expected line text, so edits fail safely if a line moved since it was read. That avoids adding task IDs to your syntax.
- **No change to the archive spec.** I left `openspec/specs/archive/spec.md` untouched rather than writing a partial MODIFIED block that would clobber its scenarios on sync.
- **find_tasks port.** Section 1 of `tasks.md` is a placeholder for your work-side changes. Once you summarize them, the spec's `#later` and tag-filter requirements can be tightened to match.

*Attachments (not included in the shared page): a zip containing `docs/planning-system.md`, `openspec/changes/cli-core/`, and `skills/project-review/SKILL.md`.*
