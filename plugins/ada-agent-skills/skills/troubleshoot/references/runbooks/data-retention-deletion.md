# Data retention and deleting end-user data

Use when the person asks how long Ada keeps data, or must erase an end
user's data on request.

## Preconditions

- An Ada API key from an Owner or Admin.
- The identifiers to erase: email, chatter id, external id, end user id or a
  variable match.
- An export of the data, if anyone may need it later.

## Steps

1. Retention: end-user data is deleted automatically after two years. Email
   attachments and stored images are deleted 7 days after upload. The full
   schedule is at the Ada Trust Center.
2. Redactions reduce the personal data stored in the first place.
3. To erase on request, use the Bulk End-User Deletion API. Send up to 1000
   identifiers per request. The body is at most 512KB, and each identifier
   matches at most 1000 end users.
4. The job is asynchronous (queued, in progress, completed, partial or
   failed) and can take up to 30 days to complete. Poll it.
5. Reuse the same `client_reference` within 24 hours to avoid a duplicate
   job. Do not resubmit an identifier within 7 days of its last submission.
   That fails the whole job.
6. Read each identifier's result: accepted, not found, invalid, exceeds limit
   or duplicate.
7. The Data Compliance API is deprecated. Use the Bulk End-User Deletion API.

## Downtime risk

None for the AI Agent. The deletion is permanent for the matched end users.

## How to verify

Poll the job until it reports completed, then check the per-identifier
results.

## Rollback

None. The docs describe no recovery after deletion. Export first through the
Data Export API when the data may be needed.

## Source

- `product-docs/fern/versions/pages/docs/other/data-retention/overview.mdx`
- `.../reference/bulk-end-user-deletion/overview.mdx`

## OPEN or ASSUMED

- OPEN: the retention schedule on the Trust Center was not read. Cite it, do
  not restate it beyond the two figures above.
