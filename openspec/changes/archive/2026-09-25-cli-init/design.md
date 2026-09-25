## Context

`meta_notes#notes#Init` in `autoload/meta_notes/notes.vim` creates 13
folders and writes four templates from Vimscript list literals, echoing one
line per item ("Created directory: …", "Template already exists: …",
"Overwrote template: …") and a final "Meta-notes initialization complete!".
`test/init.vader` checks folders, template headings, idempotence, and `!`.

cli-core left `scripts/meta_notes/cli.py` resolving the root in `_run()`
before any handler runs: `--root`, then `META_NOTES_ROOT`, then a walk to the
filesystem root looking for `plan/`, `project/`, and `area/`
(`is_notes_root`). `meta_notes#cli#Run` always passes `--root getcwd()
--json`. pytest fixtures and vader tests run in temp directories outside
`$HOME` (`/var/folders/...`, `/private/tmp/...`).

The plugin ships one skill, `skills/project-review/SKILL.md`. The notes root
is a git repo, and the plugin usually lives elsewhere (often another volume).

See proposal.md for motivation and specs/ for required behavior.

## Goals / Non-Goals

**Goals:**
- One implementation of init, in the CLI, reachable from shell and Vim
- A single, bounded upward search shared by root resolution and init's
  nesting check
- Template files byte-identical to what Vim writes today

**Non-Goals:**
- Sentinel contents beyond a marker (no config file yet)
- Relative skill links or `.gitignore` handling
- Removing skills the plugin no longer ships
- Upgrading templates in place, or detecting user edits to them

## Decisions

### 1. Module layout

New `scripts/meta_notes/init.py` holds `init(target, force) -> InitResult`
and the skill-link logic. The bounded search goes in a new
`scripts/meta_notes/root.py` (`find_root(start, home)`), used by both
`cli.resolve_root` and `init`. `is_notes_root` and `ROOT_MARKERS` are
removed; nothing else uses them.

**Why a separate `root.py`:** the search is now shared by two callers with
different start points, and it is the part with the subtle rules
(permissions, `$HOME`), so it gets its own tests.

### 2. Bounded upward search

```
find_root(start, home):
    d = realpath(start)
    home = realpath(home) if home else None
    loop:
        if not os.access(d, R_OK | W_OK | X_OK): return None
        try: if os.path.isfile(join(d, ".meta-notes")): return d
        except OSError: return None
        if d == home: return None
        parent = dirname(d)
        if parent == d: return None
        d = parent
```

- `os.access` plus a single `isfile` per directory: no `listdir`, no
  `scandir`, so no reads of directory contents and nothing to raise on
  unreadable siblings.
- Both paths go through `realpath` so `$HOME` compares correctly when either
  side involves a symlink (`/var` → `/private/var` on macOS). The start is
  checked before anything above it, so a sentinel in the start directory
  always wins.
- `home` comes from `os.environ.get("HOME")`. If unset, there is no `$HOME`
  stop; the permission stop still bounds the walk, because system
  directories aren't user-writable.
- Outside `$HOME` the walk continues until the permission stop. On this
  machine that is `/Volumes` for `/Volumes/Data/...`.

**Alternatives considered:** a mount-point stop (`os.path.ismount`) was
dropped as redundant with the permission stop. Searching for `.git` was
rejected: a git repo isn't necessarily a notes root.

### 3. Sentinel file

`.meta-notes` is a small text file:

```
# meta-notes notes root. Created by `meta-notes init`; keep and commit it.
```

Only its existence matters (`isfile`). Init never rewrites an existing one,
even with `--force`, so later changes can store settings in it without init
clobbering them.

### 4. Init bypasses root resolution

`build_parser` sets `resolves_root=True` by default and `False` on the
`init` subparser. `_run` calls `resolve_root` and `chdir` only when it is
true; otherwise the handler gets `root=None`. `cmd_init` computes the target
as `abspath(expanduser(--root))` or `os.getcwd()`, ignoring
`META_NOTES_ROOT`.

**Nesting check before any write:** start the search at the nearest
*existing* ancestor of the target's parent. A missing directory would fail
`os.access` and end the search early, so for `--root a/b/c` where only `a/`
exists, the search starts at `a/`. If it finds a root, fail with
`Cannot initialize inside existing notes root: <root>`. The target's own
sentinel is never checked by this search, so re-running is allowed.

