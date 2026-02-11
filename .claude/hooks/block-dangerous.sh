#!/bin/bash
# Hook: Block dangerous/destructive shell commands
# Catches commands that could destroy files, wipe git history, or corrupt the database.
#
# How it works:
# - Reads the Bash command from JSON stdin
# - Matches against known dangerous patterns
# - Exit 0 = allow, Exit 2 = block

COMMAND=$(jq -r '.tool_input.command' < /dev/stdin)

# Pattern 1: Recursive force delete (rm -rf /)
if echo "$COMMAND" | grep -qE 'rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+|.*-rf\s+)/'; then
  echo "BLOCKED: Recursive force delete on root path." >&2
  exit 2
fi

# Pattern 2: Destructive git commands
if echo "$COMMAND" | grep -qE 'git\s+reset\s+--hard'; then
  echo "BLOCKED: git reset --hard discards all uncommitted changes." >&2
  echo "Use 'git stash' to save changes first, or 'git reset --soft' to keep them staged." >&2
  exit 2
fi

if echo "$COMMAND" | grep -qE 'git\s+clean\s+-[a-zA-Z]*f'; then
  echo "BLOCKED: git clean -f permanently deletes untracked files." >&2
  echo "Use 'git clean -n' (dry run) first to see what would be deleted." >&2
  exit 2
fi

# Pattern 3: Database deletion
if echo "$COMMAND" | grep -qE 'rm\s+.*CLI_Guard_DB\.db'; then
  echo "BLOCKED: Attempted deletion of the CLI Guard database file." >&2
  echo "If you need to reset the database, export a backup first." >&2
  exit 2
fi

# Pattern 4: Drop table commands via sqlite3
if echo "$COMMAND" | grep -qiE 'DROP\s+TABLE'; then
  echo "BLOCKED: DROP TABLE detected." >&2
  echo "This permanently destroys table data. Export a backup first if needed." >&2
  exit 2
fi

exit 0
