# Agent Task Management with Beads

This document explains how to use the Beads CLI (`bd`) for task management in AI-assisted development sessions.

## What is Beads?

Beads is a git-backed issue tracker designed specifically for AI-supervised coding workflows. It provides:
- **Persistent memory** across AI sessions
- **Dependency-aware** task graphs
- **Version-controlled** task database (stored in `.beads/`)
- **AI-first design** with JSON output and semantic commands

Created by Steve Yegge, beads acts as a "memory upgrade" for coding agents.

## Installation

### Quick Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
```

### Alternative Methods

**Homebrew (macOS/Linux):**
```bash
brew install beads
```

**Go Install:**
```bash
go install github.com/steveyegge/beads/cmd/bd@latest
```

**Windows 11 (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/steveyegge/beads/main/install.ps1 | iex
```

### Verify Installation

```bash
bd version
```

You should see output like: `bd version 0.49.6`

## 🚨 SESSION CLOSE PROTOCOL 🚨

**CRITICAL**: Before saying "done" or "complete", you MUST run this checklist:

```
[ ] 1. git status              (check what changed)
[ ] 2. git add <files>         (stage code changes)
[ ] 3. bd sync                 (commit beads changes)
[ ] 4. git commit -m "..."     (commit code)
[ ] 5. bd sync                 (commit any new beads changes)
[ ] 6. git push                (push to remote)
```

**NEVER skip this.** Work is not done until pushed.

## Project Setup

### Initialize Beads in Repository

**Standard initialization (uses SQLite):**
```bash
cd /path/to/your/project
bd init --quiet
```

**For ephemeral/containerized environments (no SQLite):**
```bash
cd /path/to/your/project
bd init --no-db --quiet
```

This creates a `.beads/` directory with:
- `issues.jsonl` - Task database (tracked in git)
- `interactions.jsonl` - Session history (tracked in git)
- `config.yaml` - Configuration (tracked in git)
- `beads.db` - SQLite database (ignored by git, not created with `--no-db`)
- `.gitignore` - Ignores ephemeral files

