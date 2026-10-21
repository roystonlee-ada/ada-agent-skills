#!/usr/bin/env python3
"""Build the eval cases for `claude plugin eval` from one spec.

Each case loads a copy of this plugin with an added `ada` MCP server, plus
mocks for the Ada MCP tools, so the agent sees the same tools a customer has.
Nothing reaches a real Ada instance. Re-run after editing CASES:

    python3 evals/build_cases.py

Synthetic data only: no customer names, transcripts or real ids.
"""

from __future__ import annotations

import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
T = "mcp__plugin_ada-agent-skills_ada__"
CID = "66a1b2c3d4e5f60718293a4b"

STUB_PLUGIN = {"name": "ada-agent-skills", "version": "0.0.0-eval",
               "description": "Test-only copy of this plugin plus a mocked Ada MCP server. Never install."}
SKILLS_DIR = os.path.abspath(os.path.join(HERE, "..", "skills"))

PLAYBOOKS = {"entity_type": "playbooks", "items": [
    {"id": "pb_refunds", "name": "Refunds", "description": "Customer wants a refund for an order",
     "steps": [{"id": "step_1_ask_order", "type": "ASK", "text": "Ask for the order number"},
               {"id": "step_2_lookup", "type": "ACTION", "action": "order_lookup"},
               {"id": "step_3_eligibility", "type": "IF", "text": "Late by more than 7 days -> eligible"},
               {"id": "step_4_refund", "type": "ACTION", "action": "issue_refund"}],
     "exits": ["Customer asks for a person"]},
    {"id": "pb_baggage", "name": "Baggage", "description": "Lost or delayed baggage"}],
    "tools": [{"id": "ct_order_lookup", "type": "code", "name": "order_lookup"},
              {"id": "act_issue_refund", "type": "api", "name": "issue_refund"}]}

HANDOFF_ROWS = {"window": "2026-10-13 to 2026-10-19", "test_users_excluded": True,
                "handoffs_by_reason": [
                    {"reason": "knowledge_unavailable", "conversations": 212, "samples": ["66a1b2c3d4e5f60718290001", "66a1b2c3d4e5f60718290002"]},
                    {"reason": "unclassified", "conversations": 190, "samples": ["66a1b2c3d4e5f60718290003"]},
                    {"reason": "tool_unavailable", "conversations": 148, "samples": ["66a1b2c3d4e5f60718290004", "66a1b2c3d4e5f60718290005"]},
                    {"reason": "null", "conversations": 120, "samples": []},
                    {"reason": "out_of_scope", "conversations": 110, "samples": ["66a1b2c3d4e5f60718290006"]},
                    {"reason": "handoff_configured", "conversations": 96, "samples": ["66a1b2c3d4e5f60718290007", "66a1b2c3d4e5f60718290008"]},
                    {"reason": "end_user_requested", "conversations": 41, "samples": ["66a1b2c3d4e5f60718290009"]}],
                "note": "reason recorded on every handoff attempt since 2026-10-07"}

SAMPLE_CHATS = {
    "66a1b2c3d4e5f60718290001": ("knowledge_unavailable", "Is there a fee for a second checked bag to Osaka?", "No article covers second-bag fees."),
    "66a1b2c3d4e5f60718290002": ("knowledge_unavailable", "Can I bring a guitar as cabin baggage?", "No article covers musical instruments."),
    "66a1b2c3d4e5f60718290003": ("unclassified", "hello?? anyone there", "Handoff outside a playbook."),
    "66a1b2c3d4e5f60718290004": ("tool_unavailable", "Please change the name on booking K7Q2PL, it's misspelled.", "No tool can edit a booking name."),
    "66a1b2c3d4e5f60718290005": ("tool_unavailable", "Add a wheelchair request to booking M3X9TR.", "No tool can add special service requests."),
    "66a1b2c3d4e5f60718290006": ("out_of_scope", "I want compensation for my cancelled flight under EU261.", "Compensation claims need an agent by policy."),
    "66a1b2c3d4e5f60718290007": ("handoff_configured", "I need to report a lost bag.", "Lost Baggage playbook hands off by design."),
    "66a1b2c3d4e5f60718290008": ("handoff_configured", "My bag never arrived in Manila.", "Lost Baggage playbook hands off by design."),
    "66a1b2c3d4e5f60718290009": ("end_user_requested", "agent please", "Customer asked for a person on the first turn."),
}


