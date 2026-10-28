---
type: llm
criteria: Cites a source and marks what it could not verify
---
Pass if it cites where the steps come from (Ada docs, a doc page, or the product) and marks any step it could
not verify as OPEN, ASSUMED or unverified. Fail if it presents unverified steps as fact with no source.
