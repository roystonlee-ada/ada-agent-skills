# Embed script and allowed websites

Use when the chat widget does not load on a site, or the person wants to add
a website that may show it.

## Preconditions

- Owner or Admin role to edit approved domains.
- The exact site origin (scheme and host, no path).
- Whether the agent uses the Messaging channel or the older Chat channel.

## Steps

1. Record the current allowed websites list.
2. Messaging: open Config > Channels > Messaging > Launch. An empty allowed
   list lets any website show the standard widget. A custom app needs an
   approved HTTPS origin even when the list is empty.
3. Chat (older): open Config > CHANNELS > Chat > Launch > Allowed websites >
   Add domain. Use `https://www.yourdomain.com` or `https://*.yourdomain.com`.
   Top-level only, no paths. The list is capped at 8KB, and going over may
   stop the bubble loading, so use wildcards.
4. Copy the embed script from the Installation tab. Copy the handle and the
   cluster details with it.
5. If the widget still does not load, read the browser console. The error
   "violates the Content Security Policy directives" means the host page's
   policy must allow `https://static.ada.support`.
6. Do not replace an existing script tag only to change the channel name.
7. Launch controls split visitors into three groups. A test from the
   dashboard can bypass the rollout controls, so test on the live site too.
8. The `embed2` npm package needs its own package migration.

## Downtime risk

Removing a domain hides the widget on that site at once. Adding one has no
effect on others.

## How to verify

Load the page in a private window and confirm the widget opens and a message
sends.

## Rollback

Put the recorded list back.

## Source

- `product-docs/fern/versions/pages/docs/channels/messaging/messaging-configuration/launch-options.mdx`
  and `installation.mdx`
- `.../channels/chat/chat-configuration/launch-options.mdx`

## OPEN or ASSUMED

- ASSUMED: the person's agent uses Messaging unless they say Chat. Confirm
  first.
