#!/usr/bin/env python3
"""Check the instruction of every reasoning-mode ASK step for unexpected-reply handling.

Accepts any JSON that holds ask steps: a playbook export, `playbooks get --json`, a
changeset file, or a folder of them. Prints one line per problem. Exits 1 when any
FAIL is found. WARN lines are advice and do not change the exit code.

Usage: python3 check_ask_instructions.py [--active-only] [--summary] <file-or-dir> [...]

Why: an ASK that saves yes/no (or any short list) reads a reply that is off the list
as "no answer", re-asks, and repeats the question word for word until the re-ask cap.
A yes/no ASK about an add-on looped on a reply saying the add-on cannot be bought in
that situation, which means NO. The instruction must say what each value means, including
problem replies, and how to word a re-ask.

Rules:
  A1  FAIL  a value is neither mapped nor named in the instruction
  A2  FAIL  a yes/no ASK never says that an error, problem or restriction means "no"
            (checked only when the question asks whether something worked or was done)
  A3  FAIL  the instruction tells the model to repeat the question as it was
  A4  WARN  max_reask_attempts is 0 and the ask has no fallback value, and a later action
            runs with no "is null" check on the variable in between. One non-answer
            ("thanks, that's all", a bare "yes") leaves the variable empty and the
            playbook moves on, so the action runs without it
  A5  WARN  contextual ASK with values and no line on how to word a re-ask
  A6  WARN  no max re-ask attempts set (default is 3, so the customer is asked 4 times)
  A7  WARN  ASK with values and no fallback value
  A8  WARN  the instruction says to accept any answer or never re-ask. The extraction
            prompt then drops the off-topic and Q&A statuses for the step, though live
            chats still answered side questions. Keep it only on purpose
"""
import json
import re
import sys
from pathlib import Path

STATUS = {"did_not_answer", "did not answer"}
QUOTES = "\"'“”‘’`"
SUCCESS_Q = re.compile(
    r"\b(able to|were you able|did (it|that|this)|worked|work\b|success|solved|resolved|"
    r"answered|helped|helpful|fixed|done|complete|go through|went through|received|get it)\b",
    re.I)
PROBLEM_WORDS = re.compile(
    r"\b(error|problem|issue|restriction|cannot|can't|can not|couldn't|could not|didn't|"
    r"did not|doesn't|does not|not work|failed|fail|unable|need help|needs help|declined|"
    r"blocked|stuck)\b", re.I)
REASK_LINE = re.compile(
    r"(acknowledg|reword|rephrase|different words|other words|another way|"
    r"say what the customer|name what the customer|briefly (note|mention|explain|say))", re.I)
VERBATIM = re.compile(
    r"(repeat (the|your|this|that) (same |exact |original )?(question|ask)\b|"
    r"ask (the )?same question again|re-?ask (it )?(exactly|verbatim|word for word)|"
    r"(same|exact) (words|wording) (again|as before))", re.I)
# Wording that removes the off-topic and Q&A controls for the step
# (extraction_system.jinja, STEP-INSTRUCTION PRECEDENCE).
ACCEPT_ANY = re.compile(
    r"(accept any (answer|reply|response)|any (answer|reply|response) is (fine|ok|accepted)|"
    r"accept the first answer|capture the reply verbatim|never re-?ask|never ask again|"
    r"always set this variable and proceed|do not classify as a topic change|"
    r"cannot be skipped|do not search knowledge)", re.I)


def asks(node):
    if isinstance(node, dict):
        if node.get("type") == "ask":
            yield node
        for value in node.values():
            yield from asks(value)
    elif isinstance(node, list):
        for value in node:
            yield from asks(value)


def flat_steps(node):
    """Every step in printed order: a branch's steps follow its if_else."""
    if isinstance(node, dict):
        if "type" in node and isinstance(node.get("type"), str):
            yield node
            for branch in node.get("branches") or []:
                yield from flat_steps(branch.get("steps") or [])
            yield from flat_steps(node.get("steps") or [])
            return
        for key in ("sections", "steps", "fields", "content", "playbook", "data", "changes"):
            if key in node:
                yield from flat_steps(node[key])
    elif isinstance(node, list):
        for value in node:
            yield from flat_steps(value)


def conditions_of(step):
    for branch in step.get("branches") or []:
        stack = [branch]
        while stack:
            group = stack.pop()
            yield from group.get("conditions") or []
            stack.extend(group.get("groups") or [])


def guards(step, var):
    """Whether an if_else tests the variable for null or blank."""
    return any(
        c.get("left_operand") == var and (
            c.get("comparison_operator") in ("is null", "is not null")
            or (c.get("comparison_operator") in ("is", "is not") and c.get("right_operand") == ""))
        for c in conditions_of(step))


def playbooks(node):
    """Each playbook (a dict with sections) in the file, or the whole file when none."""
    found = []
    stack = [node]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            if "sections" in item:
                found.append(item)
                continue
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    return found or [node]


def unguarded_actions(doc):
    """(ask, variable, action) for each zero-re-ask ask with no fallback whose next action
    runs with no null check on the variable in between."""
    found = []
    for playbook in playbooks(doc):
        found.extend(unguarded_in(list(flat_steps(playbook))))
    return found


