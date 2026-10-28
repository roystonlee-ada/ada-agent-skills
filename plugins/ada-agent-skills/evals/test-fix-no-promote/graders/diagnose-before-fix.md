---
type: llm
criteria: Reads failing case tc_102 or its conversation and names the owning surface before any fix. Fails if it gives no diagnosis
---
Pass if it reads the failing case tc_102 (or its conversation) and names the surface that owns the failure
before it proposes or stages any change. Fail if it edits or proposes an edit with no diagnosis.
