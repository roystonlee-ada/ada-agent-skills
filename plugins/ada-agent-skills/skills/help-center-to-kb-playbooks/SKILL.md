---
name: help-center-to-kb-playbooks
description: >
  Turn a help center (Zendesk, Intercom, Freshdesk, HelpScout, Notion, or a
  plain website) into an Ada knowledge base plus V2 playbooks, and use playbook
  send-step images for articles that rely on screenshots. Use it whenever
  someone says "turn the help center into KB", "import the help center",
  "convert these articles to playbooks", "migrate the FAQ", "the articles have
  screenshots", or hands over a help center URL, sitemap or export, even if
  they never say "playbook". Covers sorting each article into KB, playbook or
  both, handling every image, building, attaching images, and testing. Not for
  one article edit, or for one playbook from an approved design (use
  author-playbook).
---

# Help center to KB and playbooks

A help center mixes two kinds of content. Facts ("what is the return window")
belong in the KB. Procedures ("how do I reset my router") belong in playbooks,
because a playbook walks the customer through one step at a time and can show a
picture at the right step. Copying everything into the KB loses that: the agent
either dumps a wall of text or invents the steps.

Images drive the split. A screenshot that says "click the green button" helps
only while the customer is looking for that button. Treat KB articles as text
only (ASSUMED: check on the instance before promising otherwise). A playbook
send step can carry the image.

Work on one customer's content at a time. Mark anything you have not verified
OPEN or ASSUMED.

## 0. Pick the runtime

Each step below says what to do, not a command. Read one file for how:
- `adacli` on the path → `references/runtime-cli.md`
- Ada MCP tools present (`get_ada_configuration`, `edit_agent_behavior`) →
  `references/runtime-mcp.md`

The extractor script in `scripts/` runs the same on both.

## 1. Constraints that decide the order of work

Checked against the platform on 28/10/2026. Re-check if it may have moved.

- Changesets cannot author or edit send-step `attachments`. A changeset that
  touches one is rejected, and adacli has no image upload either.
- A playbook that has an image anywhere cannot have its `sections` edited
  through a changeset at all, not even a typo in a neighbouring step.
- So images go on last. Build, test and approve the text-only playbook through
  a changeset first. Attach images as the final step, then make no more
  changeset edits to that playbook's sections.
- Images are stored per playbook and do not survive a copy to another playbook.
  Upload again for each playbook.
- Upload limits: 5 MB, 6000 x 6000 pixels. Convert WebP and SVG to PNG or JPEG
  first.
- Never link the help center's own image URLs into an attachment. They break
  when the site is redesigned.

## 2. Extract

Run the extractor (command in the runtime file). It fetches each article,
converts it to Markdown, downloads every image beside it, and writes
`manifest.json` with each article's last-edit date and each image's size.

Use the help center's official API or export when one exists. It is cleaner than
scraping and keeps article ids for re-sync. Use the script for plain sites.

- Use `--discover` with the index URL. It crawls category, folder and article
  links on the same host. An index page alone under-counts: one test had 87
  articles in the folder links and 92 after the deeper crawl.
- The script warns when a page's content sits in script tags (Next.js
  `__next_f`) and when a page yields very little text. A scrape of such a page
  looks fine and holds nothing. Parse the payload instead, or use the API.
- If a sentence in `article.md` ends mid-way, fetch the raw HTML before blaming
  the script. The source page may be cut off. Tell the customer.
- Keep the raw output in the customer's own project folder, not in the skill.

## 3. Sort every article

Read each article and give it one label. Record the label and the reason in
`manifest.json` so the review shows it.

| Label | Signal | Goes to |
|---|---|---|
| Fact | Policy, definition, pricing, eligibility, "what is" | KB only |
| Procedure, no images | Numbered steps the agent can say in words | Playbook (text) plus a short KB summary for search |
| Procedure with images | Steps that point at a screen, button or photo | Playbook with send-step images plus a text KB summary |
| Decision | "If X do A, if Y do B", needs customer data | Playbook, and an action if it needs a lookup |
| Needs an action | Cancel, refund, change, status check | Playbook calling an action. Flag it as an automation opportunity |
| Dead | Outdated, duplicate, marketing, not customer help | Skip. List it so the customer can confirm |

Push toward automation maturity: when a procedure ends with "contact support to
do X", that is an action candidate, not a finished playbook.

Two checks before you finalise labels:

