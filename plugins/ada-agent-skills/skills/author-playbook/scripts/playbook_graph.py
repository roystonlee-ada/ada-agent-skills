import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import sys


def select_playbook(data):
    if isinstance(data, list):
        if not data:
            raise ValueError("Empty export has no playbook graph")
        if all(isinstance(item, dict) and "type" in item for item in data):
            return {"steps": data}
        if all(isinstance(item, dict) and "steps" in item for item in data):
            return {"sections": data}
        if len(data) == 1:
            return select_playbook(data[0])
        raise ValueError("Export one playbook at a time, preserving its sections")
    if not isinstance(data, dict):
        raise ValueError("Expected a playbook object, sections or steps array")
    if data.get("next_cursor") or data.get("has_more") or "items" in data:
        raise ValueError("Paged exports must be fully assembled into one complete playbook first")
    if "sections" in data or "steps" in data:
        return data
    wrappers = [key for key in ("data", "playbook", "playbooks", "fields", "entities") if key in data]
    if len(wrappers) == 1:
        return select_playbook(data[wrappers[0]])
    raise ValueError("No unambiguous playbook found; save the complete playbook object")


def convert(data):
    playbook = select_playbook(data)
    if playbook.get("version", 2) != 2:
        raise ValueError("Only structured V2 playbooks are supported")
    sections = playbook.get("sections")
    if sections is None:
        sections = [{"id": None, "steps": playbook.get("steps")}]
    if not isinstance(sections, list) or not sections:
        raise ValueError("Expected a non-empty sections array")
    graph = {"identity": playbook.get("id") or playbook.get("_id"),
             "name": playbook.get("name"), "sections": [],
             "playbook_config": {key: playbook[key] for key in ("general_instructions", "on_human_request", "on_off_topic", "on_off_script") if key in playbook},
             "nodes": [], "edges": [], "findings": []}
    ids = set()
    sequences = []

    def finding(code, step, detail, status="OPEN"):
        graph["findings"].append({"code": code, "step": step, "status": status, "detail": detail})

    def register(steps, location, depth=0):
        if depth > 10 or not isinstance(steps, list):
            raise ValueError(f"Invalid or excessively nested steps at {location}")
        for index, step in enumerate(steps):
            path = f"{location}.steps[{index}]"
            if not isinstance(step, dict) or not isinstance(step.get("id"), str) or not step["id"]:
                raise ValueError(f"Step needs a persisted string id at {path}")
            sid = step["id"]
            if sid in ids:
                raise ValueError(f"Duplicate step id: {sid}")
            ids.add(sid)
            if len(ids) > 10000:
                raise ValueError("Graph exceeds 10000 steps; export a bounded playbook")
            if not isinstance(step.get("type"), str):
                raise ValueError(f"Step type missing at {path}")
            config = {key: value for key, value in step.items() if key not in ("id", "type", "branches")}
            graph["nodes"].append({"id": sid, "type": step["type"], "source": path, "config": config})
            if step["type"] == "if_else":
                branches = step.get("branches")
                if not isinstance(branches, list) or len(branches) != 2:
                    raise ValueError(f"Expected two canonical branches at {path}")
                for bi, branch in enumerate(branches):
                    if not isinstance(branch, dict):
                        raise ValueError(f"Invalid branch at {path}.branches[{bi}]")
                    register(branch.get("steps"), f"{path}.branches[{bi}]", depth + 1)
            elif "branches" in step or "steps" in step:
                raise ValueError(f"Unrecognized nested control flow at {path}")

    for index, section in enumerate(sections):
        if not isinstance(section, dict) or "steps" not in section:
            raise ValueError("Header-only sections are incomplete; export every section's steps")
        graph["sections"].append({key: value for key, value in section.items() if key != "steps"})
        register(section["steps"], f"sections[{index}]")
        sequences.extend(section["steps"])
    if not ids:
        raise ValueError("Export contains no steps")

    def boundary(kind, label):
        key = f"boundary:{kind}:{label}"
        while key in ids:
            key += ":boundary"
        ids.add(key)
        graph["nodes"].append({"id": key, "type": "boundary", "source": "", "config": {"kind": kind, "label": label}})
        return key

    end = boundary("end", "playbook completion or caller return")

    def edge(source, target, event, evidence, condition=None):
        graph["edges"].append({"from": source, "to": target, "event": event,
                               "condition": condition, "evidence": evidence, "coverage": "UNTESTED"})

    def connect(steps, successor):
        steps = [step for step in steps if step["type"] != "note"]
        for index, step in enumerate(steps):
            sid = step["id"]
            following = steps[index + 1]["id"] if index + 1 < len(steps) else successor
            kind = step["type"]
            if kind == "if_else":
                for bi, branch in enumerate(step["branches"]):
                    condition = {key: value for key, value in branch.items() if key != "steps"}
                    branch_steps = [item for item in branch["steps"] if item["type"] != "note"]
                    target = branch_steps[0]["id"] if branch_steps else following
                    edge(sid, target, "if" if bi == 0 else "else", "ordered binary branches and lexical continuation", condition)
                    connect(branch["steps"], following)
            elif kind == "go_to":
                target = step.get("target_step_id")
                if isinstance(target, str) and target in persisted_ids and types[target] != "note":
                    edge(sid, target, "go_to", "target_step_id")
                    if target == sid:
                        finding("invalid_target", sid, "A self-targeting GO_TO is invalid configuration", "SUSPECTED")
                elif isinstance(target, str) and target in persisted_ids:
                    finding("invalid_target", sid, "A GO_TO cannot target a non-executable note", "SUSPECTED")
                else:
                    finding("missing_target", sid, f"target_step_id {target!r} does not identify an exported step", "SUSPECTED")
            elif kind == "run":
                target_type = step.get("target_type")
                target_id = step.get("target_id")
                if target_type == "exit":
                    target = boundary("exit", sid)
                    edge(sid, target, "exit", "target_type=exit")
                elif target_type == "playbook":
                    if not isinstance(target_id, str) or not target_id:
                        finding("missing_target", sid, "Child target_id is missing", "SUSPECTED")
                        continue
                    target = boundary("child", str(target_id))
                    edge(sid, target, "call", "target_type=playbook; target_id")
                    edge(target, following, "if child completes and returns", "lexical continuation after child return")
                    finding("child_boundary", sid, "Child internals and alternate exits are not expanded; inspect the child export and return traces")
                elif target_type in {"action", "mcp_tool", "handoff", "sms", "csat_survey", "clear_authentication", "collaborator_ask", "collaborator_bring_in"}:
                    if target_type in {"action", "mcp_tool", "handoff", "collaborator_ask", "collaborator_bring_in"} and (not isinstance(target_id, str) or not target_id):
                        finding("missing_target", sid, "External target_id is missing", "SUSPECTED")
                        continue
                    target = boundary(str(target_type), str(target_id))
                    edge(sid, target, "invoke", "target_type and target_id")
                    finding("external_boundary", sid, "External outcome and error behavior require runtime evidence")
                    if target_type not in {"handoff", "collaborator_bring_in"}:
                        edge(target, following, "if execution continues", "lexical continuation on successful run")
                else:
                    finding("unsupported_type", sid, f"Unrecognized run target_type {target_type!r}; no continuation inferred")
            elif kind in {"ask", "set", "send", "say", "reason"}:
                edge(sid, following, "configured continuation", "ordered steps, branch rejoin and section fallthrough")
                if kind == "ask":
                    finding("ask_runtime", sid, "ASK retry, fallback, existing-value skip and off-script transitions need verified runtime evidence; unset fields remain absent")
                if kind == "reason":
                    finding("reason_runtime", sid, "Reason instructions may invoke entities dynamically; those transitions are not inferred from prose")
            else:
                finding("unsupported_type", sid, f"Unrecognized step type {kind!r}; no continuation inferred")

    persisted_ids = set(ids)
    persisted_ids.remove(end)
    types = {node["id"]: node["type"] for node in graph["nodes"]}
    executable = [step for step in sequences if step["type"] != "note"]
    if not executable:
        raise ValueError("Export contains no executable steps")
    graph["entry"] = executable[0]["id"]
    connect(sequences, end)
    adjacency = {node["id"]: [] for node in graph["nodes"]}
    for item in graph["edges"]:
        adjacency[item["from"]].append(item["to"])
    visited = set()
    pending = [graph["entry"]]
    while pending:
        current = pending.pop()
        if current not in visited:
            visited.add(current)
            pending.extend(adjacency[current])
    for sid in sorted(sid for sid in persisted_ids - visited if types[sid] != "note"):
        finding("unreachable", sid, "No path from entry in the extracted graph; unknown or external transitions may change runtime reachability", "SUSPECTED")
    colors = {}
    for start in adjacency:
        if start in colors:
            continue
        colors[start] = 1
        stack = [(start, iter(adjacency[start]))]
        while stack:
            current, children = stack[-1]
            child = next(children, None)
            if child is None:
                colors[current] = 2
                stack.pop()
            elif colors.get(child) == 1:
                finding("cycle", current, f"Structural cycle edge to {child}; verify progress and a safe exit", "SUSPECTED")
            elif child not in colors:
                colors[child] = 1
                stack.append((child, iter(adjacency[child])))
    return graph


