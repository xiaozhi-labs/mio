## ADDED Requirements
### Requirement: MCP Capture Tools
The Go gateway SHALL implement MCP `initialize`, `tools/list`, and `tools/call` for capture tools.

#### Scenario: MCP tool listing
- **WHEN** XiaoZhi requests `tools/list`
- **THEN** the gateway returns `take_photo` and `take_screenshot` tool schemas

### Requirement: Capture Request Bridge
The Go gateway SHALL forward capture requests to the UI and return results to XiaoZhi.

#### Scenario: Capture request
- **WHEN** XiaoZhi calls `take_photo`
- **THEN** the gateway sends `mcp-capture-request` to the UI and responds with MCP result content

### Requirement: Vision Endpoint Integration
The Go gateway SHALL call the vision endpoint provided by MCP `initialize` capabilities.

#### Scenario: Vision analysis
- **WHEN** the UI returns a capture image
- **THEN** the gateway uploads it to the vision URL and returns the response as MCP tool result
