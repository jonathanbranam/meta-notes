---
id: 5zm3
title: "Context-aware nudges: checks prompted by place, day and what's going on"
kind: explore
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [u34c, zyab]
tasks: []
---

# Context-aware nudges

The human, 2026-10-03 (relayed by the notes advisor), GTD-style:

> We're going to need a set of things that, similar to David Allen's
> Getting Things Done, I could be prompted or nudged to check on, depending
> on where I am and what's going on that day, so it would require my
> schedule.

Location: "my note should keep track of where I am. If I'm out of town or
something, this should be indicated in your context so you can make
appropriate nudges for me" (and later from the phone app). Examples:

- "you started the laundry an hour ago, two hours ago, go check to see if
  it needs to go in the dryer";
- "you're home, it's Saturday": does the recycling need to go to the
  recycling center;
- the kitchen compost: "a periodic reminder... don't schedule that".

## Shape, to explore with the human

Two parts. The prompting itself (waking, noise, the phone) is bridle's and
the phone app's (sent to dalek with that idea). meta-notes holds the data:

- where the human is: a field in the daily note (home, out of town, a
  city), which `prime` puts in the agent's context;
- the nudge list: checks that are not scheduled tasks, each with when it
  applies (place, day, time since something started, a rough period), in a
  note an agent reads during `checkin` or the daily plan;
- "started the laundry" as a time-stamped event an agent can measure from
  (a Time Log entry may already be enough).

Nothing to build until the human picks the first nudges they want. The
daily workout (u34c) may be the first.
