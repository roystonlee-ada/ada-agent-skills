#!/usr/bin/env python3
"""Check that every Ada MCP tool and operation the skills name exists on a live server.

The mocked suite follows the runtime files, so a tool renamed on the server
still passes there. This lists the real server's tools (read-only, no tool is
called) and diffs them against the names in skills/.

Usage:
  python3 evals/check_tool_names.py https://<instance>.ada.support/api/mcp/oauth
Exit 1 when a name the skills use is missing on the server.
"""
import json
import pathlib
import re
import subprocess
import sys

SKILLS = pathlib.Path(__file__).resolve().parent.parent / "skills"
TOOL_RE = re.compile(r"`((?:get|list|search|edit|run|send|connect|refresh|compare|draft)_[a-z_]+)`")
OP_RE = re.compile(r'"operation"\s*:\s*"([a-z_]+)"|operation[`\s]+`([a-z_]+)`')


def skill_names():
    tools, ops = {}, {}
    for f in SKILLS.rglob("*.md"):
        text = f.read_text()
        rel = str(f.relative_to(SKILLS))
        for name in TOOL_RE.findall(text):
            tools.setdefault(name, set()).add(rel)
        for a, b in OP_RE.findall(text):
            ops.setdefault(a or b, set()).add(rel)
    return tools, ops


def server_tools(url):
    proc = subprocess.Popen(
        ["npx", "-y", "mcp-remote@0.1.38", url],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )

    def send(msg):
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()

    def wait_for(msg_id):
        for line in proc.stdout:
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("id") == msg_id:
                return msg
        raise SystemExit("server closed before answering; run the OAuth login once in Claude Code")

    send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18", "capabilities": {},
        "clientInfo": {"name": "check-tool-names", "version": "1"}}})
    wait_for(1)
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    tools, cursor, n = [], None, 2
    while True:
        send({"jsonrpc": "2.0", "id": n, "method": "tools/list",
              "params": {"cursor": cursor} if cursor else {}})
        result = wait_for(n)["result"]
        tools += result["tools"]
        cursor = result.get("nextCursor")
        n += 1
        if not cursor:
            break
    proc.terminate()
    return tools


def schema_ops(tool):
    found = set()

    def walk(node):
        if isinstance(node, dict):
            op = node.get("properties", {}).get("operation", {})
            found.update(op.get("enum", []))
            if "const" in op:
                found.add(op["const"])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(tool.get("inputSchema", {}))
    return found


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    tools = server_tools(sys.argv[1])
    live = {t["name"] for t in tools}
    live_ops = set().union(*(schema_ops(t) for t in tools))
    want_tools, want_ops = skill_names()

    missing = sorted(set(want_tools) - live)
    print(f"server tools: {len(live)}; tools the skills name: {len(want_tools)}")
    for name in missing:
        print(f"MISSING tool {name}  (used in {', '.join(sorted(want_tools[name]))})")
    if live_ops:
        for op in sorted(set(want_ops) - live_ops):
            print(f"MISSING operation {op}  (used in {', '.join(sorted(want_ops[op]))})")
    else:
        print("no operation enums in the server schemas; operations not checked")
    unused = sorted(live - set(want_tools))
    if unused:
        print("on the server, never named by a skill: " + ", ".join(unused))
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