Then `os.makedirs(target, exist_ok=True)`, `chdir` into it, and create items
in a fixed order: folders (today's order), templates, sentinel, skills.
`OSError` becomes a `CliError` with the path and reason.

### 5. Templates as shipped files

Templates move to `templates/{daily,weekly,quarterly,yearly}.md` at the
plugin root. Init copies bytes (`shutil.copyfile`), so the Python side never
reformats content. The files are generated once from the current Vimscript
lists using Vim's own `writefile()` (LF line endings, trailing newline),
which guarantees identity with today's output; a pytest compares the four
files against fixtures captured the same way before the Vimscript is
removed.

`--force` overwrites all four. Without it, an existing file is left alone
regardless of content.

**Why `templates/` rather than `resource/`:** it sits next to `skills/` as
another thing the plugin ships, and avoids confusion with the notes root's
own `resource/template/`.

### 6. Plugin location and skill links

`init.py` finds the plugin root as `Path(__file__).resolve().parents[2]`
(`scripts/meta_notes/init.py` → plugin). `resolve()` follows symlinks, so a
plugin installed by symlink (`~/.vim/pack/.../meta-notes`) links skills to
the real checkout, matching how `bin/meta-notes` resolves itself.

A skill is a directory under `skills/` containing `SKILL.md`. For each, the
expected link is `<root>/.claude/skills/<name>` → absolute
`<plugin>/skills/<name>`.

| Found at target | Without `--force` | With `--force` |
|---|---|---|
| nothing | create link (`created`) | same |
| link, `realpath` equals expected | leave (`exists`) | same |
| link elsewhere or broken | replace link (`repointed`) | same |
| real file or directory | leave, warn (`skipped`) | remove, link (`replaced`) |

"Correct" compares `realpath` of both sides, so a relative link that
reaches the same directory counts as correct. Replacing a link uses
`os.remove`, never `rmtree`; only the `--force` real-directory case uses
`shutil.rmtree`.

**Why absolute links:** notes and plugin are usually on different paths
(often different volumes), and a relative link breaks when either moves. An
absolute link committed from one machine points to the wrong place on
another; re-running init repoints it (see Risks).

### 7. Output

JSON adds `root` (absolute) and `items`, one per folder, template, sentinel,
and skill, in creation order:

```json
{"ok": true, "root": "/…/notes",
 "items": [{"kind": "folder", "path": "plan", "status": "created"}, …,
           {"kind": "skill", "path": ".claude/skills/project-review",
            "status": "skipped"}],
 "warnings": [".claude/skills/project-review exists and is not a link; left alone (use --force to replace)"]}
```

`status` is one of `created`, `exists`, `overwritten`, `repointed`,
`skipped`, `replaced`. Text output prints one line per item using the same
wording Vim shows (Decision 8), then `Meta-notes initialization complete!`.

### 8. Vim caller

`meta_notes#notes#Init(force)` calls
`meta_notes#cli#Run(['init'] + (force ? ['--force'] : []))`. On failure it
`echoerr`s the error, like `file_ops`. On success it echoes each item:

| kind / status | Message |
|---|---|
| folder created / exists | `Created directory: X` / `Directory already exists: X` |
| template created / overwritten / exists | `Created template: X` / `Overwrote template: X` / `Template already exists: X` |
| sentinel created / exists | `Created notes root marker: .meta-notes` / `Notes root marker already exists: .meta-notes` |
| skill created / exists / repointed / replaced | `Linked skill: X` / `Skill already linked: X` / `Relinked skill: X` / `Replaced with skill link: X` |

Skipped skills are shown through `meta_notes#cli#ShowWarnings`. Then
`Meta-notes initialization complete!`.

One deliberate difference: today `:MetaNotesInit!` says "Overwrote template"
even for a template it just created; the CLI reports `created` in that case.
No vader test depends on it.

## Risks / Trade-offs

- [Existing roots have no sentinel, so shell commands without `--root` stop
  finding them] → The error says to run `meta-notes init`; Vim always passes
  `--root` and is unaffected. Docs call out the one-time step.
- [Absolute skill links committed to git break on another machine] → Re-run
  `meta-notes init` there; a broken or foreign link is repointed. `.gitignore`
  handling stays out of scope.
- [Permission stop depends on the OS: a user-writable directory above the
  notes root (e.g. `/Volumes/Data`) is still searched] → Only a `stat` of one
  file per directory; bounded by the first non-writable ancestor.
- [`os.access` checks real, not effective, IDs and ignores ACL subtleties] →
  Acceptable for a single-user tool; a wrong answer only ends the search
  early or lets it check one more directory.
- [`--force` deletes a real directory at a skill target] → Only with
  `--force`, only at `.claude/skills/<shipped name>`, and the spec states it.
- [Template parity drift during the move] → Files generated by Vim's own
  `writefile`, pinned by a byte-comparison test, and `test/init.vader` kept.
- [Tests that exercised the marker walk] → `test_cli.py` root-walk tests are
  rewritten for the sentinel and set `HOME` explicitly so they don't depend
  on where `tmp_path` lives.

## Migration Plan

1. Add `root.py` and switch `resolve_root` to it; update `test_cli.py`.
2. Generate `templates/*.md` from the Vimscript and add the parity test.
3. Add `init.py` and the `init` subcommand with tests.
4. Switch `meta_notes#notes#Init` to the CLI; run `test/init.vader`.
5. Remove the Vimscript template lists and folder loop.
6. Update README, `doc/meta-notes.txt`, and `docs/planning-system.md` if it
   describes root discovery.
7. Run `meta-notes init` once in each existing notes root and commit the
   sentinel.

Rollback is reverting the commit; an added `.meta-notes` and
`.claude/skills/` links in a notes root are harmless to older versions.
