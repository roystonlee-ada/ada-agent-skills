#!/usr/bin/env python3
"""Check every adacli command and flag the skills name against a real adacli.

The mocked suite drives the MCP route only, so a command removed from adacli
still passes there. This reads adacli's own description of itself
(`adacli <instance> agent-context`), finds each adacli command in skills/, and
reports any command or flag that adacli no longer has.

With --baseline it also diffs two agent-context files, so an upgrade shows
which commands and flags came and went, and which new commands write.

Usage:
  adacli <instance> agent-context > new.json
  python3 evals/check_cli_commands.py new.json
  python3 evals/check_cli_commands.py new.json --baseline evals/adacli-commands.json
  python3 evals/check_cli_commands.py new.json --save evals/adacli-commands.json
Exit 1 when a skill names a command or flag that adacli does not have.
"""
import argparse
import json
import pathlib
import re
import sys

SKILLS = pathlib.Path(__file__).resolve().parent.parent / "skills"
SPAN_RE = re.compile(r"`([^`\n]+)`")
WORD_RE = re.compile(r"^[a-z][a-z-]*$")
FLAG_RE = re.compile(r"(?<![\w-])(--?[a-zA-Z][\w-]*)")
STOP = {"|", ">", ">>", "&&", ";", "2>", "<", "||"}

# agent-context lists each command once, without its aliases.
ALIASES = {"client info": "client show"}

# A span right after one of these words names a command on purpose: one adacli
# removed, or one not released yet.
NAMED_ON_PURPOSE = re.compile(r"(removed|unmerged|unreleased|no longer)[^`]{0,40}$", re.I)
WRITE_WORDS = {
    "create", "update", "delete", "remove", "add", "set", "unset", "stage",
    "promote", "revert", "enable", "disable", "import", "revoke", "connect",
    "configure", "set-rollout", "stop-rollout", "update-role", "update-step",
    "approve", "dismiss", "move", "hide", "unhide", "group", "ungroup",
    "scrape", "sync", "set-rules", "clear", "test", "generate", "start",
    "record", "talk",
}


def load(path):
    """Commands as {path: set of flags}, from a full agent-context or a saved list."""
    data = json.loads(pathlib.Path(path).read_text())
    if "commands" in data and isinstance(data["commands"], dict):
        return data.get("version", "?"), {k: set(v) for k, v in data["commands"].items()}, set(data.get("global", []))
    cmds = {}
    for c in data["commands"]:
        flags = set()
        for o in c.get("options", []):
            flags.update(FLAG_RE.findall(o["flags"]))
        cmds[c["path"]] = flags
    glob = set()
    for g in data.get("globalFlags", []):
        glob.update(FLAG_RE.findall(g["flags"]))
    return data.get("version", "?"), cmds, glob


def children(cmds, path):
    prefix = path + " "
    return {p[len(prefix):].split()[0] for p in cmds if p.startswith(prefix)}


def check_span(tokens, cmds, glob, tops):
    """Problems in one command span, or None when the span is not a command."""
    if "adacli" in tokens:
        tokens = tokens[tokens.index("adacli") + 1:]
        if tokens and tokens[0].startswith("-"):
            return None

        # The first word is the instance unless it is already a command.
        if tokens and tokens[0] not in tops:
            tokens = tokens[1:]
    elif len(tokens) < 2 or tokens[0] not in tops or not WORD_RE.match(tokens[1]):
        return None
    if not tokens or tokens[0] not in tops:
        return None
    path = tokens[0]
    rest = tokens[1:]
    i = 0
    while i < len(rest) and WORD_RE.match(rest[i]):
        nxt = f"{path} {rest[i]}"
        nxt = ALIASES.get(nxt, nxt)
        if nxt in cmds:
            path = nxt
            i += 1
            continue
        if children(cmds, path):
            return [f"no command `{nxt}`"]
        break
    problems = []
    allowed = cmds[path] | glob | {"--help", "-h"}
    for t in rest[i:]:
        if t in STOP:
            break
        if "..." in t:
            continue
        for flag in FLAG_RE.findall(t.split("=")[0]) if t.startswith("-") else []:
            if flag not in allowed:
                problems.append(f"`{path}` has no flag {flag}")
    return problems


def scan(cmds, glob):
    tops = {p.split()[0] for p in cmds}
    found = []
    for f in sorted(SKILLS.rglob("*.md")):
        for n, line in enumerate(f.read_text().splitlines(), 1):
            for m in SPAN_RE.finditer(line):
                span = m.group(1)
                if NAMED_ON_PURPOSE.search(line[:m.start()]):
                    continue
                problems = check_span(span.split(), cmds, glob, tops)
                for p in problems or []:
                    found.append(f"{f.relative_to(SKILLS)}:{n}: {p}  in `{span}`")
    return found


def diff(old, new):
    out = []
    for p in sorted(set(old) - set(new)):
        out.append(f"REMOVED command `{p}`")
    for p in sorted(set(new) - set(old)):
        tag = "WRITE " if p.split()[-1] in WRITE_WORDS else ""
        out.append(f"NEW {tag}command `{p}`")
    for p in sorted(set(old) & set(new)):
        for fl in sorted(old[p] - new[p]):
            out.append(f"REMOVED flag `{p} {fl}`")
        for fl in sorted(new[p] - old[p]):
            out.append(f"NEW flag `{p} {fl}`")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("context", help="output of `adacli <instance> agent-context`")
    ap.add_argument("--baseline", help="an older agent-context or saved list to diff against")
    ap.add_argument("--save", help="write the command list here, as the next baseline")
    a = ap.parse_args()

    version, cmds, glob = load(a.context)
    print(f"adacli {version}: {len(cmds)} commands")
    if a.baseline:
        old_version, old, _ = load(a.baseline)
        changes = diff(old, cmds)
        print(f"since {old_version}: {len(changes)} changes")
        for line in changes:
            print("  " + line)
    problems = scan(cmds, glob)
    for p in problems:
        print("MISSING " + p)
    print(f"{len(problems)} commands or flags in skills/ that adacli {version} does not have")
    if a.save:
        pathlib.Path(a.save).write_text(json.dumps(
            {"version": version, "global": sorted(glob), "commands": {k: sorted(v) for k, v in sorted(cmds.items())}},
            indent=1) + "\n")
        print(f"saved {a.save}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