def unguarded_in(steps):
    found = []
    for i, step in enumerate(steps):
        if step.get("type") != "ask" or step.get("max_reask_attempts") != 0:
            continue
        inputs = step.get("inputs") or [step]
        for inp in inputs:
            var = inp.get("variable_id")
            if not var or inp.get("fallback_value") or step.get("fallback_value"):
                continue
            for later in steps[i + 1:]:
                if later.get("type") == "if_else" and guards(later, var):
                    break
                if later.get("type") == "run" and later.get("target_type") == "action":
                    found.append((step, var, later))
                    break
    return found


def values_of(step):
    inputs = step.get("inputs") or []
    if inputs:
        if len(inputs) != 1 or inputs[0].get("accepted_values_source") == "variable":
            return [], None
        return list(inputs[0].get("accepted_values") or []), inputs[0].get("fallback_value")
    if step.get("accepted_values_source") == "variable":
        return [], None
    return list(step.get("accepted_values") or []), step.get("fallback_value")


def mapping_patterns(value):
    v = re.escape(value)
    q = f"[{re.escape(QUOTES)}]"
    return [
        rf"^\s*[-*\u2022]\s*{q}?{v}{q}?\s*(?:[:\-\u2013\u2014=(]|\bif\b|\bwhen\b|\bonly\b)",
        rf"\b(?:save|store|extract|classify|set|record|return|output|answer)\b[^\n]{{0,60}}{q}{v}{q}",
        rf"{q}{v}{q}\s*(?:if|when|means|for|:|=|-)",
        rf"\b(?:save|store|extract|classify|set|record|return|output)\s+{v}\b",
        rf"\b{v}\b\s+(?:if|when|only when|means)\b",
    ]


def has_mapping(text, value):
    return any(re.search(p, text, re.I | re.M) for p in mapping_patterns(value))


def mapping_lines(text, value):
    """The lines that map replies to one value, used to look for problem words."""
    pats = mapping_patterns(value)
    return " ".join(
        line for line in text.splitlines() if any(re.search(p, line, re.I) for p in pats))


def problems(step):
    text = step.get("instruction") or ""
    values, fallback = values_of(step)
    values = [v for v in values if v.casefold() not in STATUS]
    out = []
    exact = step.get("question_phrasing") == "exact_words" or bool(step.get("exact_words"))

    if len(values) >= 2:
        lowered = {v.casefold() for v in values}
        yes_no = lowered == {"yes", "no"}
        if yes_no and SUCCESS_Q.search(text):
            no_value = next(v for v in values if v.casefold() == "no")
            if not PROBLEM_WORDS.search(mapping_lines(text, no_value)):
                out.append(("FAIL", "A2",
                            "yes/no worked-or-not question: no line says an error, problem "
                            "or restriction reply means no"))
        else:
            flat = text.casefold().replace("_", " ")
            plain = all(re.fullmatch(r"\d+", v) for v in values)
            missing = [] if plain else [
                v for v in values
                if not has_mapping(text, v) and v.casefold().replace("_", " ") not in flat]
            if missing:
                out.append(("FAIL", "A1", f"{missing!r} neither mapped nor named in the instruction"))

    if VERBATIM.search(text):
        out.append(("FAIL", "A3", "tells the model to repeat the question as it was"))
    if ACCEPT_ANY.search(text):
        out.append(("WARN", "A8", "accept-any-answer or never-re-ask wording"))

    if values and not exact and step.get("question_phrasing") != "exact_words":
        if not REASK_LINE.search(text):
            out.append(("WARN", "A5", "no line on how to word a re-ask"))
    if values and step.get("max_reask_attempts") is None:
        out.append(("WARN", "A6", "max_reask_attempts not set (4 prompts before the fallback)"))
    if values and not fallback:
        out.append(("WARN", "A7", "no fallback value"))
    return out


def files(args):
    for arg in args:
        p = Path(arg)
        if p.is_dir():
            yield from sorted(p.rglob("*.json"))
        else:
            yield p


def main(argv):
    active_only = "--active-only" in argv
    summary = "--summary" in argv
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    fails = warns = checked = 0
    per_rule = {}
    for path in files(args):
        try:
            doc = json.loads(path.read_text())
        except (ValueError, OSError):
            continue
        if active_only and isinstance(doc, dict) and doc.get("is_active") is False:
            continue
        name = doc.get("name") if isinstance(doc, dict) else None
        zero_reask = {}
        for ask, var, action in unguarded_actions(doc):
            zero_reask.setdefault(id(ask), []).append(
                ("WARN", "A4", f"max_reask_attempts 0 and no fallback: one non-answer leaves "
                               f"{var} empty and action {action.get('target_id')} "
                               f"[{action.get('id')}] runs with no 'is null' check"))
        for step in asks(doc):
            checked += 1
            head = " ".join((step.get("instruction") or "").split())[:70]
            for level, rule, msg in problems(step) + zero_reask.get(id(step), []):
                per_rule[(level, rule)] = per_rule.get((level, rule), 0) + 1
                if level == "FAIL":
                    fails += 1
                else:
                    warns += 1
                if not summary:
                    print(f"{level} {rule} {name or path.name} [{step.get('id')}] {msg} | {head!r}")
    print(f"checked {checked} asks: {fails} FAIL, {warns} WARN")
    if summary:
        for (level, rule), n in sorted(per_rule.items()):
            print(f"  {rule} {level}: {n}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
