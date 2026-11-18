---
name: playbook-health
description: >
  Run a read-only health check of an Ada playbook against a particular customer
  intent. Detect hidden states and missing transitions across playbooks, guidance,
  knowledge and actions, check names, descriptions, general instructions and
  SEND/ASK/SET prompts, and recommend fixes and tests. Use for playbook health,
  state coverage or prompt hygiene reviews. For a population-ranked improvement
  backlog, use improve-agent.
---

# Check playbook health for one intent

## Pick the runtime

- With adacli, read `references/runtime-cli.md`.
- With Ada MCP tools, read `references/runtime-mcp.md` and check their live schemas.
- With supplied artifacts, proceed offline and state what is missing. When live
  retrieval is needed and neither route is available, use setup-adacli or
  setup-ada-mcp.

## Review coverage and prompt health

Read `../author-playbook/references/intent-state-health.md` and follow its full
review. Use `../author-playbook/references/playbook-graph.md` for graph evidence
and conversion. Start with one intent and its required outcome, then trace the
relevant entry points, parent/child returns and follow-ups across connected
surfaces. Keep the required states separate from the implemented states.

Include the shared review's prose and ASK lint checks and semantic SEND/ASK/SET
prompt review. Report execution status and manual checks explicitly. A passed
linter does not establish correct prompting or complete state coverage.

Return the coverage maps, evidence-labelled findings, lint and prompt findings,
recommended fixes with owners, and tests that would confirm each risk. Separate
configuration risks from reproduced behavior and population impact. Do not
stage, promote, run new conversations or execute actions during this check.
Existing authorized read-only traces may be inspected. Route approved follow-up
changes to revise-playbook, diagnose-conversation or test-and-fix as appropriate.
