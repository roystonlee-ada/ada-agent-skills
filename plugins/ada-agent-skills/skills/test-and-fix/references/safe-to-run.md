# What a test run can reach

Open this before the first run, and again when a case touches a tool or a
handoff you have not checked. Sources: the product docs (Simulations and Mock
API tools pages, checked 28/10/2026) and the api code that builds simulated
conversations. A fact marked ASSUMED is not settled in either.

## Contents

1. Handoffs in a saved test run
2. What a run does reach
3. Chats that are not test runs
4. Limits and quota
5. The rule

## 1. Handoffs in a saved test run

A saved test run is a simulated conversation. The api replaces each handoff
block with a simulated one when the conversation is simulated, so the handoff
shows in the transcript and the judge grades it, but nothing reaches a queue.

| Channel | What the handoff does in a run |
|---|---|
| Web Chat | Ends the simulation. Reaches no agent, creates no ticket. No webhook is sent and nothing is written to Zendesk Messaging |
| Email | The same as Web Chat |
| Voice | Ends the call. Reaches no agent and the fallback number is not dialled. Webhooks are sent as on a real call |

Not settled (ASSUMED): the api code has a simulated version for most handoff
block types, but two types (the Salesforce email block and the Zendesk live
chat block) show none in the code read, and the docs do not name them. The
tool listings show a handoff's name, description and active flag, not its
platform. Ask the person which platform each handoff sends to. If it is one of
those two, treat the case as unsafe until they confirm that the handoff is
test-safe.

## 2. What a run does reach

The simulation is not a sandbox for tools. These run for real:
- **API tools set to Live.** Live is the default. A live call that writes
  (refund, cancel, update, send) changes real data. A tool set to Mock is
  answered from the case's external systems text, and Ada's own utility tools
  (such as today's date) always run for real.
- **Code tools.** They run and their requests reach the customer's systems.
  Only "Block in simulations" stops one, and then the run fails at that call.
- **MCP tools.** They call the real server, except from a playbook step, where
  the step carries on as if the call worked. "Block in simulations" stops one.
- **Voice runs** place a real call and send HTTP Request blocks and webhooks.
  Web Chat and Email runs never send HTTP Request blocks or webhooks.

Each tool's setting shows in the tool listing as its simulation mode. A run on
a changeset uses the changeset's version of each tool, so a staged edit can
change the mode.

## 3. Chats that are not test runs

The test chat in the dashboard, `adacli` chat and any other live-chat session
are real conversations, not simulated ones. Whether their handoff reaches a
live queue is not stated in the docs (ASSUMED: it can). Never use them to
replay a case that ends in a handoff. The MCP single-turn simulation tool is
documented as leaving real conversations and analytics untouched, and it
carries no handoff, so it is safe for a first-turn check only.

## 4. Limits and quota

- Daily runs: 3,000 per instance in the docs (changelog 11/06/2026) and in a
  live read of the quota tool. One tool page still says 300. Read the live
  quota, not a page.
- Test cases: 1,000 per instance. Turns: 40 per run.
- A run can finish as `failed`, `timeout` or `cancelled`, or show "Run not
  graded" when a mocked tool call had no answer in the case text. None of
  those is a verdict on the agent. Fix the case text or the tool setting and
  rerun, and count the extra run against the quota.
- The judge is generative. The same configuration can flip a borderline
  verdict, so one run is not proof.

## 5. The rule

For each case, before it runs:

| Case | Run? |
|---|---|
| Ends in a handoff, Web Chat or Email, handoff platform confirmed not one of the two above | Yes |
| Ends in a handoff, platform unknown or one of the two above | No, until the person confirms the handoff is test-safe |
| Voice | Only after the person agrees to a real call and webhooks |
| Reaches a Live API tool that writes | No, until the tool is set to Mock and the case text describes its answer, or the person accepts the live call |
| Reaches a code or MCP tool | No, until it is blocked, or the person confirms the tool only reads |
| Needs a chat outside the test-run path | Not for a handoff case |

When you hold a case back, say which one, why, and what would release it.
