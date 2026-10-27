#!/bin/sh
# Point vague Ada agent asks at ada-agent-guide. Stays silent unless adacli or an Ada MCP server is set up.

has_ada=""
command -v adacli >/dev/null 2>&1 && has_ada=1
if [ -z "$has_ada" ]; then
  for f in "$PWD/.mcp.json" "$HOME/.claude.json"; do
    grep -qi '"ada[-_a-z0-9]*"[[:space:]]*:' "$f" 2>/dev/null && has_ada=1 && break
  done
fi
[ -n "$has_ada" ] || exit 0

printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"For an Ada agent ask that names no stage (\"fix this chat\", \"get this live\", \"where are we\"), load the ada-agent-guide skill first."}}'
