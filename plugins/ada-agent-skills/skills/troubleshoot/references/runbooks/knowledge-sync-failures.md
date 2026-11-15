# Knowledge source will not sync

Use when articles from a connected knowledge base or a website import are
missing, stale or stuck.

## Preconditions

- Edit access to knowledge.
- Know whether the source is an integration (Zendesk Guide, Salesforce
  Knowledge, Contentful and others) or a website import.

## Steps

1. Read the source's status and last sync time (`references/runtime-mcp.md`
   or `runtime-cli.md`). On the MCP, a non-null status means the source is
   being deleted or the deletion failed.
2. Integration source: the docs say it syncs every 15 minutes after the first
   sync. Check the knowledge base uses the default URL structure and that
   articles are at most 100KB. Contentful real-time sync uses a webhook URL
   that depends on the region.
   - Zendesk Guide with a 403 or access error: private articles need the
     subdomain authorized in Config > Apps > Zendesk, Include Private Articles
     on, and a Zendesk Login Email that can see them. A help center that
     limits access by IP address or network refuses Ada's sync. Ask Ada
     support for the addresses to allow.
   - Salesforce Knowledge stopped after an admin change: the sync uses the
     Client Credentials flow through an External Client App. Check its Run As
     user still exists and can see the articles, that Knowledge is still
     enabled in the org, and that the Knowledge version setting (Lightning or
     Classic) matches the org. A changed integration user is the first suspect.
3. Website import: sync runs Daily, Weekly (default) or Never. Use "Sync now"
   on the Sources tab for an on-demand run. A second run during an import is
   refused. The CLI sync command covers website imports only (adacli source
   and `--help`). For an integration source, use the dashboard Sources tab:
   Config > AI AGENT > Knowledge, Sources.
4. Check the website import limits: 100KB per article (truncated), five link
   levels, 1,000 articles per source, 50,000 per agent, URLs up to 1024
   characters, English only.
5. Allow the `AdaWebCrawler` user agent on the site. Crawler blockers,
   non-semantic HTML and complex redirects cause missing pages. A large import
   takes up to 24 hours and sends an email when done. Still syncing after 24
   hours with the limits met: raise it with Ada support.
6. Articles from a source are read-only in a changeset. Edit them at the
   source.
7. Availability rules apply only to pages imported after the rule is set.
   For a source where most articles are disabled, check the source's
   availability rules, then whether the pages came in before the rule was set.
   The rule does not reach them, so a changed rule needs a new import. Read the
   enabled and disabled counts per source (`references/runtime-cli.md`).
8. Migrating to a new Zendesk or Salesforce integration: connect the new
   source, wait for the sync, confirm, then disconnect the old one. Coaching
   and availability rules move for Zendesk but must be redone for
   Salesforce.

## Downtime risk

While a source fails or stays stuck, the agent answers from the last synced
articles, so customers can get stale answers. A re-sync adds no risk. Delete
Connection removes the source with its articles and tags at once. Never use it
as a retry.

## How to verify

Check the last sync time moved, and search for an article that was missing.

## Rollback

A re-sync has none to undo. After a delete, connect the source again and wait
for the first sync.

## Source

- `product-docs/fern/versions/pages/docs/knowledge/content-ingestion/` (all
  pages for integrations and web import)

## OPEN or ASSUMED

- OPEN: the docs have no troubleshooting page for a failed sync.
- ASSUMED: an IP or network limit on the help center causes a 403. The docs
  list no addresses for knowledge sync.
- ASSUMED: the legacy index status values (idle, ongoing, pending, fetch
  failed, upload failed, remove failed) are the ones the source status
  shows. Not confirmed on the live tools.

## Web import excludes page elements

If navigation, cookie banners, repeated footers or other page elements pollute
imported articles, use the website source's excluded CSS selectors in the
Knowledge Sources dashboard. Preview the selectors against representative
pages before saving. They remove matching elements, not whole source URLs.

There may be at most 20 selectors, each at most 75 characters. Supported
forms include tags, classes, IDs, attributes, descendant and child selectors,
the general sibling combinator, `:not()` with a simple selector, `:empty`,
`:link` and `:any-link`. Positional pseudo-classes, adjacent sibling `+`,
leading `*`, `!=`, pseudo-elements, comments and namespaces are unsupported.
Keep selectors narrow and confirm they retain the policy answer.

Changes apply at the next sync and cannot be saved during a running sync.
If the selectors remove all page content, Ada retains the last imported
version. An old article remaining visible is therefore not proof the new
exclusions worked. After sync, inspect the actual article text and the last
sync time. Roll back by restoring the recorded selector list and syncing
again. Runtime files give verified CLI flags and MCP discovery steps.

Source: https://docs.ada.cx/docs/knowledge/content-ingestion/web-import#exclude-page-elements

## SharePoint folder sources

Use the SharePoint connection to select a folder and include its subfolders.
Authorize read access for the selected site through Microsoft Entra, following
the SharePoint integration guide. Record the site and selected folder before
changing the connection. Do not request tenant-wide access for this setup.

The source syncs every 15 minutes. Select the option to import new articles
as inactive when a review is needed, then activate the intended articles
before expecting the agent to use them. Text is extracted, with no OCR for scanned images. Missing text in an
image-only file needs a text source, rather than another sync. SharePoint
columns can map to tags; choose them before connecting, because the selected
columns cannot change afterward. Check those mappings when tags are missing.

Verify an expected file from a subfolder, its readable article text, active
state and mapped tags after sync. Record the existing connection configuration before making a change. Column
mappings cannot be edited afterward, so replacing a connection needs a new
review and verification. Deleting a connection removes its
articles, so do not delete it as a retry. Use the dashboard for authorization,
folder selection and column mappings unless the current runtime schema
explicitly exposes them.

Source: https://docs.ada.cx/docs/knowledge/content-ingestion/knowledge-integration#import-articles-from-sharepoint
