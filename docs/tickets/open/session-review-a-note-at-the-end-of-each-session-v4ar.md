---
id: v4ar
title: "Session review: a note at the end of each session"
kind: feature
opened: 2026-10-06
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: []
---

## The ask

# Session review: a note at the end of each session

Relayed by the notes advisor, 2026-10-06 18:27 (notes m-0111): "From the
human, via advisor (notes)". Pending the human's review; no task yet.

## The ask (the human, verbatim)

"whenever you end a session, do a handover, or at the end of the day, I want you to write a note summarizing what happened during that session. We should work through this prompt.

Create a ticket and write your suggested prompt in it, and I'll review it. I want you to cover:
- our interactions
- some conclusions and suggestions from it
- your observations of me being on task or off task
- things I did well
- things I didn't do well
- things that we could improve
- things about our interaction that could have been better
- things to improve about the system

It's just a space for you to make suggestions and give feedback on how the session went.

I think we should create a meta notes command for this to create the exact note or something, so you can just call that. Ask for that, and then this should really be a skill. I don't know. We need to talk through skills versus these roll things, but it should be a skill that ships with it, so I can invoke it at work as well.

I should write a note out, probably the same structure as the daily note, but in a resource folder under some folder names like resource/agent/something, and then it would be by quarter and then by day. The same structure we have for daily notes"

## Proposal (advisor's draft, for review)

1. Command: `meta-notes note session [YYYY-MM-DD]` creates the day's session-review note if needed (from a template) and prints its path, like `note daily`. Path: `resource/agent/sessions/YY-QN/YYYY-MM-DD Ddd.md` (same naming as `plan/daily/`). One note per day; each session appends its own section, so several sessions (or roots: work and personal each have their own) don't collide. Optional: `meta-notes session-review append <file> --session <name> --text-file -` to add a section without hand-editing.
2. Template (`templates/session-review.md`):

   # Session Review - 2026-10-06 Tue

   `Daily Note: [[plan/daily/26-Q4/2026-10-06 Tue]]`

   (one `## <HH:MM>-<HH:MM> <agent/role>` section per session, below)

3. Skill `session-review`, shipped in meta-notes `skills/` like daily-shutdown, so it works in any notes root (work and personal). Role prompts (e.g. notes' advisor) call it at a handover, a restart, or end of day. Skills vs role text: the skill owns the "how"; a role only says "run session-review before a handover". (To talk through with the human.)

## Suggested skill prompt (draft)

---
name: session-review
description: Write a short review of the session that just happened (what we did, how the human's day went against plan, what went well or badly, and what to improve in our work together and in the system) into the day's session-review note in a meta-notes root. Use at the end of a session, before a handover or restart, at the end of the day, or when the user says "session review" or "review this session". It doesn't plan (daily-plan) or close out the workday (daily-shutdown).
---

# Session review

A candid, short look back at one session with the human, for them to read later. It's feedback, not a log: the daily note's Worked On and Time Log already hold what happened. Aim for 15-40 lines.

## Steps

1. `meta-notes note session` for today's path (after midnight, the date the session mostly covered). Read the daily note for the session's span: Worked On, Notes, the Time Log and Time Block (plan vs actual), tasks done and still due.
2. Add one section, `## HH:MM-HH:MM <your agent name>` (US Eastern), with these headings; skip one only if there's truly nothing to say:
   - **What we did**: 3-6 bullets, high level, linking the notes touched.
   - **On task / off task**: plan vs actual from the time block and log; where the day held, where it slipped and why (as far as the record shows), with times. Facts first, then a short read.
   - **Went well (the human)**: specific, with the moment ("left for the 9:00 interview on time despite a detour").
   - **Didn't go well (the human)**: specific and kind, no lecture; what it cost (a missed stop time, a skipped workout).
   - **Our interaction**: what worked, what could have been better on both sides: misunderstandings, my mistakes (wrong claims, things I had to redo, questions I shouldn't have needed), messages that were hard to act on.
   - **Conclusions and suggestions**: 2-4 concrete changes to try next time (a habit, a reminder time, a check-in).
   - **The system**: meta-notes, bridle, skills, rules: bugs hit, missing commands, friction; say whether it's already filed (with its ticket) or should be.
3. Be honest and specific; quote the human where it helps. No praise padding, no blame. Don't invent motives: say what the record shows and mark guesses as guesses.
4. Personal vs work: write in the root you're in; don't copy work detail into a personal root (or the reverse).
5. Commit the note (only that file) and push, per the root's conventions. Link it from the daily note's Worked On (`session review: [[...]]`).
6. Offer the human the 2-4 suggestions in one short message; anything for meta-notes/bridle goes to the orchestrator.

## Open questions for the human

- Path: `resource/agent/sessions/` OK, or another name (`resource/agent/reviews/`)?
- One note per day with a section per session (proposed), or one note per session?
- Does the human want to read it each morning (link from the next daily plan), or only weekly (weekly-review reads the week's)?
