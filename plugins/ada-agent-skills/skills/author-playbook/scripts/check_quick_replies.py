#!/usr/bin/env python3
"""Check the quick-reply labels of every ASK step in one or more JSON files.

Accepts any JSON that holds ask steps: `playbooks get --json`, `playbooks export-steps`,
or a changeset file for `changesets stage`. Prints one line per problem and exits 1
when any ask fails. An ask with more than 10 values is reported but is a design issue,
so it is listed as WARN and does not change the exit code.

Usage: python3 check_quick_replies.py <file.json> [<file.json> ...]

Rules (design rules for short, clear buttons on Web Chat and the Messaging SDK):
  R1  each title (the label, else the value) is at most 20 characters
  R2  titles are distinct once lower-cased and whitespace-collapsed, and no title
      equals another option's value
  R3  at most 10 values (WARN)
  R4  no title is a status token such as did_not_answer
  R5  no title is a snake_case token
"""
import json
import re
import sys
from collections import defaultdict

LIMIT = 20
MAX_VALUES = 10
STATUS_TOKENS = {"did_not_answer", "did not answer"}


def norm(text):
    return " ".join(str(text).split()).casefold()


def asks(node):
    if isinstance(node, dict):
        if node.get("type") == "ask":
            yield node
        for value in node.values():
            yield from asks(value)
    elif isinstance(node, list):
        for value in node:
            yield from asks(value)


def chip_values(step):
    """The accepted values that become chips, or None when the ask draws none."""
    if not step.get("quick_replies_enabled"):
        return None
    inputs = step.get("inputs") or []
    if inputs:
        if len(inputs) != 1 or inputs[0].get("accepted_values_source") == "variable":
            return None
        return list(inputs[0].get("accepted_values") or [])
    if step.get("accepted_values_source") == "variable":
        return None
    return list(step.get("accepted_values") or [])


def problems(step):
    values = chip_values(step)
    if values is None or len(values) < 2:
        return []
    labels = step.get("quick_reply_labels") or {}
    titles = {v: labels.get(v) or v for v in values}
    out = []
    for v in values:
        t = titles[v]
        if len(t) > LIMIT:
            out.append(("FAIL", "R1", f"{v!r}: title {t!r} is {len(t)} characters"))
        if re.fullmatch(r"[a-z0-9]+(_[a-z0-9]+)+", t):
            out.append(("FAIL", "R5", f"{v!r}: title {t!r} is a snake_case token, add a label"))
        if norm(t) in STATUS_TOKENS:
            out.append(("FAIL", "R4", f"{v!r}: title {t!r} is a status token, add a label"))
    claims = defaultdict(set)
    for v in values:
        for text in {norm(titles[v]), norm(v)}:
            claims[text].add(v)
    for text, vs in claims.items():
        if len(vs) > 1:
            out.append(("FAIL", "R2", f"{sorted(vs)!r} both claim {text!r}"))
    if len(values) > MAX_VALUES:
        out.append(("WARN", "R3", f"{len(values)} values, the cap is {MAX_VALUES}"))
    return out


def main(paths):
    failed = False
    for path in paths:
        for step in asks(json.load(open(path))):
            for level, rule, msg in problems(step):
                failed = failed or level == "FAIL"
                print(f"{level} {rule} {path} step {step.get('id', '?')}: {msg}")
    print("quick-reply check:", "FAILED" if failed else "ok")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
