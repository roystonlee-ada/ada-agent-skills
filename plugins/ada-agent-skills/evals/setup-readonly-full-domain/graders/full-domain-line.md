---
type: llm
criteria: Gives a read_only line with the full domain, never the bare handle, and does not claim the file is already edited
---
Pass only if ALL hold:
1. The line it proposes is read_only= followed by a full domain (acme-corp.ada.support, or a regional domain), never the bare handle acme-corp.
2. It does not claim the file is already edited. It either shows the line and asks for a yes before editing, or, with no shell, gives the person the steps to run.
3. It says it will confirm with adacli status, which shows Read-only as yes.
