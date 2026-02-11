#!/bin/bash
# Hook: Run unit tests before committing
# This ensures that code being committed doesn't break existing tests.
#
# How it works:
# - Triggered on Bash tool use
# - Only activates when the command is a git commit
# - Runs the test suite; blocks the commit if tests fail
# - Exit 0 = allow, Exit 2 = block

COMMAND=$(jq -r '.tool_input.command' < /dev/stdin)

# Only run on git commit commands
if ! echo "$COMMAND" | grep -qE 'git\s+commit'; then
  exit 0
fi

# Run the test suite from the project directory
cd "$CLAUDE_PROJECT_DIR" || exit 0

TEST_OUTPUT=$(python3 -m unittest discover tests/ 2>&1)
TEST_EXIT=$?

if [ $TEST_EXIT -ne 0 ]; then
  echo "BLOCKED: Unit tests are failing. Fix tests before committing." >&2
  echo "" >&2
  echo "$TEST_OUTPUT" >&2
  exit 2
fi

exit 0
