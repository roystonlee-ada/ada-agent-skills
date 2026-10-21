#!/usr/bin/env python3
"""Compare a skills-on run against a skills-off run of the same cases.

    python3 evals/compare.py <with.json> [<without.json>] [--md out.md]

Score per run = share of graders passed, leaving out `skill-fired`, so a case
scores what the agent did, not whether it loaded the skill. Without a second
file it prints the skills-on table only.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict


def load(path: str) -> dict:
    out = {}
    for case in json.load(open(path))["cases"]:
        runs = [r for arm in case["arms"].values() for r in arm]
        fired, scores, fails, errors = [], [], defaultdict(int), []
        for r in runs:
            if r.get("error") and not r.get("graders"):
                errors.append(r["error"][:80])
                continue
            gs = r.get("graders", [])
            sf = [g for g in gs if g["name"] == "skill-fired"]
            if sf:
                fired.append(bool(sf[0]["passed"]))
            rest = [g for g in gs if g["name"] != "skill-fired"] or gs
            scores.append(sum(bool(g["passed"]) for g in rest) / len(rest))
            for g in rest:
                if not g["passed"]:
                    fails[g["name"]] += 1
        out[case["name"]] = {"tags": case.get("tags") or [], "runs": len(scores), "fired": fired,
                             "score": sum(scores) / len(scores) if scores else None,
                             "fails": dict(fails), "errors": errors}
    return out


def pct(x) -> str:
    return "-" if x is None else f"{round(100 * x)}%"


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    md = sys.argv[sys.argv.index("--md") + 1] if "--md" in sys.argv else None
    if md in args:
        args.remove(md)
    on = load(args[0])
    off = load(args[1]) if len(args) > 1 else {}
    rows = ["| Case | Skill fired | Score, skills on | Score, skills off | Failed checks (skills on) |",
            "|---|---|---|---|---|"]
    order = sorted(on, key=lambda n: (on[n]["score"] if on[n]["score"] is not None else -1, n))
    for n in order:
        c = on[n]
        fired = f"{sum(c['fired'])}/{len(c['fired'])}" if c["fired"] else "-"
        fails = ", ".join(f"{k} x{v}" for k, v in c["fails"].items()) or ("error: " + c["errors"][0] if c["errors"] else "-")
        rows.append(f"| {n} | {fired} | {pct(c['score'])} | {pct(off.get(n, {}).get('score'))} | {fails} |")
    text = "\n".join(rows)
    print(text)
    if md:
        open(md, "w").write(text + "\n")


if __name__ == "__main__":
    main()