- Overlap. Help centers answer one question many ways (one test had 6 articles
  on order timing and 5 on refunds). Cluster by the customer's goal and build one
  playbook per cluster, not one per article. Compare overlapping articles for
  conflicts before merging. Do not pick one silently.
- Age. Read the last-edit date. An article untouched for 2 or more years (46 of
  92 in the test) is a claim to verify with the customer, not content to copy.
  Fees, limits and third-party screens go stale first.

## 4. Sort every image

An image has one job. Decide it before building.

| Job | Test | Treatment |
|---|---|---|
| Shows where to act | Text says "click", "tap", "select the icon shown" | Send-step image at that step |
| Shows the expected result | "You should now see..." | Send-step image after the action step |
| Carries data | Table, price chart, schedule as a picture | Transcribe to text into the KB. Do not rely on the agent reading it |
| Decoration | Banner, logo, stock photo | Drop |
| Too small or cropped | Unreadable at chat width | Ask the customer for a better one, or drop it and describe in words |

Open the images. Do not judge them from alt text, which is usually empty. Look
for personal data (a staff or demo email address showed up in one customer's
checkout screenshots) and for a partner's UI, which belongs to someone else and
changes without notice. Put third-party screenshots on hold until the customer
confirms they are current.

Write alt text for every kept image as an instruction to the customer, not a
caption: "The Settings icon, a grey gear at the top right".

Keep one image per send step, near square, about 560 px wide, because the chat
widget caps height near the width. Help center screenshots are usually full
pages: 20 of 65 in the test were taller than the limit. Crop to the part the
customer needs, then shrink. The manifest's `too_tall_for_chat` flag lists
them. Add one red box or arrow when the target is small. A busy full-page
screenshot is worse than no image.

## 5. Build the KB

- One article per intent, one retrievable unit per goal. A link between
  articles does not pull the linked content in, so each article stands alone.
- Split any list of 10 or more near-identical records into one article each.
  A 47-record article failed to answer for one record.
- Describe each image in prose inside the article ("the Settings icon is the
  grey gear at the top right"), so search still finds the article and a channel
  that cannot show images still helps.
- Keep each article under 100 KB. Remove navigation, "was this helpful" and
  related-article lists.
- Check the article language matches a locale the agent uses. An article in a
  locale the agent does not use is never indexed.
- Keep volatile numbers (fees, banded rates, limits) out of prose the agent will
  quote. Have it say what drives the number and point to the live source.
- Import in bulk with the runtime file's route. Prefer an upsert on a supplied
  article id, so a re-run does not duplicate.

## 6. Build the playbooks (text only)

Use the `author-playbook` skill for method. This skill adds the following.

- One playbook per goal, named for what the customer wants ("Reset my router"),
  not the article title.
- Each screenshot step becomes a send step with `instruction` text. Mark where
  the image goes in your build manifest. Do not add `attachments` yet.
- Ask what the customer sees before moving on ("Do you see the Settings
  icon?"), so the next step fits their actual screen. Do not send ten steps and
  ten images in one go.
- End on a check ("Is it working now?"), with a handoff branch for no. Leave no
  dead end.
- Save each procedure's expected conversation as a test case. Stage as a
  changeset, run every case, then get approval on a review page
  (`build-review-page` builds one).

Finish and approve every text edit before step 7.

## 7. Attach the images (last)

Read `references/attach-images.md`. In short:

1. Add each prepared image to its send step in the dashboard editor, with the
   alt text from step 4.
2. Reference it from the step text with `{{img:<attachment id>}}`. The editor
   does this for you. The attachment `id` and `image_id` are different values.
3. Re-read the playbook and confirm `attachments[]` and the reference saved.

This edits the live playbook and skips the stage, diff and promote review. Tell
the person before you do it and get their go-ahead. Do it on a sandbox or draft
first when one exists.

## 8. Test with the images

A passing text test does not prove an image shows. For each image playbook:

- Run the saved cases on the real chat channel, not only a simulation. Confirm
  the image renders and is readable at chat width.
- Open the live chat the way the customer will, follow the steps once, and
  report what you did and what you saw. If you cannot reach it, say so.
- Test a channel without images (SMS, voice, email). The step must still make
  sense from its text alone.

## 9. Hand back

Produce a review page with: before (the help center article) and after (KB
article, and the playbook flow with its images in place), the label and reason
for each article, images kept, held and dropped, and the open decisions last.
Mark it "Proposed, not built" until approved.

Write customer-facing wording in the customer's terms. Do not frame gaps as
failures: call them coverage opportunities.
