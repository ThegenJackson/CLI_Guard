#!/bin/bash
# Hook: Prevent direct pushes to main branch
# This protects your stable code by forcing work onto feature branches.
#
# How it works:
# - Claude Code passes the Bash command as JSON on stdin
# - We extract the command with jq and check if it pushes to main
# - Exit 0 = allow, Exit 2 = block

COMMAND=$(jq -r '.tool_input.command' < /dev/stdin)

# Check for git push to main or master (with or without origin)
if echo "$COMMAND" | grep -qE 'git\s+push.*\b(main|master)\b'; then
  echo "BLOCKED: Direct push to main/master branch." >&2
  echo "Use a feature branch instead: git checkout -b feature/your-feature" >&2
  exit 2
fi

# Check for force push (dangerous regardless of branch)
if echo "$COMMAND" | grep -qE 'git\s+push\s+.*--force'; then
  echo "BLOCKED: Force push detected." >&2
  echo "Force pushing can overwrite others' work. Use --force-with-lease if needed." >&2
  exit 2
fi

exit 0
