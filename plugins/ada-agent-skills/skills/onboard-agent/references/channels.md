# Channels: what each route can do

Contents: the route rules that hold for every channel, the table, then the
per-channel limits and launch checks. Open this file in stage 5 (channels),
once per channel the person wants.

Doc paths are pages on docs.ada.cx under `channels/`.

## Rules for every channel

- Content first. Docs say to put Knowledge, tools and playbooks in place
  before you turn a channel on. A live channel with thin content answers badly
  in public.
- Both routes can read a channel and test on it. Neither route can set up the
  channel itself: appearance, launch options, allowed websites, embed
  snippets, DNS, phone numbers and social connections are dashboard work.
- Enabling a channel is a live change with no changeset and no undo button
  besides disabling it again. Preview it, get approval, then do it.
- Test before launch: the dashboard Test AI Agent button (chat, and voice
  when a phone number is set), or a simulated conversation on the channel
  (chat, email and voice only).

## Table

| Channel | adacli can | The Ada MCP can | Dashboard step for the rest | Doc path |
|---|---|---|---|---|
| Messaging (web, iOS, Android, React Native) | list, get, enable, disable, configure (JSON) | list the channel, simulate a chat, count conversations by channel | Config > Channels > Messaging: Appearance, Launch, Data and privacy, then Installation (embed script or SDK, with a developer) | `messaging/messaging-onboarding` |
| Web chat (legacy Chat widget) | list, get, enable, disable, configure (JSON) | list the channel, simulate a chat, count conversations by channel | Channels > Chat > Launch: turn on Enable chat, copy the embed code, optional branding. Allowed websites list | `chat/chat-onboarding` |
| Email | list, get, enable, disable, configure (JSON) | list the channels, simulate an email, count conversations by channel | Config > CHANNELS > Email, Configuration tab, Activate Email. Then Bring Your Own Domain, launch controls, customization (sender name) | `email/email-onboarding` |
| Voice | the same channel commands. The `dialpad` group sets up a Dialpad connection | simulate a voice turn (text only, no audio), count conversations by channel | Config > CHANNELS > Voice: Configuration, Dialects, Language selection, Speaking voice tabs. Twilio or SIP setup with the Ada team | `voice/voice-onboarding` |
| Social: WhatsApp, Messenger, Twitter DM, Instagram Direct, Twilio SMS | enable and disable the Sunshine channel by name | count conversations by channel | Config > CHANNELS > Social, under Integrations beside Sunshine Conversations click Configure. Some handoff pairings go through your Customer Success Manager | `social/social-channel-onboarding`, `social/sunshine-conversations-setup`, `social/instagram-setup` |
| Third party: Zendesk SDK, Sunshine Web Messenger | the same channel commands | list only | Zendesk side deployment, then follow the guide | `third-party/overview` |
| SMS (agent sends texts during voice calls) | no command | no tool | Config > CHANNELS > Voice, Configuration tab, SMS settings. Consent rules apply | `voice/voice-configuration/sms-consent` |

Read the `channels configure` row with care. adacli sends the config as raw
JSON, and the docs do not name the keys or say whether it merges or
replaces. Run `channels get` first, copy the shape and change only the
fields the person asked for. Enable and disable resend the full config so
stored credentials stay.

The Ada MCP has no tool that enables, disables or configures a channel:
the `edit_agent_behavior` and `edit_agent_config` entity types do not include
one. Give the person the dashboard step.

Names the docs do not list as channels: X as its own channel, Apple Messages,
LINE. Say so, and send the person to their Ada team. Twitter DM and Twilio
SMS exist only as Social channels through Sunshine Conversations.

## Per channel: limits and launch checks

### Messaging and web chat

- Messaging replaces the legacy widget. If the agent uses Messaging, follow
  the Messaging page, not the web chat page. The docs ask you to confirm the
  agent's transition with the Ada team.
- Up to 3 images per message when image uploads are on. Redactions apply to
  the text read from images.
- Web chat: the allowed websites list holds at most 8KB. A content security
  policy that blocks the widget shows in the browser console.
- Installs that use the older embed package or a WebView policy need
  developer changes.
- Launch check: the widget loads on the real site or app, and one chat
  completes.

### Email

- One channel per address. Each channel has its own launch controls.
- Greetings do not play on email, and the List and Capture blocks are not
  supported. Email is not HIPAA eligible.
- Do not use an address that handoffs also send to, or the agent receives its
  own escalations.
- Forwarding or DNS (SPF and DKIM for your own domain) is the customer's
  work. Turn off forwarding before deleting a live address.
- Launch controls default to the agent answering 100% of mail. To soft-launch,
  lower the percentage and give a second address for the rest. That address
  must differ from the Ada-provisioned address and from every address on
  your own domain that is set up on the agent.
- Launch check: send a test mail to the Ada-provisioned address, and confirm
  the reply, the thread and the handoff path.

### Voice

- May not be in the subscription. Ask the Ada team before planning it.
- Ada provisions and manages Twilio for almost every deployment. A contact
  centre integrates by SIP (the Ada team needs the domain name and the IP
  addresses for the access list).
- Voice supports a subset of the 60 languages. Pick a speaking voice per
  enabled language.
- Flag brand and product terms for voice detection in the glossary.
- Launch check: a Test AI Agent call from the dashboard, then a call from a
  real phone.

### Social

- Needs Zendesk Suite or the Social add-on and a Sunshine Conversations
  licence for Zendesk Messaging handoffs.
- Zendesk Live Chat handoffs do not work on Social channels.
- Instagram needs a professional account (Business or Creator), and one
  account connects to one agent.
- Agent messages sent from Zendesk Agent Workspace do not appear in the
  Conversations view.
- Some blocks (greetings, surveys, option lists) degrade or are missing per
  channel. Check the feature compatibility table on the Social page.
- Launch check: a message from a real account on each channel.
