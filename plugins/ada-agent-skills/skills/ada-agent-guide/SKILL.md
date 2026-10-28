---
name: ada-agent-guide
description: >
  Routes a vague Ada agent request to the skill that owns its stage. Use when
  the ask names no stage, such as "fix this chat", "this agent feels off",
  "get this use case live", "sort it out", or "where are we on this use case".
  Does no work itself. Skip it when the request names a stage or a skill, or
  says what to build or change ("I want the agent to handle X", "add a step",
  a conversation link, "promote this"): the stage skill owns those directly.
---

# Route, then step aside

Pick the stage, load that skill with the Skill tool, and let it run. Do not
restate its steps here.

## 1. Find the stage

| The request is about | Load |
| --- | --- |
| Setting up a new agent, or how far its setup has got | `onboard-agent` |
| Connecting or debugging a handoff platform (Zendesk, Salesforce, Gladly, email): chats not reaching agents, wrong queue, missing transcript | `configure-handoff` |
| An Ada platform or account question with no conversation behind it (swap an email address, SSO, roles, API keys, a sync) | `troubleshoot` |
| A new use case the agent can't do yet | `design-conversation` |
| An approved design board (DESIGN-APPROVED) | `author-playbook` |
| Changing or fixing an existing playbook | `revise-playbook` |
| Why one conversation went wrong: a link, a wrong answer, a loop, an odd handoff | `diagnose-conversation` |
| Failing tests, or a bad conversation to fix and retest until the use case passes | `test-and-fix` |
| What to improve across the whole agent: handoffs, containment, CSAT and custom metrics together | `improve-agent` |
| Why conversations hand off, counted by the recorded reason | `review-handoffs` |
| A tested changeset that should go live | `ada-promote-changeset` |
| Ramping a change on live traffic, or "should we revert" | `ada-rollout-changeset` |
| Watching a playbook after launch, alert noise, a control set | `ada-playbook-monitor-loop` |
| No custom metrics yet | `ada-custom-metrics-setup` |
| Reviewing the scorecard | `ada-custom-metrics-improve` |
| Looping on a failing metric | `ada-custom-metrics-loop` |
| "How do we prove this works", a new code tool, a metric claim | `create-verification-skill` |
| Not connected to Ada, or adacli missing | `setup-ada-mcp`, `setup-adacli` |

## 2. Rules for the pick

- Never start a fix request at an edit. A trace makes the playbook look
  guilty even when knowledge, coaching or a trigger owns the problem. A "why"
  question goes to `diagnose-conversation`. A request to fix and prove it goes
  to `test-and-fix`, which diagnoses each failure before changing anything.
- A question about the Ada platform itself goes to `troubleshoot`, not to a
  conversation skill. A handoff that never reaches the helpdesk is
  `configure-handoff`. A handoff the agent chose to make is `review-handoffs`
  or `diagnose-conversation`.
- When two stages fit, take the earlier one. "Make it live" with no passing
  tests starts at the test run, not at promote.
- For "where are we", read the agent's playbooks, changesets and test runs,
  then name the current stage and the next skill.
- When the stage is still unclear, ask one question and offer the two likeliest
  stages as options.

## 3. Say what you picked

Open with one line: the stage, the skill, and why. Then load the skill.
