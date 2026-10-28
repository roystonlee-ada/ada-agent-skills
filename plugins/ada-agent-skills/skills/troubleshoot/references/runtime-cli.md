# troubleshoot over adacli

For anyone with adacli installed. Checked against `--help` of adacli 0.13.0
on 28/10/2026. Put the instance first: `adacli <handle> <group> ...`. Outside
the default US region, pass the full domain (for example
`<handle>.eu.ada.support`) instead of the bare handle.

## Log in and check the session

| Need | Command |
|---|---|
| Log in (device code, works for SSO and MFA accounts) | `adacli <handle> login` |
| Session health and connectivity | `adacli <handle> status --json` |
| Instance details | `adacli <handle> client show --json` |
| Bundled guide | `adacli docs guide` |

Exit code 3 means log in again. A session lasts as long as the instance's
inactivity timeout.

## Reads

| Need | Command |
|---|---|
| Channels and their state | `adacli <handle> channels list --json`, then `channels get <id-or-name> --json` |
| API keys (names and ids, never values) | `adacli <handle> api-keys list --json` |
| Team members and roles | `adacli <handle> team list --json`, `team get <id> --json` |
| Knowledge sources, status and last sync | `adacli <handle> knowledge sources list --json` |
| Changesets | `adacli <handle> changesets list --status testing --json`, then `changesets get <id> --diff` |
| Diff a saved snapshot against live | `adacli <handle> snapshot diff <file>` |
| Export conversations to a file | `adacli <handle> conversations export --since 30d -o <file>` |

`conversations export` pages best-effort. A page can repeat or skip rows while
new conversations arrive, and a file export stops at 50,000 rows unless
`--limit` raises it (100,000 at most). Use the Data Export API when the
person needs a complete, dated pull (`references/runbooks/data-export.md`).

When `knowledge sources list` is refused or returns nothing, estimate source
health from the articles:
1. Page `adacli <handle> knowledge list --limit 200 --page <n> --json` (200 is
   the API maximum). Quote `meta.total_items` and stop when the pages run out.
2. Group the articles by `source`. Count `enabled` true and false per source.
3. Take the newest `updated_in_ada` per source. It is the last time Ada wrote
   an article from that source, by a sync or an edit.

Article dates approximate the last change. They cannot prove a failed sync: a
source with no new or changed pages leaves old dates and still syncs fine.

`channels get` shows id, name, enabled, type, modality, app id, whether a
webhook is configured and the Zendesk subdomain. It does not show an email
inbox's sender address or forwarding. Read those in the dashboard.

## Writes

Preview each one for the person and wait for a yes. Record the old value
first.

| Need | Command |
|---|---|
| Create an API key | `adacli <handle> api-keys create --name <name>` |
| Revoke an API key | `adacli <handle> api-keys revoke <id>` |
| Add a team member | `adacli <handle> team add --email <email> --role <role> --name <name>` |
| Change a role | `adacli <handle> team update-role <id> --role <role>` |
| Remove a team member | `adacli <handle> team remove <id>` |
| Re-crawl a website import | `adacli <handle> knowledge sources sync <id>` |
| Change a website import's schedule | `adacli <handle> knowledge sources update <id> --sync daily` (daily, weekly or never) |
| Enable or disable a channel | `adacli <handle> channels enable <name>` or `channels disable <name>` |
| Build a revert of a promoted changeset | `adacli <handle> changesets revert <id> --name <name>` |

Role names: the CLI accepts `admin`, `manager` and `agent`. The docs list
Owner, Admin, Agent and Read Only. OPEN: how the two sets map. Check the
result of `team get` after any role change, and use the dashboard for Owner
and Read Only.

`api-keys create` accepts `--expiry`. The docs say API keys do not expire.
OPEN: whether the flag has any effect. Treat a key as non-expiring and
rotate on your own schedule.

`knowledge sources sync` re-crawls a website import only. The API returns 429
while an import is already running. An App connection syncs on its own
schedule.

## Snapshot as a backup

`adacli <handle> snapshot export -o <file>` writes the content configuration.
`--include` and `--exclude` narrow the resource types. The output shape
depends on the adacli version (a JSON file in 0.13.0, an archive on newer
builds), so ASSUMED: check `snapshot export --help` on the installed version.

A snapshot does not hold email inboxes and settings, blocked and trusted
senders, API keys, webhooks, team, roles, SSO, session limits, MCP server
setup, conversations, the audit log, change sets, or the agent's name and
handle. Import replaces the sections it carries and deletes items the archive
lacks, and Ada has no undo for it. Do not suggest `snapshot import` as a
rollback for a platform setting.

## What the CLI does not reach

These have no adacli command. Give the dashboard path from the runbook.

- Email sender address, inbox, forwarding and BYO domain setup.
- SSO, session limits and approved domains.
- Webhooks and the audit log.
- Data retention and bulk end-user deletion. Both are API calls with an API
  key, and `conversations export` above is not the Data Export API.
- Region and instance lookup.

## Inside Ada Architect

Skip this section outside Ada Architect. Architect sessions run on a
gateway that holds the promote token. A promote still goes through
`ada-promote-changeset`, and this skill never runs one.
