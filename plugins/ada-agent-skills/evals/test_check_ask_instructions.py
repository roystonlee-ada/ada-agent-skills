#!/usr/bin/env python3
"""Tests for author-playbook/scripts/check_ask_instructions.py.

Run: python3 evals/test_check_ask_instructions.py
"""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = (pathlib.Path(__file__).resolve().parent.parent
          / "skills" / "author-playbook" / "scripts" / "check_ask_instructions.py")
spec = importlib.util.spec_from_file_location("check_ask_instructions", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

REASON = "6650aa000000000000000001"
REFUND = "6650aa0000000000000000a1"


def ask(**extra):
    step = {"id": "ask-reason", "type": "ask", "ask_mode": "reasoning", "variable_id": REASON,
            "instruction": "the reason the customer wants a refund", "max_reask_attempts": 0}
    step.update(extra)
    return step


def action(step_id="run-refund"):
    return {"id": step_id, "type": "run", "target_type": "action", "target_id": REFUND}


def null_check(steps):
    return {"id": "guard", "type": "if_else", "branches": [
        {"conditions": [{"left_operand": REASON, "comparison_operator": "is null",
                         "right_operand": None}],
         "steps": [{"type": "run", "target_type": "handoff", "target_id": "h1"}]},
        {"conditions": [], "steps": steps}]}


def playbook(*steps):
    return {"name": "Refund", "sections": [{"title": "Main", "steps": list(steps)}]}


def a4(doc):
    return [(a["id"], var, act["id"]) for a, var, act in check.unguarded_actions(doc)]


class ZeroReaskFallThrough(unittest.TestCase):
    def test_flags_action_with_no_null_check(self):
        self.assertEqual(a4(playbook(ask(), action())),
                         [("ask-reason", REASON, "run-refund")])

    def test_null_check_before_action_clears_it(self):
        self.assertEqual(a4(playbook(ask(), null_check([action()]))), [])

    def test_blank_check_counts_as_a_guard(self):
        guard = null_check([action()])
        guard["branches"][0]["conditions"] = [
            {"left_operand": REASON, "comparison_operator": "is", "right_operand": ""}]
        self.assertEqual(a4(playbook(ask(), guard)), [])

    def test_check_inside_nested_group_counts(self):
        guard = null_check([action()])
        cond = guard["branches"][0].pop("conditions")
        guard["branches"][0].update(
            {"conditions": [], "operator": "OR", "groups": [{"operator": "AND", "conditions": cond}]})
        self.assertEqual(a4(playbook(ask(), guard)), [])

    def test_check_on_another_variable_does_not_count(self):
        guard = null_check([action()])
        guard["branches"][0]["conditions"][0]["left_operand"] = "other"
        self.assertEqual(len(a4(playbook(ask(), guard))), 1)

    def test_fallback_value_clears_it(self):
        self.assertEqual(a4(playbook(ask(fallback_value="not given"), action())), [])

    def test_reask_cap_above_zero_is_not_this_rule(self):
        self.assertEqual(a4(playbook(ask(max_reask_attempts=2), action())), [])
        self.assertEqual(a4(playbook(ask(max_reask_attempts=None), action())), [])

    def test_no_later_action(self):
        self.assertEqual(a4(playbook(ask(), {"type": "send", "message": "Thanks"})), [])

    def test_multi_input_ask_checks_each_variable(self):
        step = ask(inputs=[{"variable_id": REASON},
                           {"variable_id": "email", "fallback_value": "none"}])
        del step["variable_id"]
        self.assertEqual(a4(playbook(step, action())), [("ask-reason", REASON, "run-refund")])

    def test_action_in_another_playbook_is_not_linked(self):
        doc = {"changes": [{"fields": playbook(ask())},
                           {"fields": playbook(action())}]}
        self.assertEqual(a4(doc), [])

    def test_cli_prints_a4_and_keeps_exit_0(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(playbook(ask(), action()), f)
        out = subprocess.run([sys.executable, str(SCRIPT), f.name], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("WARN A4", out.stdout)
        self.assertIn("run-refund", out.stdout)


class AcceptAnyWording(unittest.TestCase):
    def test_accept_any_is_now_a8(self):
        rules = [r for _, r, _ in check.problems(ask(instruction="Accept any answer and move on."))]
        self.assertIn("A8", rules)
        self.assertNotIn("A4", rules)


if __name__ == "__main__":
    unittest.main()
