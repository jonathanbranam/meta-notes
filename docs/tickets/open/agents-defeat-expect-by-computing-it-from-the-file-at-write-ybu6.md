---
id: ybu6
title: Agents defeat --expect by computing it from the file at write time (sed/grep)
kind: explore
opened: 2026-10-08
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [zk5p, t85d]
tasks: [mn-ybu6]
---

## The ask

The human, 2026-10-08, via the notes advisor (relayed to the meta-notes
aide as m-0713), asking for this ticket:

> write up exactly what happened and file a ticket on the MetaNotes repo
> ... include examples of the commands that you're running with the sed
> and the grep so that we can analyze and kind of come up with a better
> solution so that these kinds of things are prevented or much harder to
> happen by accident.

Related, already filed from the advisor's earlier message (notes m-0127):
zk5p (guard hook, idea 3; approved by the human) and t85d (revision
token, idea 1). This ticket is the incident write-up and the analysis
across all five ideas; build ideas 1 and 3 under those tickets.

The advisor's write-up, verbatim:

### Agents defeat --expect by computing it from the file at write time

#### What happened (2026-10-08, notes root, advisor session)

1. 06:22 EDT: listed the open Kings Island tasks with line numbers:

       grep -n '^- \[ \]' project/2026-10-kings-island/Home.md
       # 125: Josiah and Judah's answers ... #wait 📅 2026-10-08
       # 127: Buy day tickets or passes ... 📅 2026-10-08
       # 133: Plan the Kings Island day ... 📅 2026-10-10

2. Right after, inserted three lines into the note's `## Weather` section with a Python str.replace (prose, no CLI). Every line below moved down 3.

3. 07:09: the human asked to move the tasks to Friday. I reused the stale numbers and built --expect from the file itself:

       for n in 125 127 133; do
         meta-notes task update "$P:$n" --expect "$(sed -n ${n}p $P)" --due 2026-10-09
       done

   Result:
       Error: Line 125 of project/2026-10-kings-island/Home.md is not a checkbox
       + - [x] Text Josiah and Judah again: do they want the mazes? #next 📅 2026-10-09
       Error: Line 133 of project/2026-10-kings-island/Home.md is not a checkbox

   Line 127 was now a DONE task; its due date changed 2026-10-05 -> 2026-10-09. --expect matched because it was read from that same line a moment earlier. The CLI behaved correctly; the check was defeated by its input. Caught only because two of three lines happened not to be checkboxes. Fixed by hand (re-queried, restored 2026-10-05, moved the right three).

#### The pattern, used all session (it "worked" only by luck)

Look up the line by a pattern, then feed sed of that line as --expect:

    n=$(grep -n "Deposit the dental check" "$W" | cut -d: -f1)
    meta-notes task update "$W:$n" --expect "$(sed -n ${n}p "$W")" --status x

    n=$(grep -n "Bedtime checklist.*2026-10-07" $H | cut -d: -f1) && \
      meta-notes task update "$H:$n" --expect "$(sed -n ${n}p $H)" --status x

    # line from an earlier `tasks --json` query, expect from sed:
    meta-notes task update area/work-desk/Home.md:87 \
      --expect "$(sed -n 87p area/work-desk/Home.md)" --status x

    # several in one go:
    for pat in "Order melatonin" "Order Tiffany's watch band"; do
      n=$(grep -n "$pat" "$R" | cut -d: -f1)
      meta-notes task update "$R:$n" --expect "$(sed -n ${n}p "$R")" --time 20:00
    done

Extra hazards: if grep matches two lines, $n is "12\n40" and the command is garbage; grep matches non-task lines and copies (Tasks Due Today blocks); nothing ties the grep to what I actually read or showed the human.

#### Related: silent no-op prose edits (2026-10-07)

Notes-section lines (not tasks, no CLI) were added with Python:

    s=s.replace("  all the way home (update 8:59 AM), so no pickup at work.\n\n## Worked On", ...)

The note wrapped as "Zeal's violin ...; he's with Mom, who's bringing him all\n  the way home ...", so the match text never occurred; three edits wrote nothing, reported nothing, and were committed as if done. Found 12 hours later. Since then the script asserts `s.count(key)==1`. There's no CLI for "append a bullet to ## Notes" / "add a line to section X", so agents hand-roll these.

#### Why the agent reaches for sed (the friction)

- --expect needs the whole task line exactly, including "- [ ] ", emoji, dates and the ✅ stamp. Retyping it in a shell argument is error-prone: apostrophes ("Tiffany's", "Wednesday night's"), emoji, 📅/⏰ spacing.
- The natural agent loop is "find, then act" in one command. --expect wants "what you read earlier", which is awkward when the read and write are in the same Bash call.
- `task update <file> --expect <text>` without a line number exists and is the safer form, but still needs the full exact text.
So the safe path is harder than the unsafe one; the unsafe one passes every check.

#### Ideas to analyze (none decided)

1. Revision token (optimistic concurrency, like an ETag): `tasks --json` returns a per-task `rev` (hash of the line plus file identity/version); `task update <file> --rev <rev> ...` refuses if stale. Can't be reproduced with sed at write time without deliberate effort. Possibly stable task ids too.
2. Match by a unique substring: `task update <file> --match 'Deposit the dental check' --status x` (refuses if 0 or >1 tasks match; prints the line it changed). Easy to type, no line numbers. Doesn't protect against concurrent edits but removes the reason to use sed.
3. Guard hook: refuse a meta-notes command whose --expect contains `$(` or backticks, pointing to the rule (approved by the human, m-0127).
4. Prose editing: `meta-notes note append <file> --section Notes --text ...` (and maybe `--after`), so Notes/Worked On lines stop being hand-rolled; it would fail loudly if the section is missing.
5. The human is considering blocking agents' direct read access to notes so everything goes through the CLI ("this wouldn't happen as easily in a database"), but that's a lot of work; worth weighing against 1-4.

Interim: notes rule `.bridle/rules/expect-what-you-read.md` (never compute --expect from the file; prefer text over line numbers; re-query after any write; verify hand edits).

## The human, 2026-10-08 (via the notes advisor, relayed by the meta-notes aide as m-0717)

On blocking read access:

> when I say blocking read access, obviously there would still be a way
> to read, but the reading and writing would all go through the CLI, and
> that would prevent some of these manipulations, because sed would just
> not work.

On fixing it with an agent rule:

> I'm not sure I want that rule yet ... it's also going to depend on the
> agent following the rule, which I am not convinced is the right way to
> fix this.

> I want to continue to explore this with that ticket instead of making a
> quick change ... The problem with the rule is it only fixes it in this
> bridle repo, and I need this fixed in meta notes. Also for my work repo,
> which doesn't use bridle at all.

So the fix has to live in meta-notes itself and work in a notes root
without bridle; an agent rule (or a bridle-only hook) isn't the fix. The
notes rule `expect-what-you-read` was reverted at the human's request.
