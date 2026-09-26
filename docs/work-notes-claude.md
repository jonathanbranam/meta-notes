# Overview

This is my note-taking and planning system which uses the PARA method of folder
organization. PARA is:

- project/ -> stores active projects
- area/ -> notes on domain areas that I am responsible for
- resource/ -> informational notes that don't involve personal responsibility
- archive/ -> internally contains PAR: inactive projects, inactive areas, and
  old resources

# Planning

## Daily Notes

I start a daily note in "resource/daily-notes" folder using the template file
"Daily Note Template.md". This is a holder for my daily time block plan and
planning and tracking daily notes and tasks. Notes and tasks that are associated
with projects, areas, or resources should be filed in those folders and linked
from the daily note when I update them.

### Time Tracking

#### Log

The first section in Time Tracking is my log of what I actually did during any
block of time. Each log item starts with a single bullet that gives a name to
the main effort during the time. Tags can be added for organization with a hash
mark "#". These tags are used by my time log Python script to report on how I
spent my time throughout the day.

Important tags are:

- #meeting -> every Zoom meeting has this tag
- #personal -> personal time outside of work responsibilities
- #break -> non-work time where I take a small break to refresh
- #recruiting -> interviewing and recruiting efforts
- #admin -> various non-productive admin tasks
- #1-1 -> a 1-1 meeting with someone. Will also have the #meeting tag
- #plan -> planning activities

#### Time Block

This section is where I plan my available time in a table format. This approach
is called Time Blocking and was introduced to me by Cal Newport. The table
divides the day into 15 min increments and I attempt to give each block a task.
The "Plan" column indicates what I planned to do during that time and the
"Actual" column indicates what I actually did. The "Actual" column and the time
log duplicate the same information, but the Actual column is a very short
summary.

When planning my day, I usually start my day at 8am and end by 5pm. Do not plan
any work activities after 5pm. I will add any meetings to the time block myself
and any planned personal time. Do not replace these when making a plan. I
typically eat make and lunch at my desk at 11:30am, and I will eat during a
meeting if it is primarily an informational meeting where I don't have to
participate heavily. I like to take several breaks during my day where I get
some light exercise such as taking a walk, doing pushups, squats, or curls.

At the end of every work day, I should have a 15 min block for my "shutdown
routine" where I review what I accomplished, update my plan and file any notes,
and make any notes for the following day.

### Daily Reflection / Shutdown

Every day should end with a daily reflection and shutdown procedure.

## Weekly Plan

I also make a weekly plan in the "resource/plan/week" folder with a name for
the Monday of that week such as "Plan %Y-%m-%d.md" This plan should outline what
I want to accomplish at a high level for each of my current projects and note
any important deadlines or time commitments that I have on each day. The weekly
plan should be referenced when making a daily plan to ensure that I have time to
complete the plan every week.

### Weekly Reflection

Every week should end with 30-60 min of reflection on the week and planning for
the following week. Important milestones should be noted and added to my
quarterly list of accomplishments, incomplete tasks and projects should be noted
and scheduled for the following week, and I should review my calendar for the
following week to determine my overall availability and the amount of productive
time that I have as well as any administrative deadlines.

At the end of every week I should also:

- submit any pending expenses
- complete any pending CBTs (required quarterly trainings)
- review and clean up my list of open tasks
- review my list of projects to ensure it is up to date
- update all projects with current status
- write a status update for every project to share with my manager
- go through my open tabs and close them, adding bookmarks or links for
  important sites
- go through my Slack list of "saved for later" items and either remove them or
  move them to a note or task for later follow up

# Projects

Active projects are listed in "project/Project List.md". Each project has a link
to the project folder or project note. Large projects have a folder dedicated to
them. Shorter projects keep everything in a single note.

A project is a short-term effort that I am working on right now. When a project
is complete, it should be moved to the "archive" folder and moved from
"project/Project List.md" to "project/Project History.md" in the proper section
and with a note about the project.

## Project Home

A large project has a "project/name/Home.md" note that organizes key information
about the project such as links to other notes and external links to key
documents, important people and deadlines, etc. This note should be short enough
to skip quickly and most information is in other files.

## Project Meetings & Notes

A project should also have a "Tasks.md" file containing the next tasks to be
done for the project. Completed tasks will be marked off following the task
system described below and may be moved to a "Completed" section of the file for
easier visibility into current tasks.

## Project Planning

A large project will have a "project/name/Planning.md" project where thoughts
and notes about project planning are kept. The file should be organized in
reverse chronological order by date using a markdown header such as "### Daily
Plan 2026-01-22 Thu" or "## Weekly Plan 2026-01-19 Mon" for each section. Weekly
plans should also be summarized in the overall weekly plan document described
below.

# Tasks

A task can be created in any notes file and will be found by my search program.
A task begins with a bullet symbol such as "-", "\*", or "+", a space, then
square brackets "[ ]". A space inside the brackets indicates the task is
incomplete. An "x" or "X" inside the brackets indicates completion. A dash
symbol "-" inside the square brackets indicates that the task was canceled. A
greater than sign ">" indicates that the task was rescheduled or moved somewhere
else in notes. Any other character inside the brackets indicates partial
completion such as "o" or "/".

A task can have tags listed beginning with a hash mark "#" on the same line or
subsequent, indented lines. A task can also have a due date indicated by the
emoji calendar symbol "📅" and a start date indicated by the emoji airplane take
off symbol "🛫". Completed tasks may optionally have a completion date added to
the task line or an indented sub-bullet point using the green check mark emoji
"✅" and the date.

# Explanation of PARA

## Project

These are short-term efforts that I am working on right now. When a project is
complete, it should be moved to the "archive" folder. If a project is ongoing
for a long time, it may need to be converted into an area. A large project will
contain a "Home.md" file that organizes links to related files. It will also
contain a "Meetings & Notes.md" file that keeps a reverse-chronological sorting
of meeting notes and other adhoc notes.

A project should also have a "Tasks.md" file containing the next tasks to be
done for the project.

## Area

An area is a long-term responsibility that I want to manage over time. Areas may
have projects within them and can reference out to a short-term project as
needed. Resources may also be associated with a particular area and should be
linked.

## Resource

Resources are reference material for topics that I want to keep and use in the
future. Resources may be directly related to projects or areas or may not. I
keep meeting notes for general meetings in the resource area.

# Note Files and Folder Naming

- folders should be named using dashes instead of spaces
- folders should be all lowercase
- notes should be named using Title Case and use spaces, ending in .md
- notes should be written in markdown
- other file types can be included in a notes folder as necessary for reference
  such as JSON, CSV, and images

