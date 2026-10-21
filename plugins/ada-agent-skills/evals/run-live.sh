#!/usr/bin/env bash
# Run the live cases (evals-live/) against a real Ada instance's MCP server, read tools only.
# Write tools are never granted, so the harness refuses them even if the agent tries.
#
#   evals/run-live.sh                         # roystonlee-csc, 3 runs per case
#   RUNS=1 evals/run-live.sh                  # quick pass
#   ADA_LIVE_MCP_URL=https://<instance>.ada.support/api/mcp/oauth evals/run-live.sh
#
# Sign in once first: python3 evals/check_tool_names.py <url> opens the OAuth page
# and caches the token that the live cases reuse.

set -euo pipefail
cd "$(dirname "$0")/.."
RUNS="${RUNS:-3}"
URL="${ADA_LIVE_MCP_URL:-https://roystonlee-csc.us2.ada.support/api/mcp/oauth}"
OUT="evals-live/results/$(date +%Y%m%d-%H%M)"

# The harness gives each run a temporary HOME, so point mcp-remote at the real token cache.

export MCP_REMOTE_CONFIG_DIR="${MCP_REMOTE_CONFIG_DIR:-$HOME/.mcp-auth}"
mkdir -p "$OUT"

# No cached token means every run opens its own sign-in tab, so stop here instead.

KEY=$(python3 -c "import hashlib,sys; print(hashlib.md5(sys.argv[1].encode()).hexdigest())" "$URL")
if ! ls "$MCP_REMOTE_CONFIG_DIR"/mcp-remote-0.1.37/"${KEY}"_tokens.json >/dev/null 2>&1; then
  echo "No mcp-remote@0.1.38 token for $URL. Sign in once: python3 evals/check_tool_names.py $URL" >&2
  exit 1
fi


# A missing tool is reported in tool-names.txt and summary, but the cases still run.

python3 evals/check_tool_names.py "$URL" | tee "$OUT/tool-names.txt" || true
ADA_LIVE_MCP_URL="$URL" python3 evals/build_cases.py

READ_TOOLS=$(python3 -c "
import sys; sys.path.insert(0, 'evals')
from build_cases import T, READ_TOOLS
print(' '.join(T + t for t in READ_TOOLS))")

# shellcheck disable=SC2086
claude plugin eval . --eval-dir evals-live --mocks off --allow-tools $READ_TOOLS \
  --runs "$RUNS" -j 2 --ablation none --no-publish --trust-plugin --threshold 0 \
  --judge-model "${JUDGE:-sonnet}" --max-cost-usd "${MAX_COST:-15}" \
  --json "$OUT/live.json" --report "$OUT/live.html" >"$OUT/live.log" 2>&1 || true

python3 evals/compare.py "$OUT/live.json" --md "$OUT/summary.md"
echo "Results in $OUT"