**Note:** If you encounter SQLite WAL locking errors after initialization, see the [Troubleshooting](#troubleshooting) section to enable no-db mode.

### Setup Claude Code Integration

```bash
bd setup claude
```

This registers hooks in `~/.claude/settings.json`:
- **SessionStart** - Runs `bd prime` at the start of each session
- **PreCompact** - Runs `bd prime` before conversation compression

## Using Beads in Every Session

### Session Start (Automatic)

When a Claude Code session starts, the `SessionStart` hook automatically runs:
```bash
bd prime
```

This command:
1. Loads relevant tasks into the AI context
2. Identifies "ready" tasks (unblocked dependencies)
3. Provides session-specific context

### Manual Priming (Optional)

If you need to refresh task context mid-session:
```bash
bd prime
```

### Viewing Tasks

**List all open tasks:**
```bash
bd list --status=open
```

**List tasks in progress:**
```bash
bd list --status=in_progress
```

**List ready tasks (unblocked):**
```bash
bd ready
```

**Show blocked issues:**
```bash
bd blocked
```

**View specific task:**
```bash
bd show <task-id>
```

**List children of an epic:**
```bash
bd children <epic-id>
```

### Creating Tasks

**Create a single task:**
```bash
bd create --title="Task description" --type=task --priority=2
```

**Create task with other types:**
```bash
bd create --title="Fix bug" --type=bug --priority=0
bd create --title="New feature" --type=feature --priority=2
```

**Note on priority:** Use 0-4 or P0-P4 (0=critical, 2=medium, 4=backlog). NOT "high"/"medium"/"low".

### Creating Epics and Child Issues

**Create a parent epic:**
```bash
bd create --title="Epic name" --type=epic -d "Long description" --priority=2
```

**Create child issues of the epic:**
```bash
bd create --title="Child task" --type=task -d "Long description" --parent=<epic-id> --priority=2
bd create --title="Child feature" --type=feature -d "Long description" --parent=<epic-id> --priority=2
bd create --title="Child bug fix" --type=bug -d "Long description" --parent=<epic-id> --priority=1
```

**View epic and its children:**
```bash
bd show <epic-id>           # Shows the epic and all child issues
bd children <epic-id>       # Lists all child issues
```

**Note:** Use epics and child issues for organizing related work instead of `bd dep add` for simple parent-child relationships.

### Updating Tasks

**Mark task as in-progress:**
```bash
bd update <task-id> --status=in_progress
```

**Assign task:**
```bash
bd update <task-id> --assignee=username
```

**Update task fields:**
```bash
bd update <task-id> --title="New title"
bd update <task-id> --description="New description"
```

**Mark task as done:**
```bash
bd close <task-id>
```

**Close multiple tasks at once (more efficient):**
```bash
bd close <task-id1> <task-id2> <task-id3>
```

**Close with reason:**
```bash
bd close <task-id> --reason="explanation"
```

**Add dependencies:**
```bash
bd dep add <issue-id> <depends-on-id>
```

Note: This means `<issue-id>` depends on `<depends-on-id>` (i.e., `<depends-on-id>` blocks `<issue-id>`)

### Syncing Changes

**Before pushing to git:**
```bash
bd sync
```

This command:
1. Exports the SQLite database to JSONL files
2. Ensures all changes are persisted to git-tracked files
3. Resolves any conflicts between database and JSONL

**Check sync status without syncing:**
```bash
bd sync --status
```

## Workflow Integration

### 1. Session Start
```bash
# Automatic via SessionStart hook
bd prime
```

### 2. During Development
```bash
# View what to work on
bd ready

# Review issue details
bd show <issue-id>

# Claim a task
bd update <issue-id> --status=in_progress

# Create new tasks as needed
bd create --title="New task discovered during work" --type=task --priority=2
```

### 3. Session End
```bash
# Mark completed tasks (can close multiple at once)
bd close <issue-id1> <issue-id2> <issue-id3>

# Sync before committing
bd sync

# Git workflow
git add .beads/
git commit -m "Update beads - completed X tasks"
git push
```

### Organizing Related Work with Epics
```bash
# Create parent epic
bd create --title="Feature X Implementation" --type=epic -d "Complete implementation of feature X with tests and documentation" --priority=2

# Create child tasks under the epic
bd create --title="Implement feature X core" --type=feature -d "Core implementation" --parent=<epic-id> --priority=2
bd create --title="Write tests for feature X" --type=task -d "Unit and integration tests" --parent=<epic-id> --priority=2
bd create --title="Document feature X" --type=task -d "User documentation" --parent=<epic-id> --priority=2

# View all children of the epic
bd children <epic-id>
```

**Note:** For complex dependencies between unrelated tasks, use `bd dep add <issue> <depends-on>`.

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `bd list --status=open` | List all open tasks |
| `bd list --status=in_progress` | List tasks in progress |
| `bd ready` | List unblocked tasks ready to work on |
| `bd blocked` | Show all blocked issues |
| `bd show <id>` | Show task details with dependencies and children |
| `bd create --title="..." --type=task --priority=2` | Create new task |
| `bd create --title="..." --type=epic -d "..." --priority=2` | Create new epic |
| `bd create --title="..." --type=task --parent=<epic-id>` | Create child task under epic |
| `bd children <epic-id>` | List all child issues of an epic |
| `bd update <id> --status=in_progress` | Mark task as in-progress |
| `bd update <id> --assignee=username` | Assign task to someone |
| `bd close <id>` | Mark task as completed |
| `bd close <id1> <id2> ...` | Close multiple tasks at once |
| `bd dep add <issue> <depends-on>` | Add dependency for complex cross-epic dependencies |
| `bd sync` | Sync database to JSONL files |
| `bd prime` | Load context for AI session |
| `bd stats` | Project statistics (open/closed/blocked counts) |
| `bd doctor` | Check for issues (sync problems, missing hooks) |

## Best Practices

1. **Use beads for ALL task tracking**: Use `bd create`, `bd ready`, `bd close` - do NOT use TodoWrite, TaskCreate, or markdown files for task tracking
2. **Create beads issue BEFORE writing code**: Mark in-progress when starting with `bd update <id> --status=in_progress`
3. **Always sync before pushing**: Run `bd sync` before committing changes
4. **Use meaningful descriptions**: Make task descriptions clear and actionable with `-d "Long description"`
5. **Organize with epics**: Use `--type=epic` for parent issues and `--parent=<epic-id>` for child tasks - simpler than `bd dep add` for related work
6. **Track complex dependencies**: Use `bd dep add` only for complex cross-epic dependencies, prefer epics for simple parent-child relationships
7. **Update status regularly**: Mark tasks as in-progress/closed to keep state accurate
8. **Close multiple tasks efficiently**: Use `bd close <id1> <id2> ...` to close multiple issues at once
9. **Commit task changes**: The `.beads/` directory should be tracked in git
10. **Let hooks work**: The SessionStart hook automatically primes context
11. **Use no-db mode for ephemeral environments**: Enable `no-db: true` in config.yaml for containerized or web-based environments to avoid SQLite WAL issues
12. **Do NOT use `bd edit`**: It opens $EDITOR (vim/nano) which blocks agents - use `bd update` with inline flags instead
13. **Use correct priority format**: 0-4 or P0-P4 (0=critical, 2=medium, 4=backlog), NOT "high"/"medium"/"low"

## Claude Code on the Web

Claude Code for Web provides ephemeral Linux VM sandboxes. Each session is a fresh environment, which can cause issues with SQLite's Write-Ahead Logging (WAL) mode.

### Recommended Setup

1. **Use no-db mode** to avoid filesystem compatibility issues:
   ```yaml
   # In .beads/config.yaml
   no-db: true
   issue-prefix: "your-project"
   ```

2. **SessionStart hook** will automatically install bd and load context

3. **All state persists** via git-tracked JSONL files

### Why no-db Mode for Web Sessions?

- Ephemeral VMs may have filesystem restrictions that prevent WAL mode
- JSONL-only operation is more reliable in containerized environments
- No performance penalty in web sessions (network is the bottleneck)
- State persists perfectly via git since JSONL files are the source of truth

## Troubleshooting

### WAL (Write-Ahead Logging) Locking Issues

If you encounter SQLite locking protocol errors (common in containerized environments like Claude Code on the web):

**Error message:**
```
Error: failed to open database: failed to enable WAL mode: sqlite3: locking protocol
```

**Solution - Enable no-db mode:**

1. Edit `.beads/config.yaml`:
   ```yaml
   # Enable no-db mode (use JSONL only, bypass SQLite)
   no-db: true

   # Set issue prefix explicitly
   issue-prefix: "your-project-name"
   ```

2. Verify it works:
   ```bash
   bd list
   bd status
   ```

**What is no-db mode?**
- Bypasses SQLite entirely, works directly with JSONL files
- Perfect for ephemeral environments (Docker, Claude Code web, CI/CD)
- Slightly slower than SQLite but avoids filesystem compatibility issues
- JSONL files remain the source of truth (git-tracked)

**Alternative: Use flags instead of config**
```bash
bd --no-db list
bd --no-db ready
bd --sandbox --no-db create --title="Task name"
```

### Other Issues

**Daemon issues:**
```bash
bd doctor
```

**Database locked (SQLite mode only):**
```bash
bd sync --force
```

**Reset database from JSONL (SQLite mode only):**
```bash
rm .beads/beads.db
bd status  # Rebuilds from JSONL
```

## Resources

- **GitHub**: https://github.com/steveyegge/beads
- **Installing**: https://github.com/steveyegge/beads/blob/main/docs/INSTALLING.md
- **Introduction**: https://steve-yegge.medium.com/introducing-beads-a-coding-agent-memory-system-637d7d92514a
- **Best Practices**: https://steve-yegge.medium.com/beads-best-practices-2db636b9760c
