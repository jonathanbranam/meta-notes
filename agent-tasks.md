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

**List all tasks:**
```bash
bd list
```

**List ready tasks (unblocked):**
```bash
bd ready
```

**Search tasks:**
```bash
bd q "search term"
```

**View specific task:**
```bash
bd show <task-id>
```

### Creating Tasks

**Create a single task:**
```bash
bd add "Task description"
```

**Create task with metadata:**
```bash
bd add "Task description" --priority P2 --type task --epic epic-id
```

### Updating Tasks

**Mark task as started:**
```bash
bd start <task-id>
```

**Mark task as done:**
```bash
bd done <task-id>
```

**Add dependencies:**
```bash
bd block <blocker-id> <blocked-id>
```

### Syncing Changes

**Before pushing to git:**
```bash
bd sync
```

This command:
1. Exports the SQLite database to JSONL files
2. Ensures all changes are persisted to git-tracked files
3. Resolves any conflicts between database and JSONL

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

# Start a task
bd start <task-id>

# Create new tasks as needed
bd add "New task discovered during work"
```

### 3. Session End
```bash
# Mark completed tasks
bd done <task-id>

# Sync before committing
bd sync

# Git workflow
git add .beads/
git commit -m "Update beads - completed X tasks"
git push
```

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `bd list` | List all tasks |
| `bd ready` | List unblocked tasks ready to work on |
| `bd q <query>` | Search tasks by keyword |
| `bd show <id>` | Show task details |
| `bd add <desc>` | Create new task |
| `bd start <id>` | Mark task as in-progress |
| `bd done <id>` | Mark task as completed |
| `bd block <blocker> <blocked>` | Add dependency |
| `bd sync` | Sync database to JSONL files |
| `bd prime` | Load context for AI session |
| `bd status` | Show repository status |
| `bd help` | Show all available commands |

## Best Practices

1. **Always sync before pushing**: Run `bd sync` before committing changes
2. **Use meaningful descriptions**: Make task descriptions clear and actionable
3. **Track dependencies**: Use `bd block` to model task relationships
4. **Update status regularly**: Mark tasks as started/done to keep state accurate
5. **Commit task changes**: The `.beads/` directory should be tracked in git
6. **Let hooks work**: The SessionStart hook automatically primes context
7. **Use no-db mode for ephemeral environments**: Enable `no-db: true` in config.yaml for containerized or web-based environments to avoid SQLite WAL issues

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
