---
type: llm
criteria: Ranks by conversations removed
---
Pass if the reply recommends fixing missing knowledge (knowledge_unavailable, 212) first, ahead of missing tools
(tool_unavailable, 148), on the basis of how many conversations each would remove.
