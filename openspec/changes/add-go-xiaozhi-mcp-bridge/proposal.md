# Change: Add XiaoZhi MCP capture bridge in Go gateway

## Why
The XiaoZhi gateway must support MCP capture tools so XiaoZhi can request camera/screen captures and receive vision analysis results.

## What Changes
- Parse MCP JSON-RPC messages from XiaoZhi and respond to `initialize`, `tools/list`, and `tools/call`
- Forward capture requests to the UI via `mcp-capture-request` and accept `mcp-capture-response`
- Call the vision endpoint from MCP capabilities and return MCP results

## Impact
- Affected specs: `xiaozhi-gateway`
- Affected code: `mio-server/internal/ws`, `mio-server/internal/xiaozhi`
