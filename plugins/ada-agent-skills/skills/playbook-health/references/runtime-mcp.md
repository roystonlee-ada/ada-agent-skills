# Playbook health over the Ada MCP

Check the connected tool schemas before retrieval. Use the complete persisted
configuration and graph procedure in
`../../author-playbook/references/runtime-mcp.md`, under "Convert persisted
configuration to a graph". Read related guidance, knowledge, variables and
existing conversation traces through available read operations, following
pagination and retaining source identities. Do not invoke configuration updates,
test runs or actions during this review.

When local execution is available, use the checkers described in
`runtime-cli.md` on the saved decoded playbooks. Otherwise inspect those fields
manually and label the linter NOT RUN. If a connected tool omits complete step
configuration or a related surface, record the missing evidence instead of
assuming coverage.