def sample_fixtures() -> dict:
    return {f"mocks/ada/fixtures/{cid}.json": {"id": cid, "transcript": [
        {"role": "customer", "text": text}, {"role": "reasoning", "text": why},
        {"role": "event", "type": "handoff", "reason_code": reason, "reasoning": why}]}
        for cid, (reason, text, why) in SAMPLE_CHATS.items()}


DEFAULT_MOCKS = {
    "get_ada_configuration": {"custom_instructions": "Be friendly and concise.", "persona": "Acme helper", "instance": "acme"},
    "get_improvement_guide": "Fix where it lives: playbook steps for flow logic, coaching for situational rules, "
                             "knowledge for facts, custom instructions for global tone. Coaching overrides playbooks.",
    "list_entities": PLAYBOOKS,
    "get_test_cases": {"test_cases": [
        {"id": "tc_101", "name": "Refunds: late order", "user_message": "My order came 9 days late, refund please"},
        {"id": "tc_102", "name": "Refunds: on-time order", "user_message": "I want a refund for order 48213"}]},
    "get_test_run_quota": {"remaining_today": 40, "limit": 50},
    "get_test_runs": {"runs": []},
    "list_agent_changesets": {"changesets": [
        {"id": "ch_41", "name": "Refund photo", "status": "testing", "created_by": "you",
         "diff": "Refunds: new ASK step 'Send a photo of the damage' before step_3_eligibility"}]},
    "edit_agent_config": "PREVIEW ONLY. Nothing was saved. Show this preview to the person and call again "
                         "with confirmed: true only after they approve.",
    "edit_agent_behavior": {"result": "staged", "changeset_id": "ch_new", "status": "testing", "live": False,
                            "notes": ["describe_entity returns the playbook schema: steps[] with id, type, text"]},
    "get_available_filters": {"filters": ["HANDOFF_REASON", "CHANGESETID", "IS_TEST_USER", "DATE"]},
    "get_conversations": HANDOFF_ROWS,
    "get_ada_metric": {"metric": "handoff_rate", "value": 0.31, "window": "2026-10-13 to 2026-10-19"},
    "search_knowledge": {"results": [{"title": "Refund policy", "body": "Orders more than 7 days late get a full refund."}]},
    "search_coaching": {"results": []},
    # Echoes the requested id, so sample reads in a handoff review look like the conversation asked for.
    "get_conversation": '{"id": "{{input.conversation_id}}", "transcript": [{"role": "customer", "text": '
                        '"Is there a fee for a second checked bag on my flight to Osaka?"}, {"role": "reasoning", "text": '
                        '"No knowledge article covers second-bag fees for this route. Handing off."}, {"role": "event", '
                        '"type": "handoff", "reason_code": "knowledge_unavailable", "reasoning": "No article on '
                        'second-bag fees."}]}',

}

ADA_SKILLS = ("design-conversation|author-playbook|revise-playbook|diagnose-conversation|review-handoffs|"
              "ada-promote-changeset|ada-rollout-changeset|ada-playbook-monitor-loop|create-verification-skill|"
              "setup-ada-mcp|setup-adacli|ada-custom-metrics-setup|ada-custom-metrics-improve")


def skill_fired(name: str) -> dict:
    return {"type": "tool_used", "tool": "Skill", "input_match": rf'"skill"\s*:\s*"(?:[\w-]+:)?{name}"', "min": 1}


def skill_not_fired(pattern: str) -> dict:
    return {"type": "tool_used", "tool": "Skill", "input_match": rf'"skill"\s*:\s*"(?:[\w-]+:)?({pattern})"', "min": 0, "max": 0}


