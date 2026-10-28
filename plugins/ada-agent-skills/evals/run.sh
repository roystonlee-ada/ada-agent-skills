#!/usr/bin/env bash
# Run the suite twice with the same mocked Ada tools: skills on, then skills off
# (the Skill tool removed), and print the comparison table.
#
#   evals/run.sh                 # 3 runs per case
#   RUNS=1 evals/run.sh          # quick pass
#   TAG=behaviour evals/run.sh   # one tag only

set -euo pipefail
cd "$(dirname "$0")/.."
RUNS="${RUNS:-3}"
OUT="evals/results/$(date +%Y%m%d-%H%M)"
mkdir -p "$OUT"
python3 evals/build_cases.py
FILTER=()
[ -n "${TAG:-}" ] && FILTER=(--tag "$TAG")

# The default Haiku judge failed correct replies on multi-part rubrics, so judge with Sonnet.
common=(--runs "$RUNS" -j 4 --ablation none --no-publish --trust-plugin --threshold 0
  --judge-model "${JUDGE:-sonnet}" --max-cost-usd "${MAX_COST:-40}")

claude plugin eval . "${common[@]}" ${FILTER[@]+"${FILTER[@]}"} --json "$OUT/with.json" --report "$OUT/with.html" >"$OUT/with.log" 2>&1 || true

# Routing cases mean nothing with the Skill tool removed, so the baseline runs behaviour only.
claude plugin eval . "${common[@]}" --tag behaviour --disallow-tools Skill \
  --json "$OUT/without.json" --report "$OUT/without.html" >"$OUT/without.log" 2>&1 || true

python3 evals/compare.py "$OUT/with.json" "$OUT/without.json" --md "$OUT/summary.md"
echo "Results in $OUT"
