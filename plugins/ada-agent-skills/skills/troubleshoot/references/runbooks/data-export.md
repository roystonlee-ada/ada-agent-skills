# Export conversations and messages

Use when the person wants conversation data in their own system or a file.

## Preconditions

- An Ada API key. The Data Export API may not be in every plan.
- The date window. History covers the past 12 months.

## Steps

1. Pick the endpoint: conversations or messages, both under the v2 export
   API, with the API key as a Bearer token.
2. A query window ends at most 60 days after it starts. Split a longer
   period into windows.
3. A page holds at most 10,000 records. Set the window with `created_since`
   and `created_to`, and the page with `page_size`. Follow `meta.next_page_uri`
   until it is empty.
4. The rate limit is 10 requests per second per endpoint. A 429 means slow
   down.
5. For a quick file from the terminal, adacli can export conversations, with
   weaker completeness (`references/runtime-cli.md`).
6. Export before any bulk deletion. See `data-retention-deletion.md`.

## Downtime risk

None. It is a read.

## How to verify

Compare the exported count to the conversation count for the same window in
the dashboard.

## Rollback

Not applicable, nothing changes.

## Source

- `product-docs/fern/versions/pages/reference/data-export/v2/overview.mdx`
- `.../docs/optimization/conversations/data-export.mdx`
- `.../reference/data-export/v2/conversations.mdx` and `getting-started.mdx`
  (parameters, `next_page_uri`)
- `adacli/docs/guide.md` (`conversations export`)

## OPEN or ASSUMED

- OPEN: freshness. The v2 page says near real time and the dashboard page
  says at least 2 hours of ingestion. Tell the person to allow 2 hours.