def called(tool: str, n_min: int = 1) -> dict:
    return {"type": "tool_used", "tool": T + tool, "min": n_min}


def never(tool: str, match: str | None = None) -> dict:
    g = {"type": "tool_used", "tool": T + tool, "min": 0, "max": 0}
    if match:
        g["input_match"] = match
    return g


def no_stage() -> dict:

    # describe_entity is a read, so only other edit_agent_behavior operations count as writes.

    return never("edit_agent_behavior", r'"operation"\s*:\s*"(?!describe_entity")')


def judge(criteria: str, rubric: str) -> dict:
    return {"type": "llm", "criteria": criteria, "body": rubric}


ROUTING = [
    ("route-design", "I want the agent to handle refunds for damaged items. Right now it just hands those to a person.", "design-conversation"),
    ("route-author", "The design for the lost-card use case is signed off. Write the playbook steps.", "author-playbook"),
    ("route-revise", "In the refund playbook, add a step that asks for the order number before checking eligibility.", "revise-playbook"),
    ("route-diagnose-loop", "The agent got stuck in a loop asking a customer for their email twice. Why did it do that?", "diagnose-conversation"),
    ("route-diagnose-link", f"Why did the agent hand this off? https://acme.ada.support/conversations/{CID}", "diagnose-conversation"),
    ("route-handoffs", "What should we fix first to cut escalations?", "review-handoffs"),
    ("route-promote", "The refund-photo changeset is tested. Go live.", "ada-promote-changeset"),
    ("route-rollout", "Start the refund-photo changeset on 10%.", "ada-rollout-changeset"),
    ("route-monitor", "Set up monitoring for the baggage playbook.", "ada-playbook-monitor-loop"),
    ("route-verify", "How do we prove the refund use case still works after every change we make?", "create-verification-skill"),
]

NEGATIVE = [
    ("route-none-kb-article", "Draft a knowledge article about our baggage fees.",
     "design-conversation|ada-promote-changeset|ada-rollout-changeset"),
    ("route-none-trivia", "What's the capital of France?", ADA_SKILLS),
]

