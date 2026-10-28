# onboard-agent over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Checked against the
live tool schemas and read calls on a sandbox agent on 28/10/2026. Your host
may prefix the tool names.

Contents: the inventory reads (step 1), what this route cannot read, the
write routes, and traps.

## Inventory reads (step 1)

Make every call read-only. Use a window of the last 30 days wherever a tool
needs dates.

| Evidence | Tool call | What to read |
|---|---|---|
| Connection works | `get_ada_configuration` | Any reply. An authentication error means `setup-ada-mcp` |
| Company description | `get_ada_configuration` | The item with `entity_type: company_description`. Page through `next_cursor`, and join items that carry `chunk` and `chunk_count` in order |
| Glossary | `list_glossary_terms` | `returned_count`, page with `next_cursor`. Each term has `user_terms`, `ai_agent_terms` and `translation_mode` |
| Knowledge sources | `list_entities` with `entity_type: knowledge_sources` | Each source's `name`, `last_sync` and `status`. A non-null `status` means a deletion is running or failed. The source named "Created in Ada" holds articles written in Ada |
| Knowledge coverage | `search_knowledge` with a short keyword per top question | A title match per question. It matches titles only, returns at most 25, and skips disabled articles unless you pass `enabled_only: false`. Say "at least N articles", never a total |
| Handoffs | `list_entities` with `entity_type: handoffs`, `detail: full` | `name`, `description`, `is_active` for each |
| Handoffs working | `get_conversations` with `detail_level: IDS_ONLY`, a `HANDOFF IS true` filter and an `ISTESTUSER IS true` filter in a second call | Whether any conversation, real or test, escalated |
| Tools | `list_entities` with `entity_type: tools` | `type` (`api`, `code`, `mcp`), `enabled`, `direct_use`, inputs and outputs. Treat a name or description that says placeholder, stub or template as not real |
| MCP server connections | `list_entities` with `entity_type: mcp_server_connections` | `status`: `connected` and `auth_expired` offer tools, `pending` and `error` do not. Also `enabled` and `tool_count` |
| Tool health | `get_ada_metric` with `metric_type: api_tool_performance` | `error_rate` and calls per tool |
| Playbooks | `get_ada_configuration` (playbook items), or `list_entities` with `entity_type: playbooks` | Name, description, `enabled` |
| Channels | `list_entities` with `entity_type: channels` | Name, `type` (native or custom), `modality`. There is no enabled flag |
| Channel traffic | `get_ada_metric` with `metric_type: conversation_volume_opened` and a `CHANNEL IS <value>` filter | Real conversations on that channel. Values come from `get_available_filters` (for example chat, email, voice, sms, whatsapp). Test chats are excluded by default |
| Languages seen | `get_ada_metric` with `conversation_volume_opened` and a `LANGUAGE IS <code>` filter | Traffic per language. It shows use, not what is enabled |
| Custom metrics | `list_entities` with `entity_type: custom_metrics`, `detail: full`, then `scorecards` | `total_count`, and each metric's state if the record carries one |
| Metric results | `get_ada_metric` with `metric_type: custom_metric_pass_rate` | A pass rate means the metric graded chats |
| Test cases | `get_test_cases` with `group_by_last_run: true` | `total_count`, `last_run_at` per case. Page with `next_cursor` before you quote a total |
| Test results | `get_test_runs` (latest per case by default), with `status_filter` if needed | Status and pass or fail for each case's latest run |
| Test quota | `get_test_run_quota` | `runs_remaining` today |
| Changesets | `list_agent_changesets`, once with `status: testing` and once with `status: promoted` | Names, dates, summaries of what waits and what shipped |
| Live volume | `get_ada_metric` with `conversation_volume_opened` | Non-test conversations in the window |

## What this route cannot read

Mark these rows Unknown and give the person the dashboard page. Each is a
missing tool or field I saw, not a guess.

- Persona (agent name, company name, tone, emoji, message length): not in
  `get_ada_configuration`. Dashboard: Config > AI AGENT > Settings,
  Preferences tab.
- Enabled languages: no tool returns them. Dashboard: Config > AI AGENT >
  Settings, Languages tab.
- Redactions, built-in or custom: no tool returns them. Dashboard: Config >
  AI AGENT > Settings, Preferences tab, Redactions.
- Whether a channel is enabled: `list_entities` for channels has no such
  field. Use traffic as the evidence, or Config > CHANNELS.
- A handoff's destination platform, its integration state and which handoff is
  the fallback: Config > AI AGENT > Handoffs, Integrations.
- A total article count: use `search_knowledge` for a floor, or Config > AI
  AGENT > Knowledge.

If the person also has `adacli`, read `references/runtime-cli.md` for these
rows. It reads all of them.

## Writes

The skill makes no write on its own. Writes in a stage go through that
stage's skill. Foundation is the one exception, and only after the person
approves a preview.

| Foundation item | Route |
|---|---|
| Glossary term | `edit_agent_config` with `entity_type: glossary_term`, `operation: create`. Call it with no `fields` first to read the schema. Call it with `fields` to get the preview, show the preview, and call again with `confirmed: true` only after the person says yes |
| Company description | No tool. The `edit_agent_behavior` and `edit_agent_config` entity types do not include it. Give the person the exact text and the page: Config > AI AGENT > Settings, Preferences tab, Company description |
| Persona, languages, redactions | No tool, same reason. Give the exact values and the dashboard page from the section above |

Say before the glossary write that `edit_agent_config` edits go live at once,
with no changeset. The same holds on the CLI route. Read the term list first
so you do not create a duplicate, and keep the "before" state in your
preview.

## Traps

- `list_entities` rejects `limit` for every entity type except `variables`,
  even though the schema lists it. Page with `next_cursor` instead.
- `get_ada_configuration` pages by size and holds the playbooks, tools and
  custom instructions as well. Follow `next_cursor` to the end before you say
  something is absent.
- A default agent already has a native Chat and Email channel and a default
  handoff. Their presence is not progress: grade from active state, traffic and
  tests.
- `get_conversations` and `get_ada_metric` exclude test conversations by
  default. Add `ISTESTUSER IS true` when the question is "did a test escalate".
