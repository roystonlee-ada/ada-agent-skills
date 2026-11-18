import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "playbook_graph.py"


def load_converter():
    spec = importlib.util.spec_from_file_location("playbook_graph", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def playbook(steps):
    return {"id": "example", "version": 2, "sections": [{"id": "main", "steps": steps}]}


class GraphTests(unittest.TestCase):
    def convert(self, data):
        self.assertTrue(SCRIPT.exists(), "The persisted playbook graph converter is missing")
        return load_converter().convert(data)

    def pairs(self, graph):
        return {(edge["from"], edge["to"]) for edge in graph["edges"]}

    def test_nested_branch_rejoins_and_goto_enters_nested_continuation(self):
        graph = self.convert(playbook([
            {"id": "jump", "type": "go_to", "target_step_id": "inside"},
            {"id": "choice", "type": "if_else", "branches": [
                {"conditions": [{"left_operand": "answer", "comparison_operator": "is_set"}], "steps": [{"id": "inside", "type": "send"}]},
                {"conditions": [], "steps": []},
            ]},
            {"id": "after", "type": "send"},
        ]))
        self.assertIn(("jump", "inside"), self.pairs(graph))
        self.assertIn(("inside", "after"), self.pairs(graph))
        self.assertIn(("choice", "after"), self.pairs(graph))
        self.assertNotIn(("jump", "choice"), self.pairs(graph))

    def test_missing_targets_cycles_and_unreachable_steps(self):
        graph = self.convert(playbook([
            {"id": "loop", "type": "go_to", "target_step_id": "loop"},
            {"id": "broken", "type": "go_to", "target_step_id": "absent"},
        ]))
        codes = {finding["code"] for finding in graph["findings"]}
        self.assertTrue({"cycle", "missing_target", "unreachable"} <= codes)
        self.assertNotIn("absent", {node["id"] for node in graph["nodes"]})

    def test_contract_keeps_unset_distinct_and_does_not_invent_retry_edges(self):
        graph = self.convert(playbook([
            {"id": "question", "type": "ask", "instructions": "Which option?", "inputs": [
                {"variable_id": "answer", "accepted_values": ["a", "b"], "fallback_value": "unknown"}
            ]},
            {"id": "done", "type": "send"},
        ]))
        question = next(node for node in graph["nodes"] if node["id"] == "question")
        self.assertEqual(question["config"]["inputs"][0]["fallback_value"], "unknown")
        self.assertNotIn("max_retries", question["config"])
        self.assertFalse(any(edge["from"] == edge["to"] == "question" for edge in graph["edges"]))
        self.assertIn("ask_runtime", {item["code"] for item in graph["findings"]})

    def test_duplicate_ids_and_header_only_sections_are_rejected(self):
        self.assertTrue(SCRIPT.exists(), "The persisted playbook graph converter is missing")
        converter = load_converter()
        for data in [playbook([{"id": "x", "type": "send"}, {"id": "x", "type": "send"}]),
                     {"sections": [{"id": "main", "title": "Header only"}]}]:
            with self.assertRaises(ValueError):
                converter.convert(data)

    def test_unknown_type_is_an_open_boundary(self):
        graph = self.convert(playbook([
            {"id": "new", "type": "future_step"}, {"id": "later", "type": "send"}
        ]))
        self.assertNotIn(("new", "later"), self.pairs(graph))
        self.assertIn("unsupported_type", {item["code"] for item in graph["findings"]})

    def test_child_returns_but_exit_and_handoff_do_not_fall_through(self):
        graph = self.convert(playbook([
            {"id": "child", "type": "run", "target_type": "playbook", "target_id": "other"},
            {"id": "stop", "type": "run", "target_type": "exit"},
            {"id": "handoff", "type": "run", "target_type": "handoff", "target_id": "team"},
            {"id": "later", "type": "send"},
        ]))
        child_boundary = next(item["to"] for item in graph["edges"] if item["from"] == "child")
        self.assertIn((child_boundary, "stop"), self.pairs(graph))
        self.assertNotIn(("stop", "handoff"), self.pairs(graph))
        self.assertNotIn(("handoff", "later"), self.pairs(graph))

    def test_notes_are_retained_but_not_executed(self):
        graph = self.convert(playbook([
            {"id": "annotation", "type": "note", "body": "Builder text"},
            {"id": "first", "type": "send"},
            {"id": "another-note", "type": "note"},
            {"id": "last", "type": "send"},
        ]))
        self.assertEqual(graph["entry"], "first")
        self.assertIn(("first", "last"), self.pairs(graph))
        self.assertFalse(any("note" in source or "note" in target for source, target in self.pairs(graph)))
        self.assertEqual(len([node for node in graph["nodes"] if node["type"] == "note"]), 2)

    def test_sections_flat_exports_and_mcp_single_entity(self):
        source = {"id": "one", "version": 2, "sections": [
            {"id": "a", "steps": [{"id": "first", "type": "send"}]},
            {"id": "b", "steps": [{"id": "last", "type": "send"}]},
        ]}
        for wrapped in [source, {"entities": [source]}, {"data": source}, source["sections"],
                        [{"id": "first", "type": "send"}, {"id": "last", "type": "send"}]]:
            with self.subTest(wrapped=wrapped):
                self.assertIn(("first", "last"), self.pairs(self.convert(wrapped)))

    def test_ambiguous_and_incomplete_exports_fail_closed(self):
        self.assertTrue(SCRIPT.exists(), "The persisted playbook graph converter is missing")
        converter = load_converter()
        for data in [[], {"entities": [playbook([]), playbook([])]},
                     {"sections": [{"steps": [{"type": "send"}]}]},
                     {"version": 1, "steps": [{"id": "old", "type": "send"}]},
                     {**playbook([{"id": "first", "type": "send"}]), "next_cursor": "page-2"}]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                converter.convert(data)

    def test_preserves_section_identity_and_inherited_deviation_settings(self):
        source = playbook([{"id": "first", "type": "ask", "variable_id": "answer"}])
        source["on_off_script"] = "allow"
        graph = self.convert(source)
        self.assertEqual(graph["sections"][0]["id"], "main")
        self.assertEqual(graph["playbook_config"]["on_off_script"], "allow")
        self.assertNotIn("on_off_topic", graph["playbook_config"])

    def test_group_conditions_and_builtin_run_continuations(self):
        graph = self.convert(playbook([
            {"id": "choice", "type": "if_else", "branches": [
                {"groups": [{"operator": "AND", "conditions": [{"left_operand": "answer"}]}],
                 "steps": [{"id": "sms", "type": "run", "target_type": "sms"}]},
                {"steps": []},
            ]},
            {"id": "clear", "type": "run", "target_type": "clear_authentication"},
            {"id": "survey", "type": "run", "target_type": "csat_survey"},
            {"id": "done", "type": "send"},
        ]))
        self.assertFalse(any(item["code"] == "unsupported_type" for item in graph["findings"]))
        self.assertTrue(any(edge["to"] == "clear" and edge["from"] != "choice" for edge in graph["edges"]))
        self.assertTrue(any(edge["to"] == "done" for edge in graph["edges"]))

    def test_output_directory_cannot_replace_the_source(self):
        self.assertTrue(SCRIPT.exists(), "The persisted playbook graph converter is missing")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "graph.json"
            content = json.dumps(playbook([{"id": "first", "type": "send"}]))
            source.write_text(content)
            result = subprocess.run([sys.executable, str(SCRIPT), str(source), "--output-dir", str(root),
                                     "--state", "live", "--revision", "r1", "--channel", "chat"], capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(source.read_text(), content)

    def test_note_targets_and_missing_external_targets_are_flagged(self):
        graph = self.convert(playbook([
            {"id": "jump", "type": "go_to", "target_step_id": "annotation"},
            {"id": "annotation", "type": "note"},
            {"id": "action", "type": "run", "target_type": "action"},
        ]))
        self.assertIn(("invalid_target", "jump"), {(item["code"], item["step"]) for item in graph["findings"]})
        self.assertIn(("missing_target", "action"), {(item["code"], item["step"]) for item in graph["findings"]})

    def test_excessive_nesting_is_rejected(self):
        steps = [{"id": "leaf", "type": "send"}]
        for index in range(12):
            steps = [{"id": f"branch-{index}", "type": "if_else", "branches": [
                {"conditions": [{"left_operand": "answer"}], "steps": steps}, {"steps": []}
            ]}]
        self.assertTrue(SCRIPT.exists(), "The persisted playbook graph converter is missing")
        with self.assertRaises(ValueError):
            load_converter().convert(playbook(steps))

    def test_cli_writes_matching_json_and_escaped_mermaid(self):
        self.assertTrue(SCRIPT.exists(), "The persisted playbook graph converter is missing")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            source.write_text(json.dumps(playbook([{"id": "x[]", "type": "send", "instructions": "hello | <tag>"}])))
            result = subprocess.run([
                sys.executable, str(SCRIPT), str(source), "--output-dir", str(root / "out"),
                "--state", "draft", "--revision", "example-r1", "--channel", "chat",
            ], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            graph = json.loads((root / "out" / "graph.json").read_text())
            report = (root / "out" / "graph.md").read_text()
            self.assertEqual(graph["metadata"]["revision"], "example-r1")
            self.assertIn("```mermaid", report)
            self.assertIn("flowchart TD", report)
            self.assertNotIn('x[] -->', report)
            self.assertEqual(graph["nodes"][0]["id"], "x[]")


if __name__ == "__main__":
    unittest.main()