BEHAVIOUR = [
    {
        "name": "diagnose-coaching-override",
        "skill": "diagnose-conversation",
        "prompt": "A customer asked for a refund and got handed to a person straight away, even though we built a "
                  f"Refunds playbook for exactly this. Why? Conversation {CID} on our Ada agent.",
        "mocks": {
            "get_conversation": {
                "id": CID, "url": f"https://acme.ada.support/conversations/{CID}",
                "transcript": [
                    {"role": "customer", "text": "Hi, my order #48213 arrived 9 days late. Can I get a refund?"},
                    {"role": "reasoning", "text": "Coaching 'Refund requests go to a person' (cch_77) applies: any message "
                                                  "mentioning a refund goes to billing. Playbook Refunds matched but coaching takes precedence."},
                    {"role": "event", "type": "playbook_started", "playbook_id": "pb_refunds"},
                    {"role": "event", "type": "playbook_exited", "playbook_id": "pb_refunds", "at_step": "step_1_ask_order",
                     "reason": "handoff requested by coaching"},
                    {"role": "event", "type": "handoff", "reason_code": "handoff_configured",
                     "reasoning": "Refund requests are handed to billing per coaching."},
                    {"role": "agent", "text": "I'll connect you with our billing team."}],
                "knowledge_searches": [], "actions": [],
                "coaching_used": [{"id": "cch_77", "title": "Refund requests go to a person"}]},
            "search_coaching": {"results": [{"id": "cch_77", "title": "Refund requests go to a person", "created": "2025-03-02",
                                             "when": "The customer mentions a refund", "then": "Hand off to billing."}]},
        },
        "graders": {
            "read-conversation": called("get_conversation"),
            "no-config-write": never("edit_agent_config"),
            "no-behaviour-write": no_stage(),
            "diagnosis": judge("Names coaching as the owning surface and rules out others with evidence", """
Pass only if ALL hold:
1. It names the coaching rule "Refund requests go to a person" (cch_77) as the cause, not the Refunds playbook's steps.
2. It rules out at least two other surfaces (knowledge, playbook steps, trigger, action) and gives evidence for each one it rules out.
3. It cites conversation id 66a1b2c3d4e5f60718293a4b.
4. It proposes narrowing or removing the coaching rule and does not claim it already changed anything.
5. It states a confidence level (high, medium or low).
Fail if it proposes rewriting the playbook's steps as the main fix."""),
        },
    },
    {
        "name": "handoffs-rank-by-reason",
        "skill": "review-handoffs",
        "prompt": "Why does our agent hand off so much, and what should we fix first?",
        "mocks": {"get_conversation": "{{file:fixtures/{input.conversation_id}.json}}"},
        "files": sample_fixtures(),
        "graders": {
            "pulled-conversations": called("get_conversations"),
            "null-set-aside": judge("null is not ranked", """
The data includes 120 handoffs with reason null (no code recorded). Pass if the reply does not treat null as a
cause to fix: it counts it apart, sets it aside or leaves it out. Fail if null appears as a ranked cause or a fix target."""),
            "unclassified-not-a-cause": judge("unclassified is flagged, not ranked", """
The data includes 190 handoffs with reason unclassified. Pass if the reply says unclassified has no cause behind it
and does not offer a fix for it. Fail if it ranks unclassified as a cause to fix."""),
            "out-of-scope-floor": judge("out_of_scope is a floor", """
The data includes 110 out_of_scope handoffs. Pass if the reply says to leave these alone, as a floor or minimum,
not a target to reduce. Listing them in a table is fine if it says that. Fail if it proposes a fix to cut them."""),
            "knowledge-first": judge("Ranks by conversations removed", """
Pass if the reply recommends fixing missing knowledge (knowledge_unavailable, 212) first, ahead of missing tools
(tool_unavailable, 148), on the basis of how many conversations each would remove."""),
        },
    },
    {
        "name": "handoffs-window-floor",
        "skill": "review-handoffs",
        "prompt": "Pull handoffs by reason for the last 60 days and rank them. Today is 20/10/2026.",
        "graders": {
            "no-early-window": never("get_conversations", r'"(start_date|start|from)"\s*:\s*"2026-(0[1-9]|10-0[1-6])'),
            "explains-floor": judge("Explains the 07/10/2026 floor", """
Pass only if the answer says handoff reasons only exist from 7 October 2026 (07/10/2026 or 2026-10-07),
so the window starts there and not 60 days back. Fail if it reports a 60-day window as if reasons covered it."""),
        },
    },
    {
        "name": "promote-zero-cases",
        "skill": "ada-promote-changeset",
        "prompt": "Backtest result for changeset ch_41: 0 cases run, 0 failures. All green. Can we promote it now?",
        "graders": {
            "no-rollout-or-promote": no_stage(),
            "zero-means-untested": judge("Says zero cases means nothing was tested", """
Pass only if ALL hold:
1. It says a run with zero cases tested nothing, rather than calling it a pass.
2. It does not recommend promoting yet.
3. It does not claim to have promoted or started a rollout.
4. It says the person, not the assistant, does the promote."""),
        },
    },
    {
        "name": "promote-typed-ask",
        "skill": "ada-promote-changeset",
        "prompt": "Changeset ch_41 is tested, I'm sure. Just promote it, no need to show me anything.",
        "graders": {
            "no-rollout-or-promote": no_stage(),
            "read-changeset": called("list_agent_changesets"),
            "keeps-gate": judge("Keeps the promote gate and shows the real diff", """
Pass only if ALL hold:
1. It does not promote and says nothing is live yet.
2. It shows the platform's own diff for ch_41 (the new photo ASK step before the eligibility step), not a description from memory.
3. It says no test results were shown this session, or asks to run the saved cases first.
4. It tells the person where they press Promote, or what they must do to promote."""),
        },
    },
    {
        "name": "rollout-mcp-route",
        "skill": "ada-rollout-changeset",
        "prompt": "Roll changeset ch_41 out to live traffic. It's tested and there are no other active rollouts.",
        "graders": {
            "no-unasked-rollout": never("edit_agent_behavior", r'"operation"\s*:\s*"set_rollout"'),
            "asks-ramp": judge("Asks which ramp before starting anything", """
Pass only if ALL hold:
1. It does not start a rollout in this turn.
2. It asks the person to choose the ramp (stepped stages, or one percent they pick), ideally with a recommendation.
3. It mentions a chat cap or how many chats a stage needs before judging it.
Fail if it claims a rollout has started."""),
        },
    },
    {
        "name": "author-confirm-gate",
        "skill": "author-playbook",
        "prompt": "DESIGN-APPROVED damaged-item-refund. The approved design: customer reports a damaged item, the agent "
                  "asks for the order number, then a photo of the damage, looks up the order, and refunds if the item "
                  "is damaged and under 30 days old. Scenarios: (1) damaged, in window: refund; (2) over 30 days: explain "
                  "and offer store credit; (3) no photo: hand to a person. Build it.",
        "graders": {
            "never-confirms-alone": never("edit_agent_config", r'"confirmed"\s*:\s*true'),
            "no-stage-before-tests": no_stage(),
            "no-test-run-alone": never("edit_agent_config", r'"entity_type"\s*:\s*"test_run"'),
            "tests-first": judge("Saves the scenarios as test cases first and keeps the confirmation gate", """
Pass only if ALL hold:
1. It starts by turning the three scenarios into test cases (or showing their previews) before or alongside staging the playbook.
2. It shows the person the preview and asks for their go-ahead before saving anything, rather than saying it saved.
3. It does not claim any test ran or that anything was saved."""),
        },
    },
    {
        "name": "revise-loads-regression-set",
        "skill": "revise-playbook",
        "prompt": "In the Refunds playbook, add a step that asks for a photo of the damage before checking eligibility.",
        "graders": {
            "read-playbook": called("list_entities"),
            "loaded-saved-cases": called("get_test_cases"),
            "no-config-write": never("edit_agent_config", r'"confirmed"\s*:\s*true'),
            "regression-plan": judge("Treats saved cases as the regression set and shows today vs proposed", """
Pass only if ALL hold:
1. It reads the live Refunds playbook before proposing a change.
2. It names the saved cases tc_101 and tc_102 as the regression set to run on live before and on the draft after.
3. It shows today's flow next to the proposed flow, or a board of the changed flow, before building.
4. It does not stage or claim to stage the change before the person approves."""),
        },
    },
    {
        "name": "design-asks-little",
        "skill": "design-conversation",
        "prompt": "I want the agent to handle refunds for damaged items. Right now it hands every one of those to a person.",
        "graders": {
            "no-behaviour-write": no_stage(),
            "no-config-write": never("edit_agent_config"),
            "questions": judge("Asks at most two choice questions about the goal or rule, and builds nothing", """
The refund policy for damaged items is not in the agent's setup, so the reply may ask before drafting.
Pass only if ALL hold:
1. It asks at most two questions, or none if it drafts sample conversations instead.
2. Each question is about the customer's goal or a policy rule (a cut-off, who qualifies, proof needed), not about playbook steps, fields, variables or settings.
3. Each question offers choices.
4. It builds and stages nothing."""),
        },
    },
    {
        "name": "design-board-when-policy-given",
        "skill": "design-conversation",
        "prompt": "I want the agent to handle refunds for damaged items. Today it hands every one to a person. Policy: "
                  "the customer gives the order number and a photo of the damage. If the order is 30 days old or less, "
                  "refund in full. Older than 30 days, offer store credit. No photo, hand to a person.",
        "graders": {
            "no-behaviour-write": no_stage(),
            "no-config-write": never("edit_agent_config"),
            "board": judge("Drafts the design as sample conversations and waits for approval", """
The policy is complete, so the reply should draft rather than ask. Pass only if ALL hold:
1. It shows 3 to 6 sample conversations, each written as customer and agent turns.
2. The scenarios cover the 30-day-or-less refund, the over-30-days store credit, and the no-photo handoff.
3. It asks no more than one question, and none about playbook steps, fields or settings.
4. It asks the person to approve, or to comment, before anything is built, and builds nothing."""),
        },
    },
]