def cell(value):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return html.escape(text, quote=True).replace("|", "&#124;").replace("\n", "<br>").replace("\r", "").replace("`", "&#96;")


def mermaid_label(value):
    return "".join(char if char.isascii() and (char.isalnum() or char in " _-.:/") else f"#{ord(char)};" for char in str(value))


def render(graph):
    names = {node["id"]: f"n{index}" for index, node in enumerate(graph["nodes"])}
    lines = ["# Persisted playbook graph", "", "Configuration structure only. All edges are UNTESTED. Runtime coverage is not established.", "", "| Metadata | Value |", "| --- | --- |"]
    lines.extend(f"| {cell(key)} | {cell(value)} |" for key, value in graph.get("metadata", {}).items())
    lines.extend(["", f"Sections: {cell(graph['sections'])}", "", f"Playbook settings: {cell(graph['playbook_config'])}", "", "```mermaid", "flowchart TD"])
    for node in graph["nodes"]:
        label = mermaid_label(f"{node['id']} ({node['type']})")
        lines.append(f'  {names[node["id"]]}["{label}"]')
    for item in graph["edges"]:
        lines.append(f'  {names[item["from"]]} -->|"{mermaid_label(item["event"])}"| {names[item["to"]]}')
    lines.extend(["```", "", "## Nodes", "", "Config retains explicit values only. Absent fields are unset. Variable references and writes remain in their source fields.", "", "| Step ID | Type | Source | Config |", "| --- | --- | --- | --- |"])
    lines.extend(f"| {cell(node['id'])} | {cell(node['type'])} | {cell(node['source'])} | {cell(node['config'])} |" for node in graph["nodes"])
    lines.extend(["", "## Edges", "", "| From | Event | Condition | To | Evidence | Coverage |", "| --- | --- | --- | --- | --- | --- |"])
    lines.extend(f"| {cell(item['from'])} | {cell(item['event'])} | {cell(item['condition'])} | {cell(item['to'])} | {cell(item['evidence'])} | UNTESTED |" for item in graph["edges"])
    lines.extend(["", "## Structural findings and open evidence", "", "| Status | Code | Step | Detail |", "| --- | --- | --- | --- |"])
    lines.extend(f"| {cell(item['status'])} | {cell(item['code'])} | {cell(item['step'])} | {cell(item['detail'])} |" for item in graph["findings"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Convert one complete persisted V2 playbook export into a structural graph, tables and findings.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--identity", help="Required when the export omits the playbook identity")
    parser.add_argument("--state", choices=("live", "draft"), required=True)
    parser.add_argument("--revision", required=True, help="Source revision or changeset identity")
    parser.add_argument("--channel", required=True)
    parser.add_argument("--captured-at", help="Export capture time in ISO 8601 form, when known")
    args = parser.parse_args()
    try:
        source = args.input.read_bytes()
        graph = convert(json.loads(source))
        identity = args.identity or graph["identity"]
        if not identity:
            raise ValueError("Export has no playbook identity; supply --identity")
        if args.input.resolve() in {(args.output_dir / name).resolve() for name in ("graph.json", "graph.md")}:
            raise ValueError("Output files would overwrite the input export; choose a separate output directory")
        graph["metadata"] = {"identity": identity, "state": args.state, "revision": args.revision,
                             "channel": args.channel, "captured_at": args.captured_at or "OPEN - export capture time not supplied",
                             "generated_at": datetime.now(timezone.utc).isoformat(),
                             "source": args.input.name, "sha256": hashlib.sha256(source).hexdigest()}
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (args.output_dir / "graph.md").write_text(render(graph), encoding="utf-8")
    except (OSError, ValueError, RecursionError) as error:
        parser.exit(2, f"Graph conversion failed: {error}\n")
    print(f"Saved {len(graph['nodes'])} nodes, {len(graph['edges'])} edges and {len(graph['findings'])} findings to {args.output_dir}")


if __name__ == "__main__":
    main()
