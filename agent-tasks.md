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

```bash
cd /path/to/your/project
bd init --quiet
```

This creates a `.beads/` directory with:
- `issues.jsonl` - Task database (tracked in git)
- `interactions.jsonl` - Session history (tracked in git)
- `config.yaml` - Configuration (tracked in git)
- `beads.db` - SQLite database (ignored by git)
- `.gitignore` - Ignores ephemeral files

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

## Troubleshooting

**Daemon issues:**
```bash
bd doctor
```

**Database locked:**
```bash
bd sync --force
```

**Reset database from JSONL:**
```bash
rm .beads/beads.db
bd status  # Rebuilds from JSONL
```

## Resources

- **GitHub**: https://github.com/steveyegge/beads
- **Installing**: https://github.com/steveyegge/beads/blob/main/docs/INSTALLING.md
- **Introduction**: https://steve-yegge.medium.com/introducing-beads-a-coding-agent-memory-system-637d7d92514a
- **Best Practices**: https://steve-yegge.medium.com/beads-best-practices-2db636b9760c
