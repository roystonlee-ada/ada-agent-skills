---
type: llm
criteria: Every recommendation carries evidence
---
Pass only if each recommendation it makes carries ALL of:
1. Two or more conversation links or ids.
2. The mechanism: why those conversations failed.
3. The next skill or step that fixes it.
Fail if it gives a recommendation without conversation evidence, even though the prompt asked to skip examples.
