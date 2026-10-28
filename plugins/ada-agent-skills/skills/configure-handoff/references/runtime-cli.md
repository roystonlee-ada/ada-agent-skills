# configure-handoff over adacli

For anyone with `adacli` on the path. Checked against `adacli --help` on
version 0.13.0, the adacli guide, the adacli source and read-only runs on four
real instances on 28/10/2026. Replace
`<instance>` with the agent's handle. If a command below is missing from
`--help`, run `adacli upgrade` and retry.

Contents: command table, what this route cannot do, reading a handoff,
reading a schedule, return path proof, testing.

Log in first with `adacli <instance> login`, then confirm with
`adacli <instance> status`. A login error with exit code 3 means log in again.

| Step | Command |
|---|---|
| List handoffs | `adacli <instance> handoffs list --json` |
| Read one handoff, block tree included | `adacli <instance> handoffs get <id> --json` |
| Back up before a write | `adacli <instance> handoffs get <id> --json > backup.json` |
| Back up the whole config | `adacli <instance> snapshot export --include handoffs -o backup.json` |
| Diff a backup against live | `adacli <instance> snapshot diff backup.json` |
| List integrations and state | `adacli <instance> handoffs integrations list --json` |
| Read one integration | `adacli <instance> handoffs integrations get <integration> --json` |
| List helpdesk groups | `adacli <instance> handoffs integrations groups <integration>` |
| Find variable ids for a rule | `adacli <instance> variables list --json` |
| List channels | `adacli <instance> channels list --json` |
| One conversation's handoff attempts | `adacli <instance> conversations handoffs <conversation-id> --json` (can be refused on some accounts: see "Return path proof") |
| Find conversations that escalated | `adacli <instance> conversations search --handoff --since 7d --json` |
| Instance schedules (Scheduled block hours) | `adacli <instance> client show --json`, then select the key `scheduled_block_schedules`. The output also holds a token field: never print or save the whole output |
| Read the reasoning around a handoff | `adacli <instance> conversations log <conversation-id>` |
| Edit description, tags or rules | `adacli <instance> handoffs update <id> --description <text>`, `--tags <csv>`, `--rules <dsl>`, `--clear-rules` |
| Edit the message tree | `adacli <instance> handoffs update <id> --file <path>` with a JSON subset. Validated before any write |
| Create a handoff, disabled | `adacli <instance> handoffs create --name <name> --file <path>` |
| Enable at create | add `--live`. Counts against the active cap |
| Zendesk Messaging block | `adacli <instance> handoffs set-zendesk-messaging <name-or-id> --department-id <id> --standby-message <text> --tags <csv>` |
| Zendesk integration credentials | `adacli <instance> handoffs integrations configure zendesk-messaging` with `--subdomain`, `--email`, `--api-token` |
| Toggle an integration | `adacli <instance> handoffs integrations enable <integration>`, or `disable` |
| Channel settings | `adacli <instance> channels get <id-or-name>`, and `channels configure <id> --config <json>` |

Integration names that adacli maps: `zendesk-chat`, `zendesk-messaging`,
`zendesk-support`, `salesforce-chat`. Verified against `--help` on 0.13.0:
`handoffs set-zendesk-support`, `integrations connect` and `integrations
download-app` are not there, and `integrations configure` takes
`zendesk-messaging` only. The adacli source on main has them, so they may
ship in a newer build. Run `adacli upgrade` and check `--help` before use.

## What this route cannot do

- It cannot read or change the integration of any other platform. The
  integration map holds only the four names above, and `integrations
  configure` accepts `zendesk-messaging` only. Use the dashboard at Config > AI
  AGENT > Handoffs > Integrations.
- It cannot edit Ada schedules or the Off hours tab. It can read them: see
  "Reading a schedule". Edit schedules in the dashboard at Config > AI AGENT >
  Handoffs > Off hours > Schedules.
- It cannot stage a handoff on a changeset. `handoffs create`, `update` and
  the `set-` helpers write live. The changeset entity types cover knowledge,
  custom instructions, coaching, playbooks and tools. Back up first.
- `handoffs delete` refuses a reserved handoff. Do not delete a handoff
  without the person's explicit approval.

## Reading a handoff

`handoffs get` returns the block tree as JSON. These block type names, seen in
live handoffs, tell you the platform:
- `zendesk_agent_workspace_handoff`: Zendesk Messaging.
- `zendesk_live_agent`: Zendesk Chat.
- `voice_handoff`: the Transfer Call block. The number field is `phone_num`.
  Flag a placeholder such as a 555 number.
- `scheduled_block`: an Ada schedule branch. Its affirmative branch is in
  hours and its negative branch is off hours. Its schedule id matches the
  `schedule_id` in `client show --json` key `scheduled_block_schedules`.
- `csat_survey`: a survey step, not a handoff target.
- Action blocks carry an `action_integration` id (observed):
  - Salesforce Messaging: an `action_integration` block with
    `action_integration_id` `app_salesforce_messaging_utils`, `action_id`
    `handoff`, `is_handoff` true and `should_pause` true.
  - Salesforce case: `salesforce2`, create-case action.
  - Gorgias live chat: the Gorgias utilities handoff action. A Gorgias ticket:
    its create-ticket action.
  - Others: `zendesk_ticketing_2`, `email`.

Fields that change what a customer meets:
- `reachable_when` lists the channels where a block is skipped. Observed on
  chat-only agents whose chats still ran blocks that list voice and email.
  ASSUMED as the general rule: confirm with one real chat before you call a
  block unreachable.
- A block can hold `messages` and `messages_voice`. Read the one for the
  channel in question.
- `is_handoff` false on a handoff action block means the handoff never counts
  in handoff metrics. Email handoffs have run this way.

## Reading a schedule

`scheduled_block_schedules` gives each schedule's name, timezone, weekly hours
and special days (observed). Run two checks:
- Special days all in the past: holidays are not covered. Report it.
- Compare the hours named in the off-hours text with the schedule's hours. A
  text that says 9 to 5 on a 9 to 6 schedule sends customers away early.

## Return path proof

When `conversations handoffs <id>` is not allowed, read the same proof from
two other commands:
- `adacli <instance> conversations details <id> --json`: the `handoffs` array
  has the target, status and reason code of each attempt.
- `adacli <instance> conversations transcript <id> --json`: presence events
  (`agent_arrival`, `agent_depart`, `live_chat_end`) and agent messages, which
  have a `source` of agent and an `agent_info` block.

Presence events alone are not a human reply. Look for an agent message. Ticket,
case and email handoffs return nothing to Ada by design (observed on Zendesk
Ticketing, a Salesforce case, a Gorgias ticket and email), so a missing reply
there is not a broken link.

## Testing

- `adacli <instance> chat` runs as a real chatter. ASSUMED unsafe for a
  handoff: it may reach the live helpdesk. Do not use it to test a handoff to
  a live queue.
- `adacli <instance> testing` runs saved cases. ASSUMED to mock handoffs the
  same way simulations do. Confirm on the first run that the result shows a
  simulated handoff, not a platform ticket.
- `adacli <instance> conversations handoffs <conversation-id>` after a real,
  approved test shows target, outcome and reason code.
