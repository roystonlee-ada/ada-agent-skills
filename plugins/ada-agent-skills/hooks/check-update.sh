#!/bin/sh
# Tell the user when a newer ada-agent-skills version exists. Checks once a day and stays silent on any failure.

root="${CLAUDE_PLUGIN_ROOT:-$(dirname "$0")/..}"
repo="roystonlee-ada/ada-agent-skills"
stamp="${XDG_CACHE_HOME:-$HOME/.cache}/ada-agent-skills-update-check"

read_version() {
  sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' | head -1
}

installed=$(read_version < "$root/.claude-plugin/plugin.json" 2>/dev/null)
[ -n "$installed" ] || exit 0

if [ -f "$stamp" ] && [ -z "$(find "$stamp" -mmin +1440 2>/dev/null)" ]; then
  exit 0
fi
mkdir -p "$(dirname "$stamp")" 2>/dev/null && : > "$stamp"

latest=$(curl -fsS --max-time 3 \
  "https://raw.githubusercontent.com/$repo/main/plugins/ada-agent-skills/.claude-plugin/plugin.json" 2>/dev/null | read_version)
[ -n "$latest" ] && [ "$latest" != "$installed" ] || exit 0

newest=$(printf '%s\n%s\n' "$installed" "$latest" | sort -V | tail -1)
[ "$newest" = "$latest" ] || exit 0

printf '{"systemMessage":"ada-agent-skills %s is out (you have %s). Update with: claude plugin marketplace update ada-agent-skills && claude plugin update ada-agent-skills@ada-agent-skills, then restart. What changed: https://github.com/%s/blob/main/CHANGELOG.md"}\n' \
  "$latest" "$installed" "$repo"