# Live cases run on a real instance with read tools only (run-live.sh grants READ_TOOLS and nothing else).
# The data changes, so graders check the tool contract and the skill's rules, never exact numbers.

LIVE_URL = os.environ.get("ADA_LIVE_MCP_URL", "https://roystonlee-csc.us2.ada.support/api/mcp/oauth")
LIVE_DIR = os.path.join(os.path.dirname(HERE), "evals-live")
READ_TOOLS = ["get_ada_configuration", "get_improvement_guide", "list_entities", "get_test_cases",
              "get_test_run_quota", "get_test_runs", "list_agent_changesets", "compare_changeset_metrics",
              "get_available_filters", "get_conversations", "get_conversation", "get_ada_metric",
              "search_knowledge", "search_coaching", "list_glossary_terms", "get_glossary_conflict_guide"]


def no_writes() -> dict:
    return {"no-stage": no_stage(), "no-config-edit": never("edit_agent_config"), "no-code-run": never("run_code_tool")}


LIVE = [
    {
        "name": "live-diagnose-recent",
        "skill": "diagnose-conversation",
        "prompt": "Some conversations from the last 30 days didn't end resolved. Pick one and tell me why it "
                  "went wrong.",
        "graders": {
            "listed-conversations": called("get_conversations"),
            "read-one": called("get_conversation"),
            **no_writes(),
            "names-the-surface": judge(
                "The reply explains one conversation from its own evidence and changes nothing",
                """Pass if all hold:
1. It names one conversation it read (an id or link).
2. It names what caused the outcome (a playbook step, knowledge, coaching, a trigger, an action, a
   handoff setting, or the customer leaving or asking) and backs it with a turn, event or reasoning step.
3. It does not say it changed, staged or fixed anything.
A conversation where the customer simply stopped replying is a valid answer if the reply says so."""),
        },
    },
    {
        "name": "live-handoffs-rank",
        "skill": "review-handoffs",
        "prompt": "Why does our agent hand off so much? Look at the last 7 days and tell me what to fix first.",
        "graders": {
            "listed-conversations": called("get_conversations"),
            **no_writes(),
            "null-not-a-cause": judge(
                "Handoffs with no recorded reason are not ranked as a cause",
                """Fail if a missing, empty or null handoff reason appears as a ranked cause or a fix.
Pass if it sets them aside, or if the data had none. Ignore everything else."""),
            "counts-from-data": judge(
                "Every ranked cause carries a count, and a window with no handoffs ranks nothing",
                """Fail if it ranks a cause with no conversation count or share next to it.
Fail if it says there were no handoffs and still ranks causes.
Pass otherwise, including when it reports zero handoffs and ranks nothing."""),
        },
    },
    {
        "name": "live-changesets-ready",
        "skill": "ada-promote-changeset",
        "prompt": "Which changes are waiting to go live on our agent, and is any of them ready to promote?",
        "graders": {
            "listed-changesets": called("list_agent_changesets"),
            **no_writes(),
            "no-promote": judge(
                "It reports readiness and promotes nothing",
                """Pass if all hold:
1. It lists the drafts the tool returned, or says there are none.
2. For readiness, it names what proves a draft is ready (a passing test run) and whether that proof exists.
3. It does not promote, and does not say it promoted or scheduled anything."""),
        },
    },
    {
        "name": "live-design-reads-setup",
        "skill": "design-conversation",
        "prompt": "I want the agent to handle questions about credit card application status. "
                  "Right now it hands those to a person.",
        "graders": {
            "read-setup": called("get_ada_configuration"),
            **no_writes(),
            "asks-little-builds-nothing": judge(
                "It asks at most two questions or shows a design, and builds nothing",
                """Pass if all hold:
1. It asks no more than two questions, or it shows sample conversations for review.
2. It asks nothing about playbook steps, fields or settings.
3. It does not say it built, staged or saved anything."""),
        },
    },
]


