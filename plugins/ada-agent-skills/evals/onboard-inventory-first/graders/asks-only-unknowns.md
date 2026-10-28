---
type: llm
criteria: "Questions are only about what the config cannot show: the business, channels, systems, extra languages, handoff platform, help content or other settings the config left out. Fail if it asks for the agent name, company description, tone or another value the config holds. Asking no questions passes"
---
Pass if every question it asks is about something the config cannot show: the business, its channels, its
systems, extra languages, or its handoff platform. Fail if it asks for the company description, the agent's
name, or anything else already present in the configuration. Asking no questions is a pass.
