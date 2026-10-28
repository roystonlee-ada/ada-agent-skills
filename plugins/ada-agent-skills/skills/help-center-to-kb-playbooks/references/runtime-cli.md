# help-center-to-kb-playbooks on the command line

For Claude Code or any shell with `adacli`. Inside Ada Architect the chat draws
the review and approval steps for you. Outside it, you show them in chat.

| Step in the skill | Command |
|---|---|
| Find articles | `python3 -I <skill folder>/scripts/extract_help_center.py --discover <index url> --out <folder>/raw`. It writes `urls.txt` and `manifest.json` |
| Extract a known list | the same script with `--urls urls.txt` instead of `--discover` |
| Extract a staging help center | add `--allow-private`. By default the script fetches only http and https, and refuses hosts on private, loopback or link-local addresses, for the page and for every image and redirect |
| List existing KB articles | `adacli <instance> knowledge list --limit 100 --json`. The default page is 25, so pass `--limit` or you will think the KB is nearly empty |
| Add a few articles | `adacli <instance> knowledge create --title "<title>" --file <article>.md`. New articles start enabled |
| Add many articles | The Knowledge API: `POST https://<handle>.ada.support/api/v2/knowledge/bulk/articles/` with `Authorization: Bearer <key>` and a raw JSON array of `{id, name, content, knowledge_source_id, language, url}`. Create the source first with `POST /api/v2/knowledge/sources/` and a client-supplied `id`. Re-posting the same `id` updates in place. Create a key with `adacli <instance> api-keys create --key-only` and keep it in an environment variable, never in a file |
| Scrape instead of import | `adacli <instance> knowledge scrape --name "<name>" --urls <url>...`. Check the extractor's warnings first. A scraper loses data on script-rendered pages without saying so |
| Check a source | `adacli <instance> knowledge sources` |
| Bulk disable or edit | Save `knowledge list --json` first. `knowledge update` can reassign an article to the default source and clear its availability rules, so you lose which articles belonged together |
| Build and stage playbooks, save cases, run them | The `author-playbook` skill's `references/runtime-cli.md` |
| Read a playbook back | `adacli <instance> playbooks get <id> --json`. Check `attachments[]` on each send step |

## Notes

- A changeset that includes a playbook with a send-step image is rejected as a
  whole. Stage in batches and leave that playbook out.
- Never promote. The person does it.
- Images attach in the dashboard. See `attach-images.md`.