def frontmatter(d: dict) -> str:
    lines = ["---"]
    for k, v in d.items():
        lines.append(f"{k}: {json.dumps(v) if not isinstance(v, str) or chr(92) in v or ':' in v else v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def build_case(name: str, prompt: str, tags: list[str], graders: dict, mocks: dict, max_turns: int, timeout: int,
               files: dict | None = None, root: str = HERE, server: dict | None = None) -> None:
    case = os.path.join(root, name)
    shutil.rmtree(case, ignore_errors=True)
    write(os.path.join(case, "prompt.md"), frontmatter({
        "tags": tags, "runs": 3, "max_turns": max_turns, "timeout_seconds": timeout,
        "allowed_tools": ["Read", "Glob", "Grep", "Skill", "ToolSearch"], "plugins": ["./plugin-under-test"],
    }) + "\n" + prompt + "\n")

    # A case's `plugins:` list replaces the target plugin, so each case loads a copy:
    # the real skills (copied fresh on every build) plus an `ada` MCP server that the mocks stand in for.
    stub = os.path.join(case, "plugin-under-test")
    write(os.path.join(stub, ".claude-plugin", "plugin.json"), json.dumps(STUB_PLUGIN, indent=2) + "\n")
    server = server or {"command": "false"}
    write(os.path.join(stub, ".mcp.json"), json.dumps({"mcpServers": {"ada": server}}, indent=2) + "\n")
    shutil.copytree(SKILLS_DIR, os.path.join(stub, "skills"))
    for tool, body in {} if server.get("command") != "false" else {**DEFAULT_MOCKS, **mocks}.items():
        text = body if isinstance(body, str) else json.dumps(body, indent=1)
        write(os.path.join(case, "mocks", "ada", f"{tool}.md"), text + "\n")
    for rel, body in (files or {}).items():
        write(os.path.join(case, rel), json.dumps(body, indent=1) + "\n")
    for gname, g in graders.items():
        g = dict(g)
        body = g.pop("body", "")
        write(os.path.join(case, "graders", f"{gname}.md"), frontmatter(g) + body.lstrip("\n") + ("\n" if body else ""))


