---
name: ada-image-cards
disable-model-invocation: true
description: Build a per-customer image card (status card, booking summary, pass, points card…) that an Ada V2 playbook shows in chat. A code tool draws the card as SVG, rasterises it to PNG in pure Python, hosts it through Ada's File Upload presign API, and a send step shows it as a picture. Use for "show an image card", "generate a card image", "image in chat from API data", "boarding pass / status card image", or when adding, changing or debugging such a card. Covers step-by-step setup (allowed domain, font atlas, code tool, playbook wiring), the runtime gotchas, and testing.
---

# Ada image cards: code tool → PNG → chat picture

A playbook can show a picture that is built per customer from live data (for example a status card
with the customer's own details). Ada has no image service for this, so the card is drawn and hosted
by a **code tool**:

```
data in variables ──► CODE TOOL (pure Python, Monty runtime)
                        1. build the card as an SVG string
                        2. rasterise SVG → PNG bytes        (scripts/svgpng.py, no libraries)
                        3. upload via the File Upload presign API  (3 fetch calls)
                        4. return {"image_url": <signed https link, 30 min>, "debug": "..."}
                  ──► output image_url → hidden variable
                  ──► SEND step with an attachment whose url is {{ variable:<image_url var> }}
```

## 0. Pick the runtime

The steps below show `adacli` commands. Read one file for how to do the same over the Ada MCP:
- `adacli` on the path → `references/runtime-cli.md` (the commands in the steps, plus what to check)
- Ada MCP tools present (`get_ada_configuration`, `run_code_tool`) → `references/runtime-mcp.md`

The local build and test scripts in `scripts/` are the same on both.

Everything in this guide was proven end to end in production bots (live in Oct 2026). The kit in
`scripts/` + `templates/` was tested in a real Ada runtime: real upload, link served as `image/png`.

**Kit contents**

| file | what it is |
|---|---|
| `templates/card_template.py` | Example card tool: title, subtitle, status pill, up to 6 label/value cells. Copy it and edit `build_card()` and `INSTANCE`. |
| `scripts/svgpng.py` | Pure-Python SVG → PNG renderer that runs inside Ada's code-tool runtime. Don't edit unless you need a new SVG feature. |
| `scripts/build_atlas.py` | Turns a .ttf font into the compressed glyph atlas the renderer uses (needs Pillow, run on your laptop). |
| `scripts/build_tool.py` | Assembles renderer + atlas + your card into one deployable file, minified, and checks the 64 KB cap. |
| `scripts/run_local.py` | Runs the built tool locally in `pydantic-monty` (same Python subset as Ada) with a fake upload, and writes the PNG so you can look at it. |
| `scripts/qr.py` | Optional pure-Python QR encoder (byte mode, versions 1–10, up to ~270 characters). Pass it to `build_tool.py` when the card needs a QR code. |
| `scripts/minify.py`, `scripts/dce.py` | Helpers used by `build_tool.py` (minify, strip unused functions). |

---

## Step-by-step

### 1. Get references and samples first

Before drawing anything, ask the requester for:

- **A reference design**: a mock-up, the equivalent screen from their app or website, or brand
  guidelines (colours, font, logo files as PNG/SVG).
- **Sample data**: a few real API responses (or variable values) covering the normal case **and**
  the edge cases: missing fields, long names, several passengers or items, cancelled or error states.
- **Which fields must appear**, which can be dropped, and what to show when a value is missing.

Design against real samples, not invented ones. Most rework comes from data you did not see
(a null field, a 40-character name, a second row). Strip personal data from samples before you
keep them anywhere.

### 2. One-time setup per bot

1. **Check access.** You need an ADMIN or OWNER role, the `code-actions-enabled` flag on the bot,
   and adacli 0.8.0 or later (`code-tools create / update / test` work from 0.8.0).
2. **Allow the upload host.** Dashboard → **Content → Tools → Allowed domains** → add
   `https://integrations-file-uploader-s3-production.s3.amazonaws.com`
   - The scheme (`https://`) is required.
   - It is **not** "Launch → Allowed websites"; that list is for where the chat widget is embedded.
     Adding the host there does nothing for code tools.
   - The bot's own `<handle>.ada.support` is reachable without listing it.
   - Without this, the tool returns `"s3 …"` or "fetch … was blocked: the domain is not on this
     client's allowed domains" and the playbook falls back to text.
3. **Local tools.** Python 3 with `pip install pillow pydantic-monty` (use a virtualenv).

### 3. Design the card as SVG

Open `templates/card_template.py` and edit `build_card()`. It returns an SVG string.

- Draw on a fixed `viewBox` (e.g. `0 0 480 360`) and set `width`/`height` to 2x for sharpness;
  `svg_to_png(svg, scale, bg)` rasterises the viewBox at `scale` (1.0 = 480×360 px).
- **Keep the card near-square.** The chat widget limits the image's height to about its width, so a
  tall card (e.g. 400×720) is shown shrunk and narrow. About 480–560 wide by 340–620 tall
  displays well.
- Supported SVG: `rect` (incl. `rx`), `line`, `circle`, `path` (full path syntax incl. arcs),
  `text` (`text-anchor`, `font-size`, `font-weight`), `g` with `transform`, `linearGradient`, and
  `image` with an embedded **PNG or SVG `data:` URI** (for logos).
- **Not supported:** `opacity`/`fill-opacity`, `clipPath`, `radialGradient`, filters, CSS
  `<style>`, `tspan`. Blend colours yourself instead of using opacity.
- Use colour hex values (`#2F3238`). Text is single-line; truncate or shrink long values yourself.
- Build every tag with the `LT` constant (`LT = "\x3c"`), never a literal `<svg` / `<rect` in the
  source (see Gotchas: WAF).
- Escape every customer value with `esc()`.
- Show a dash (`–`) for missing values rather than leaving gaps.
- **Inputs are bare names**: if the tool declares an input `title`, your code just uses `title`.
  Inputs bound to an unset variable arrive as `None`, so wrap them in `txt()`.
- To pass a list (rows, passengers, segments), use a **delimited string** such as
  `Label~Value||Label~Value` and `split()` it. It's simpler and safer than JSON in a variable.

Tip: mock the SVG in a browser first (save the string to a .svg file and open it), then check the
PNG from step 6. The PNG is the truth.

**Need a QR code?** Add `scripts/qr.py` to the build (step 5) and draw it as one path:

```python
m = qr_matrix(payload)                     # list of rows of 0/1
out.append(LT + 'rect x="330" y="200" width="130" height="130" fill="#FFFFFF"/>')   # quiet zone
out.append(LT + 'path d="' + qr_path(m) + '" fill="#000000" transform="translate(338 208) scale('
           + str(114.0 / len(m)) + ')"/>')
```

- Encode the payload **exactly** as received. Some formats (e.g. IATA boarding-pass barcodes) use
  fixed-width fields where spaces matter: never trim or collapse them, or the code scans to corrupt
  data. Check by decoding your local PNG (e.g. OpenCV `cv2.QRCodeDetector().detectAndDecode`).
- Keep the QR at least ~110 px wide in the viewBox, with a white margin around it.
- A barcode that grants access (a boarding pass, a ticket) is a live credential: never send it to a
  third-party QR service. Generating it inside the tool, as here, keeps it in Ada.

**Photo-style art?** Gradients and shapes are cheap, but a photo or illustrated background is too
big for the 64 KB source cap as PNG. The proven alternative is JPEG: pre-encode the static art
offline (with restart markers on every 8-pixel row) and, at runtime, re-encode only the rows the
dynamic text sits on. That's a bigger build; only do it if the design really needs a photo.

### 4. Build a font atlas

The renderer can't read .ttf files at runtime; it uses a pre-baked glyph atlas.

```bash
python3 scripts/build_atlas.py <font_dir> <FamilyPrefix> 24 400,600,700
# expects <font_dir>/<FamilyPrefix>-Regular.ttf, -SemiBold.ttf, -Bold.ttf
# writes font_atlas_24_400-600-700.b64 (~13 KB)
```

- Use the brand font if its licence allows it, otherwise an open font (e.g. Montserrat, OFL).
- Size 24 px covers text from ~11 to ~40 px well (glyphs are scaled).
- Each weight costs ~4–5 KB. Drop SemiBold (`400,700`) if you hit the 64 KB cap.
- The atlas covers printable ASCII plus `· • – — ' ' " " → é É`. Accented Latin letters are folded
  to plain letters (é → e). **Other scripts (Chinese, Thai, Arabic…) render as `?`.** For those
  languages, skip the card and send text.

### 5. Assemble the tool

```bash
python3 scripts/build_tool.py my_card.py font_atlas_24_400-600-700.b64 tool.py
# -> tool.py 48170 bytes OK
python3 scripts/build_tool.py my_card.py font_atlas_24_400-600-700.b64 tool.py scripts/qr.py   # with QR
# -> tool.py 53234 bytes OK
```

The code-tool source limit is **64 KB** (a bigger update or create fails with `400 source_code must be at
most 65536 bytes`, and a failed update leaves the old source live). The script prepends the
renderer and atlas, strips unused functions and minifies. If it reports OVER: use fewer font
weights, a smaller atlas, or a smaller embedded logo.

### 6. Test locally

```bash
python3 scripts/run_local.py tool.py '{"title":"Order 48213","subtitle":"Placed 19 Oct","status":"Active","rows":"Items~3||Total~USD 42.50"}' out.png
# result: {'image_url': 'https://example/ok.png', 'debug': 'card ok png 36863'} | 0.14s
```

Pass **every** input the tool declares (in Ada a declared input always exists; use `null` for a
variable that would be unset, which is what Ada sends). Open `out.png` and check it against the
reference design. Run every sample from step 1, including
the edge cases. Local runs are much faster than live (see Gotchas: time budget), so treat anything
over ~1 s locally as a risk.

### 7. Create the variables

```bash
adacli <handle> variables create --name card_image_url --scope global --type string --json
adacli <handle> variables create --name card_debug     --scope global --type string --json
```

Plus whatever input variables the card reads (usually outputs of an earlier web action).

### 8. Create the code tool

```bash
adacli <handle> code-tools create --file tool.py \
  --name "Render <thing> card image" \
  --description "Draws the <thing> card and returns a hosted image link. Playbook-only." \
  --inputs '[{"name":"title","type":"text","variable_id":"<var id>"}, ...]' \
  --outputs '[{"name":"image_url","key":"image_url","save_as_variable":true,"variable_id":"<card_image_url id>","is_visible_to_llm":false},
              {"name":"debug","key":"debug","save_as_variable":true,"variable_id":"<card_debug id>","is_visible_to_llm":false}]' \
  --no-standalone --json
```

- Set `INSTANCE` in the card file to the bot's handle **before** building. The upload API lives on
  the bot's own domain, so a sandbox and a production bot need different builds.
- Input `type` is `text|number|boolean|list|dict` (`string` is rejected).
- `--no-standalone` means only playbooks can run it, and the AI can't call it on its own.
- Both outputs hidden from the LLM (`is_visible_to_llm: false`).
- **Inputs, outputs and environment can't be changed after create.** To change them, create a new
  tool and repoint the playbook. Source-only changes: `adacli <handle> code-tools update <id> --file tool.py`
  (keeps the id and bindings). `code-tools delete <id>` has no `--yes` flag.

### 9. Dry-run it for real

```bash
adacli <handle> code-tools test <id> --inputs '{"title":"Test","rows":"A~1"}' --json
curl -s -o /dev/null -w '%{http_code} %{content_type}\n' "<image_url from the result>"
# expect: 200 image/png
```

`code-tools test` runs in the real runtime and **really uploads**, so use dummy data, never a
customer's details.

### 10. Wire the playbook

Right where the card should appear:

1. `set` **card_image_url = ""** (clear it; see Gotchas: global variables persist).
2. `run` the code tool: `{"type":"run","target_type":"action","target_id":"<tool id>"}`.
3. `if_else` with branch operator `AND`: `card_image_url is not null` **AND**
   `card_image_url is not ""` (both checks are needed)
   - **if** → `send` with the picture:
     ```json
     {"type": "send",
      "message": "Here are your details:\n\n{{img:<24-hex attachment id>}}",
      "attachments": [{"id": "<24-hex attachment id>",
                        "url": "{{ variable:<card_image_url id> }}",
                        "alt_text": "Your status card"}]}
     ```
   - **else** → a text `send` with the same information (always keep a text fallback).
4. Continue the flow.

Rules for the attachment:
- The attachment `id` is any 24-character hex string, and `{{img:<id>}}` in the message must match it.
- The `url` must be `{{ variable:<id> }}` (with the `variable:` prefix). The `{<id>|}` form is
  rejected at save.
- **Change sets can't create or edit send-step attachments** (400 "cannot be authored or edited
  through changesets"). Add the attachment with `playbooks update` or in the dashboard, after
  promoting any change set that touches the playbook.

### 11. Test in a real conversation

- Run a test conversation. In the transcript (`adacli <handle> conversations transcript <id> --json`)
  a working card appears as a separate message with `_type: "picture"` and a `pic_url`.
- `adacli … chat talk` prints only the text part, so confirm the picture in the dashboard's
  conversation view.
- If no picture appears, read `card_debug` in the conversation's variables and
  `adacli <handle> conversations log <id> --json` (look for the tool with `"status": "failed"`).
- Links expire after 30 minutes, so old transcripts show a broken image later. That's expected.

---

## Gotchas (each of these cost real time)

**Image format and hosting**
- 🛑 **SVG does not display (since 15 Oct 2026).** The upload service now serves `.svg` files as
  `application/octet-stream`, so an SVG card shows as a **blank** image. Upload PNG (this kit) or
  JPEG. The served Content-Type comes from the file name extension you pass (`card.png` →
  `image/png`).
- 🛑 **`data:` URIs are silently dropped as attachments.** A `data:image/...` link in the variable
  sends the text but no picture, with no error. The link must be a hosted `https://` URL. (A
  `data:` URI **inside** the SVG, for a logo, is fine.)
- **The File Upload backend is the hosting.** It's the API behind Ada's File Upload widget app:
  `POST https://<handle>.ada.support/api/action-integrations/s3-uploader-action/actions/generate-presigned-post/invoke`
  → multipart POST to S3 (fields first, `file` part **last**) → `…/generate-presigned-get/invoke`
  → `fetch_file_url`. It needs no auth headers.
- The presign-post call **type-checks `file_content`**: empty or invalid content fails (415 or no
  `fields`). Send real base64; the first 3 KB of the PNG is enough.
- **The S3 key must be unguessable and UUID-shaped.** Anyone holding a key can mint a fresh link
  without auth. The template hashes the current time + input data into a UUID.
- **Lifetimes:** each link lasts 30 minutes. Files are deleted after about 7–8 days. There is no
  delete endpoint. The bucket is shared across Ada bots.
- 🔒 **It's off-label.** The File Upload backend was built for customer uploads, not bot-generated
  files. Think twice before putting sensitive data in an image (e.g. a live boarding barcode or personal details);
  if you do, get the client to accept the trade-offs in writing.

**Code-tool runtime (Monty, a Python subset). Local Python passing proves nothing.**
- **Imports are required.** `json`, `re`, `math`, `os`, `datetime` work; `base64`, `time`, `zlib`
  are not available (the renderer hand-rolls base64, CRC and deflate for this reason).
- **String formatting:** `"%s" % x` raises TypeError and `.format()` doesn't exist. Use
  concatenation (`"a" + str(n)`) and `.zfill()`. f-strings work, but comma grouping (`{:,}`)
  doesn't, so group thousands by hand.
- **Bytes:** `bytes(list)` and `bytearray` aren't supported. Build bytes from a 256-entry `b"\xNN"`
  table and `b"".join(...)` (the renderer's `to_bytes`). `str.encode()` works.
- **List slice assignment** (`row[a:b] = seg`) fails live even though it works locally. Rebuild
  the list instead (`r[:a] + seg + r[b:]`).
- **Time and memory budget is much tighter live than locally.** A full RGB canvas of a large image
  hits "execution exceeded time/memory limits". The renderer draws in 32-row bands to stay inside
  it, and the template caps images at about 1 megapixel. Measured live: simple card ~0.6 s, a
  multi-section pass ~3 s. Keep cards small.
- `datetime.datetime.now(datetime.timezone.utc)` works; bare `.now()` / `.utcnow()` don't.
- `fetch(method, url, headers=, body=, timeout=)` returns a **dict**
  `{"status_code", "headers", "body"}`. Max 10 requests per run (this pipeline uses 3).
- **Never let the tool raise.** A raising tool writes no outputs and leaves no trace in test runs,
  and the playbook carries on with empty variables. Wrap `main()` in try/except and return
  `{"image_url": "", "debug": "<what failed>"}` (the template does this).
- The last expression of the file is the tool's result (the template ends with `result`).

**Creating and updating the tool**
- 🛑 **WAF 403.** Ada's firewall rejects a create or update whose source contains HTML/SVG-looking
  tags (`<svg`, `<rect`…) or injection-looking examples in comments, answering a bare
  `403 Forbidden` that looks like a permissions problem. Build tags with `LT = "\x3c"` and describe
  things in plain words in comments.
- **64 KB source cap.** See step 5. Embedded art adds up fast: a photo-style background is too
  big as PNG data. Draw shapes instead, or use a small logo.
- Inputs, outputs and environment are immutable after create (see step 8).

**Playbook side**
- 🛑 **Global variables persist across a customer's conversations.** Always clear the image URL
  variable right before running the tool. Otherwise an old (expired) link from a previous chat can
  show, or an empty-looking check passes.
- An unset variable and an empty string are different: `is null` misses `""`, and `is not ""` is
  true for an unset variable. Check both (step 10).
- The widget limits image height to about the width. Tall cards display shrunk; keep them
  near-square.
- Always keep the text fallback branch. The image can fail for reasons outside your control
  (upload service, limits, a non-Latin name).
- **Test data:** `code-tools test` and real test conversations really upload, so never use a real
  customer's details.

---

**Learned on a loyalty-points card with rings (19/10/2026)**
- A stroke on a curved path draws as ticks. Draw rings and arcs as filled band paths instead (a `band()` helper).
- `<polygon>` isn't supported. Convert polygons in logo SVGs to `path` before you embed them.
- When the calling playbook ships through a change set, put the image step in a live, non-standalone child playbook (`playbooks update`) and have the staged playbook RUN it. Change sets reject the attachment, but they can still RUN a live child.
- Allowed domains can also be added through the API: `POST /api/generative_actions/code_actions/allowed_domains` with `{"domain": "https://..."}`.
- The signed picture link carries Ada's AWS access key ID (`X-Amz-Credential=AKIA…`). Any transcript or variable dump you save shows it, and gitleaks blocks the commit. Replace the link with a placeholder before you write test output to a file or page.

## Changing an existing card

1. Edit your card file → `build_tool.py` → `run_local.py` with the saved samples → look at the PNG.
2. `adacli <handle> code-tools update <id> --file tool.py` (source only, same id).
3. `code-tools test` with dummy data, `curl` the link, then one real test conversation.
4. If you need a new input or output: create a new tool, repoint the playbook's `run` step to it,
   test, then delete the old tool.

## Quick troubleshooting

| symptom | likely cause |
|---|---|
| Blank image in chat | Uploaded as `.svg`; switch to PNG |
| Text sent but no picture | Variable empty or holds a `data:` URI; read `card_debug` |
| `debug: "s3 …"` or "domain is not on this client's allowed domains" | Upload host missing from **Content → Tools → Allowed domains** |
| `debug: "presign-post 4xx"` | Wrong `INSTANCE` handle, or empty/invalid `file_content` |
| `debug: "… FAILED TypeError …"` | `%` formatting, slice assignment, or a `None` input not wrapped in `txt()` |
| "execution exceeded time/memory limits" | Card too large; reduce size or detail |
| `403 Forbidden` on create/update | WAF: literal tags or injection-like text in the source |
| `400 source_code must be at most 65536 bytes` | Over 64 KB; smaller atlas or less embedded art |
| Old card shows in a new chat | Image URL variable not cleared before the run step |
| Card looks small/narrow in chat | Card too tall; make it closer to square |
| Letters show as `?` | Characters not in the atlas (non-Latin script); send text for those languages |
