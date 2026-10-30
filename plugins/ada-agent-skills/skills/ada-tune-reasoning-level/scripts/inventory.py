#!/usr/bin/env python3
"""List every SET and ASK step that has a Reasoning level, with difficulty signals.

  python3 inventory.py <instance> [--playbook <id>] [--json]

Reads only. A step is in scope when it is a generative SET (it has an instruction)
or a reasoning ASK. Exact SET (a literal value) and exact ASK have no level.
The signals are a first sort, not a verdict: prove each candidate with an A/B run.
"""

import json
import re
import subprocess
import sys

SIGNALS = {
    "date_math": r"\b(days?|weeks?|months?|years?|business|weekday|calendar|deadline|expir\w*|before|after|until|from now|ago|next|last|tomorrow|yesterday)\b.*\b(date|day|time)\b|\b(date|day)\b.*\b(plus|minus|after|before|from)\b|YYYY|MM-DD|ISO",
    "arithmetic": r"\b(total|subtotal|sum|multiply|divide|percent|percentage|discount|tax|vat|fee|rate|price|amount|convert)\b|\d\s*%|[+*/]\s*\d",
    "rule_in_text": r"\b(if|unless|only when|at least|at most|more than|less than|or more|or less|and not|otherwise|threshold)\b.*\b(then|otherwise|else|tier|level|eligible)\b|>=|<=",
    "classification": r"\b(classify|categor\w+|choose one|one of|primary|main reason|intent|bucket)\b",
}


def adacli(instance, *args):
    r = subprocess.run(["adacli", instance, *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"adacli {' '.join(args)} failed: {r.stderr.strip()[:300]}")
    return json.loads(r.stdout)


def walk(steps):
    for s in steps:
        yield s
        for br in s.get("branches") or []:
            yield from walk(br.get("steps") or [])


def instruction_of(step):
    parts = [step.get("instruction") or ""]
    for i in step.get("inputs") or []:
        parts.append(i.get("extraction_instructions") or "")
    return " ".join(p for p in parts if p)


def in_scope(step):
    if step.get("type") == "set":
        return bool(step.get("instruction")) and step.get("value") in (None, "")
    if step.get("type") == "ask":
        return step.get("ask_mode", "reasoning") == "reasoning"
    return False


def signals(step):
    text = instruction_of(step)
    found = [k for k, rx in SIGNALS.items() if re.search(rx, text, re.I)]
    entries = len(re.findall(r"[=:→-]>?\s*\w+\s*[,;\n]", text))
    if entries >= 12:
        found.append("long_list")
    accepted = len(step.get("accepted_values") or [])
    if accepted >= 8:
        found.append("many_accepted_values")
    if len(step.get("inputs") or []) > 1:
        found.append("multi_variable")
    return found, len(text)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    instance, only, as_json = args[0], None, "--json" in args
    if "--playbook" in args:
        only = args[args.index("--playbook") + 1]
    listing = adacli(instance, "playbooks", "list", "--json")
    listing = listing.get("playbooks", listing)
    rows = []
    for pb in listing:
        if only and pb["_id"] != only:
            continue
        if pb.get("version") != 2:
            continue
        data = adacli(instance, "playbooks", "get", pb["_id"], "--content", "--json")
        for sec in data.get("sections") or []:
            for st in walk(sec.get("steps") or []):
                if not in_scope(st):
                    continue
                sig, n = signals(st)
                rows.append({
                    "playbook": pb["name"], "playbook_id": pb["_id"], "step_id": st.get("id"),
                    "type": st["type"], "level": st.get("reasoning_level") or "normal",
                    "active": bool(pb.get("is_active", pb.get("enabled"))),
                    "instruction_chars": n, "signals": sig,
                    "has_fallback": bool(st.get("fallback_value") or any(i.get("fallback_value") for i in st.get("inputs") or [])),
                })
    if as_json:
        print(json.dumps(rows, indent=1))
        return
    print(f"{len(rows)} steps in scope")
    for r in sorted(rows, key=lambda r: (-len(r["signals"]), r["playbook"])):
        flag = "HIGH" if r["level"] == "high" else "    "
        print(f"{flag} {r['type']:<4} {r['playbook'][:38]:<38} {r['step_id']}  {','.join(r['signals']) or '-':<34} fb={'y' if r['has_fallback'] else 'N'}")


if __name__ == "__main__":
    main()
