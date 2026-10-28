# Find the instance and region

Use when the person is not sure which Ada instance or region they are on, or
a tool needs the right host.

## Preconditions

- Access to the dashboard login URL.

## Steps

1. Read the host of the dashboard URL. The host is the instance domain.
2. Map it to a region: `<handle>.ada.support` is the US region,
   `<handle>.eu.ada.support` is EU and `<handle>.maple.ada.support` is
   Canada.
3. The handle also shows at the upper left of the dashboard. Webhook events
   carry it in the `ai_agent_domain` field.
4. adacli takes a handle, a full domain or a URL. Outside the US region, pass
   the full domain, or the CLI looks in the wrong place.
5. API calls and the MCP URLs use the instance domain
   (`https://<instance-domain>/api/...`).
6. Webhook source IP allowlists differ by region. Use the list for the
   instance's region.

## Downtime risk

None. It is a read.

## How to verify

Call the instance status read from the runtime file and confirm it answers.

## Rollback

Not applicable.

## Source

- `product-docs/fern/versions/pages/docs/knowledge/content-ingestion/` (region
  specific Contentful webhook URLs for US, EU and CA)
- `.../reference/webhooks/overview.mdx` (region specific source IPs)
- `adacli/docs/guide.md` (handle, domain or URL)

## OPEN or ASSUMED

- OPEN: the docs do not say how to look up a tenant's region from a handle
  alone. Use the login URL.
- OPEN: the webhooks page shows EU as `*.ada-eu.support`. The knowledge pages
  show `eu.ada.support`. Trust the person's own login URL over either.
