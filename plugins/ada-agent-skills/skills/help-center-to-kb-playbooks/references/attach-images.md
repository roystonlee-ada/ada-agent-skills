# Attaching images to a playbook

Checked 28/10/2026. Update this file after the first real run.

## What a send step holds

```json
{
  "type": "send",
  "message": null,
  "instruction": "Tell the customer to open Settings. {{img:<attachment id>}}",
  "attachments": [{
    "id": "<attachment id>",
    "url": "https://<instance>.ada.support/playbook-images/<instance>/<playbook id>/<file>.png",
    "type": "image",
    "image_id": "<image id>",
    "alt_text": "The Settings icon, a grey gear at the top right"
  }]
}
```

The agent strips `{{img:<id>}}` before it sends text. The marker is an editor
placeholder that positions the image. The attachment `id` and `image_id` differ.

## How to attach

Use the dashboard playbook editor. adacli and the Ada MCP cannot upload or
attach an image, and a changeset rejects a send step that has `attachments`.

1. Open the playbook and the send step.
2. Add the image, paste the alt text, save.
3. Read the playbook back (`runtime-cli.md` or `runtime-mcp.md` says how) and
   check `attachments[]` and the `{{img:}}` reference are there.

If you have a browser tool, you can drive the editor with it. Otherwise give the
person the step list and the prepared image files, named
`<playbook>-step<N>.png`. Batch every image for one playbook into one visit.

## Prepare each image

- PNG or JPEG. At most 5 MB and 6000 x 6000 pixels.
- Crop to the part of the screen the customer needs. Aim near square, about
  560 px wide.
- Remove personal data: names, emails, order numbers.
- Add one red box or arrow if the target is small.

## After attaching

- Stop editing that playbook's sections through changesets. The platform
  rejects it. Any later text fix is a live dashboard edit, so say so each time.
- Run the saved cases again on the real chat channel.

## Images made per customer

An image generated per customer (a status card, a pass) is a different case. A
code tool draws a PNG and the send step takes its link from a variable. Use the
`ada-image-cards` skill. Help center screenshots do not fit it, because the
generated link expires.
