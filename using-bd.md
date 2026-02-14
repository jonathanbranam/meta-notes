# Using BD (Beads) - Issue Tracker

BD is a lightweight issue tracker with first-class dependency support. Issues are chained together like beads on a string.

## Basic Workflow

### Finding Work

```bash
# Show ready work (open issues with no blockers)
bd ready

# Search for specific issues
bd search "keyword"

# List all issues (default shows 50)
bd list

# List with filters
bd list --status open
bd list --type task
bd list --priority P2
```

### Working with Issues

```bash
# Show issue details
bd show <issue-id>

# Close an issue with a message
bd close <issue-id> -m "Description of what was done"

# Close multiple issues at once
bd close <id1> <id2> <id3> -m "Completion message"

# Defer an issue for later
bd defer <issue-id>

# Undefer an issue
bd undefer <issue-id>
```

### Comments

```bash
# List comments on an issue
bd comments <issue-id>

# Add a comment
bd comments add <issue-id> "Comment text here"
```

### Issue Types

BD supports several issue types:
- `task` - A specific task to complete
- `epic` - A collection of related tasks
- `feature` - A new feature request
- `bug` - A bug to fix
- `chore` - Maintenance work

### Useful Flags

- `--json` - Output in JSON format
- `-v, --verbose` - Enable verbose/debug output
- `-q, --quiet` - Suppress non-essential output

## Tips

1. **Start with `bd ready`** - This shows you what's ready to work on
2. **Close issues with descriptive messages** - Use `-m` flag to document what was done
3. **Search before creating** - Use `bd search` to avoid duplicates
4. **Use comments for updates** - Add comments for status updates or questions
5. **Check the parent epic** - Use `bd show` to understand context and dependencies

## Integration with Git

BD can be configured to auto-sync with git. Issues are stored in `.beads/*.jsonl` files.

```bash
# Sync database to JSONL (prepare for git commit)
bd sync

# Use git hooks for automatic sync
bd hooks
```
