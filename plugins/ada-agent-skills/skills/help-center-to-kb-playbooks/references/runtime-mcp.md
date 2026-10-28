# help-center-to-kb-playbooks over the Ada MCP

For anyone connected to an AI agent's Ada MCP server. Checked against the live
tool definitions on 28/10/2026. Your host may prefix the tool names.

| Step in the skill | Tool call |
|---|---|
| Find articles | Run `scripts/extract_help_center.py` from a shell with `--discover <index url> --out <folder>/raw`. It needs Python 3 and no other install. Without a shell, ask the person to run it and share `manifest.json`, or use the help center's own export |
| Read the platform guide | `get_improvement_guide`, once per session |
| List existing KB articles | `search_knowledge` with a short `query` (3 characters or more). It matches titles only, 25 results at most, so search several short terms |
| Add or edit articles | `edit_agent_behavior`. Call it with `operation: describe_entity` first to read the knowledge article schema, then change one article and check the preview before you do the rest. If it has no knowledge article entity, use a knowledge source (`edit_agent_config` with `entity_type: knowledge_source`) or ask the person for the dashboard import |
| Add many articles | The Knowledge API, from a shell, as in `runtime-cli.md`. The MCP has no bulk path that I saw |
| Build and stage playbooks, save cases, run them | The `author-playbook` skill's `references/runtime-mcp.md` |
| Read a playbook back | `list_entities` with `entity_type: playbooks`, then `edit_agent_behavior` with `operation: describe_entity` and `entity_type: playbook`. Check `attachments[]` on each send step |

## Notes

- The MCP cannot upload or attach an image. Images attach in the dashboard. See
  `attach-images.md`.
- `edit_agent_config` edits go live at once, after the person confirms the
  preview. Never set `confirmed` without their explicit yes.
- Never promote. The person does it.
