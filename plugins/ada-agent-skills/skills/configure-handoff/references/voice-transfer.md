# Voice transfer

Docs: `channels/voice/voice-configuration/greetings-and-handoffs.mdx` and
`channels/voice/contact-center-integration.mdx` (one section per contact center,
plus `channels/voice/dialpad-voice.mdx`). Handoff block type: `voice_handoff`
(the Transfer Call block). On voice, each handoff has a Messaging tab and a
Voice tab. Fill the Voice tab, or the call has nothing to run.

## Setup summary

- The Transfer Call block moves the call outside Ada. Blocks below it do not
  run. Destinations: Phone number, SIP address, Amazon Connect (queue ID),
  Aircall (Number, Team, User, or None), Twilio (Ada drops off and your flow
  continues, with optional key-value data).
- SIP: Ada sends a SIP REFER. An optional User-to-User header carries key-value
  data, for example the caller's number.
- Amazon Connect: the caller reaches Ada through a contact flow and a Lambda
  that returns a `uuid` sent as DTMF. When Ada escalates or ends the call, it
  disconnects and the contact flow resumes. Set "Resume flow after disconnect"
  to Yes. Routing after that is the contact flow's job.
- Genesys Cloud: the SIP domain needs Secure Media enabled for the TLS and
  SRTP trunk.
- Aircall: the Ada Voice Smartflow widget must be enabled by Aircall and holds
  the Twilio Application ID and an application key from the Ada team.
- Zendesk Talk: a SIP-IN line that allows the Ada source addresses for the
  cluster. Create the ticket with an HTTP Request block, not Zendesk
  Ticketing, and pass its id as an X-header.
- Other documented sections: Cisco CUBE, Dixa, Five9, Gladly, NICE CXone.
- Location metavariables work only when the end user dials in. A Twilio
  outbound test call does not set them, so hardcode them in a Set Variable
  block when testing.

## Symptoms

The docs list symptoms for the Twilio transfer only. For the others, use the
chain checks.

| Symptom | Likely layer | Check | Fix |
|---|---|---|---|
| Call never reaches Ada (Twilio) | Trigger | Inbound number points at the right Studio flow or webhook, the TwiML endpoint returns valid TwiML, the Application SID is right | Fix the number, the TwiML or the SID |
| Call connects then drops (Twilio) | Connection | The TwiML endpoint is reachable over HTTPS, the dial element is well formed with a valid Application target, Twilio limits | Fix the endpoint or the TwiML |
| Escalation does not return to the Twilio flow | Return path | The dial element has an `action` URL that answers fast with valid TwiML, and the path reaches the Transfer Call block | Add or fix the action URL |
| Parameters from Ada missing (Twilio) | Payload | "Pass additional data to Twilio" is on with key-value rows, and the handler reads them before any redirect | Turn it on and read the request parameters |
| Transfer shows Busy, No answer or Failed | Routing | The destination in the conversation view: outcome and wait time | Fix the number, SIP address or queue. Failed also means a carrier error or unreachable destination |
| Blocks after Transfer Call never run | What the caller hears | A block was placed below the Transfer Call block | Move it above. Say what the caller needs to hear before the transfer |
| No outcome shown | Return path | Aircall and Twilio show no outcome by design. Ada drops off | None. Read the outcome in the contact center |
| Queue transfer wrong in Amazon Connect | Routing | The queue ID in the block, contact flow resume setting | Correct both |
| Out of hours | Hours | Ada schedule and timezone, then the contact center's own queue hours | Add a Scheduled branch with a voice message |

## Read and change

- Read: the handoff's Voice content through adacli. The MCP lists the handoff
  and channels. The conversation view shows the transfer outcome and the sent
  metadata.
- Change: the Voice tab content through adacli, or in the dashboard. Contact
  center flows are platform-side.
- The dashboard Test handoff button can place a real call. Treat it as
  ASSUMED unsafe against a live number.
