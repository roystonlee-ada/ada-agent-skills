# Other resources, and which to trust

Live sources beat anything written down, this skill included. When they disagree with a reference file, follow the live
source and tell the skill's maintainer.

| Resource | Good for | Notes |
|---|---|---|
| **The live playbook schema** (the runtime file names the call) | Every step field, operators by variable type, nesting limits, deviation settings, the action-error rule | Most current. Read it before every build. |
| **The improvement guide** (once per session, over MCP) | Which entity to use, the changeset lifecycle, voice ask rules (capture modes, confirmation styles), "short send before a slow run" | Chat-first otherwise. |
| **The CLI's step schema command** | Field reference incl. the Send SMS `run` target and "handoff is terminal" | Its nesting limit (4) and re-ask default (4) differ from the MCP schema (10, 3). Trust the live schema. |
| **The CLI's deviations command** | Each ask's resolved deviation settings | Shows what the flow will actually do. |
| **The CLI's built-in docs for Claude Code** | General V2 rules: says `NONE` clears (on the bots checked, an exact SET of `NONE` stores the string `NONE`, which is what the patterns' `is "NONE"` checks rely on), clear before a backward `go_to`, uppercase operators, rules DSL takes variable ids | Nothing on voice. |
| **The adacli skills** (test agent, optimize, insights, config snapshot) | Test cases from failing conversations, comparing two test runs, config export | None authors playbooks or covers voice. |
| **`author-playbook`** (this plugin) | Chat V2 mechanics and the build method | Chat only; for voice, this skill wins. |
| **`diagnose-conversation`, `revise-playbook`** (this plugin) | Finding why a call went wrong, then changing the playbook | Hand the call to them once a live voice call fails. |
| **docs.ada.cx**: [Playbook best practices](https://docs.ada.cx/docs/automation/playbooks/best-practices), [Step reference](https://docs.ada.cx/docs/automation/playbooks/step-reference), [Voice call capture options](https://docs.ada.cx/docs/channels/voice/voice-configuration/voice-call-capture-options) | Voice basics: no duplicate acknowledgments, prose not lists, say how to read dates and emails, end on a clear question; capture modes | Short. Nothing on loops, corrections, failures or testing. |
| **EvalJS docs** | Writing and testing EvalJS expressions | For the logic module. |
| **This skill's `examples/`** | Shipped voice builds: texts, logic, fixtures, sims, live findings | Add yours when it ships. |
