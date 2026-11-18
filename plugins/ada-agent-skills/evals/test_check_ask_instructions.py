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


STORE_ANY = ("Ask in ONE short sentence whether that sorts it out.\n\nCAPTURE: store the "
             "customer's next message exactly as they typed it, whatever it says. Never repeat "
             "this question and never offer a list of options.")


def rules(**extra):
    return [r for _, r, _ in check.problems(ask(**extra))]


class StoreAnyReply(unittest.TestCase):
    def test_store_any_reply_is_not_flagged(self):
        self.assertEqual(rules(instruction="Accept any answer and move on."), [])
        self.assertEqual(rules(instruction=STORE_ANY), [])

    def test_store_any_reply_still_gets_a4(self):
        # A non-answer ("thanks, that's all") is classed did_not_answer and leaves the
        # variable empty even when the instruction says to store any reply.
        self.assertEqual(a4(playbook(ask(instruction=STORE_ANY), action())),
                         [("ask-reason", REASON, "run-refund")])
        self.assertEqual(a4(playbook(ask(instruction="Accept any answer."), action())),
                         [("ask-reason", REASON, "run-refund")])

    def test_store_any_reply_is_cleared_by_a_null_check(self):
        self.assertEqual(a4(playbook(ask(instruction=STORE_ANY), null_check([action()]))), [])

    def test_cli_names_store_any_in_the_a4_line(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(playbook(ask(instruction=STORE_ANY), action()), f)
        out = subprocess.run([sys.executable, str(SCRIPT), f.name], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("storing any reply does not cover a non-answer", out.stdout)


class RepeatTheQuestion(unittest.TestCase):
    def test_asking_to_repeat_fails(self):
        self.assertIn("A3", rules(instruction="If unclear, repeat the question."))
        self.assertIn("A3", rules(instruction="Do it now. Ask the same question again."))

    def test_negated_repeat_passes(self):
        for text in (STORE_ANY, "Do not repeat the question as it was.",
                     "Avoid asking the same question again; reword it."):
            self.assertNotIn("A3", rules(instruction=text), text)

    def test_negation_in_an_earlier_sentence_does_not_count(self):
        self.assertIn("A3", rules(instruction="Never guess. Repeat the question."))


class BareTrueFalse(unittest.TestCase):
    def test_negative_condition_does_not_negate_output(self):
        for text in ("If the customer does not confirm, write false.",
                     "If they do not agree, output false."):
            self.assertIn("A9", rules(instruction=text), text)

    def test_unrelated_prohibition_does_not_negate_output(self):
        for text in ("Do not ask again, write exactly true if they confirm.",
                     "Never guess and output false if they decline."):
            self.assertIn("A9", rules(instruction=text), text)

    def test_directly_negated_output_passes(self):
        for text in ("Do not output true or false.",
                     "Don't ever write true in your reply.",
                     "Never directly respond with false."):
            self.assertNotIn("A9", rules(instruction=text), text)

    def test_write_the_word_is_flagged(self):
        for text in ("Write exactly true if they confirm the cancellation, otherwise false.",
                     "Respond with only 'false' when they say no.",
                     "Output true when the customer agrees."):
            self.assertIn("A9", rules(instruction=text), text)

    def test_save_wording_passes(self):
        for text in ("Save true if they confirm the cancellation, otherwise save false. "
                     "Never say true or false to the customer.",
                     "Never write true or false in your reply.",
                     STORE_ANY):
            self.assertNotIn("A9", rules(instruction=text), text)


class WorkedOrNot(unittest.TestCase):
    def yes_no(self, instruction):
        return rules(instruction=instruction, accepted_values=["yes", "no"], fallback_value="no")

    def test_already_answered_is_not_a_worked_question(self):
        text = ("Do not ask something they have already answered. Capture whether they have "
                "already submitted a claim - 'yes' if they have, 'no' if they have not.")
        self.assertNotIn("A2", self.yes_no(text))

    def test_did_it_work_without_problem_mapping_fails(self):
        text = "Ask whether that answered their question. 'yes' if it did, 'no' if they want more."
        self.assertIn("A2", self.yes_no(text))


if __name__ == "__main__":
    unittest.main()