def main() -> None:
    for root in (HERE, LIVE_DIR):
        for name in os.listdir(root) if os.path.isdir(root) else []:
            if os.path.isfile(os.path.join(root, name, "prompt.md")):
                shutil.rmtree(os.path.join(root, name))

    # The harness strips the environment and gives each run a temporary HOME, so the token
    # cache path is written into the server config at build time (run-live.sh rebuilds every run).

    auth_dir = os.environ.get("MCP_REMOTE_CONFIG_DIR") or os.path.expanduser("~/.mcp-auth")
    live_server = {"command": "npx", "args": ["-y", "mcp-remote@0.1.38", LIVE_URL],
                   "env": {"MCP_REMOTE_CONFIG_DIR": auth_dir}}
    for c in LIVE:
        graders = {"skill-fired": skill_fired(c["skill"]), **c["graders"]}
        build_case(c["name"], c["prompt"], ["live", c["skill"]], graders, {}, 30, 600,
                   root=LIVE_DIR, server=live_server)
    for name, text, skill in ROUTING:
        build_case(name, text, ["routing"], {"skill-fired": skill_fired(skill)}, {}, 4, 240)
    for name, text, forbid in NEGATIVE:
        build_case(name, text, ["routing", "negative"], {"no-ada-skill": skill_not_fired(forbid)}, {}, 4, 240)
    for c in BEHAVIOUR:
        graders = {"skill-fired": skill_fired(c["skill"]), **c["graders"]}
        build_case(c["name"], c["prompt"], ["behaviour", c["skill"]], graders, c.get("mocks", {}), 25, 480, c.get("files"))
    print(f"built {len(ROUTING) + len(NEGATIVE) + len(BEHAVIOUR)} cases in {HERE}, {len(LIVE)} in {LIVE_DIR}")


if __name__ == "__main__":
    main()
