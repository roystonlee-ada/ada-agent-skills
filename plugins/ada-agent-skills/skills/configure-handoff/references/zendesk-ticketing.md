# Zendesk Ticketing

Docs: `handoffs/zendesk/zendesk-ticketing.mdx`. Action integration id seen in
live handoffs: `zendesk_ticketing_2`. A passive "Create Ticket" action: it
creates a standard ticket and the agent replies by email. There is no live
return.

## Setup summary

- Connect at Config > AI AGENT > Handoffs > Integrations > Zendesk Ticketing >
  Connect, then Finish.
- The block captures nothing itself. Build the handoff in this order:
  1. Capture blocks for `name`, `email` (Email validation) and the issue.
  2. A Fetch Chat Metadata block. Input `chatter_token`. Save
     `chat_transcript` and `chatter_info`. Select both optional variables or
     the transcript and info are not passed.
  3. The Create Ticket action.
- Mandatory inputs: Comment, Chatter's Name, Chatter's Email.
- Optional inputs: Attach Comment To (internal note by default, or public
  reply), file data or `chat_attachments`, Tags (underscores, no special
  characters), Email CCs, custom fields by tag, and a "Count as Handoff"
  toggle.
- Replies come by email. Without the SMTP Connector they arrive from a
  different address in a new thread (see `zendesk-smtp-connector.md`).

## Email webform pattern (observed on a real instance)

An email webform can update a ticket that already exists, not only create one.
- An HTTP Request block updates the existing ticket by id (PUT to the Zendesk
  REST API). A Create Ticket action is the fallback when no ticket id is
  known.
- Every block in the pattern needs Count as Handoff on, or email handoffs never
  count in handoff metrics.
- Check the fallback branch fills the subject and the customer name. A branch
  that skips them creates tickets with a blank subject or no requester name.

## Symptoms

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Save button stays grey | Payload | Name and Email variables exist | Create the variables, then pick them |
| Handoff fails on a conditional or required Zendesk field | Field mapping | Every conditional and required Zendesk field has a tag mapped | Map a tag to each. A field without one breaks the handoff |
| Tag missing on the ticket | Field mapping | The tag entered is the display label | Enter the tag value |
| Ticket has no transcript | Payload | Fetch Chat Metadata ran before the action, and both optional variables were chosen | Add the block, select the variables, pass them in Comment |
| Email Validation lost, wrong email | Field mapping | The `email` variable type | Keep Email validation |
| No ticket at all | Connection | Integration connected and enabled | Reconnect |
| Tile shows not connected | Connection | Config > Apps > Zendesk for the subdomain, then the Zendesk Ticketing tile. A multi-brand account connects through the primary account subdomain | Reconnect with a current Zendesk admin. Access can be revoked from Zendesk admin settings, so ask what changed there |
| 401 on ticket creation | Connection | Whether the Zendesk admin who approved the OAuth connection is deactivated or removed access, or the handoff is still on the old token method. ASSUMED: a deactivated approver breaks the connection, the docs only say access can be revoked | Reconnect with a current Zendesk admin. For the token method, see troubleshoot's `references/runbooks/zendesk-token-to-oauth.md` |
| A message is missing from the transcript | Payload | Where the Fetch Chat Metadata block sits relative to later messages. ASSUMED: it saves what the conversation holds when it runs | Put the block last, right before the Create Ticket action, and pass the variable in Comment |
| CSAT not updating on the ticket after a new handoff | Return path | The handoff counts as a handoff ("Count as Handoff") and the CSAT path matches the new handoff | Turn on the toggle. Check the CSAT step follows the new block. Raise it with the Ada team if it persists |
| Reply arrives from a new address or thread | Return path | SMTP Connector | See `zendesk-smtp-connector.md` |
| Duplicate tickets with Zendesk Messaging | Trigger | Both blocks ran for one conversation | Gate each block by channel or variable |
| Closed-hours handling | Hours | Ada schedule and timezone, Zendesk business hours | Add a Scheduled branch. The ticket still queues, so say when to expect a reply |

## Read and change

- Read: the handoff action block and its inputs through adacli. The MCP lists
  the handoff only.
- Change: the handoff through adacli. Integration connection is the
  dashboard. Ticket fields, triggers and views are Zendesk-side.
