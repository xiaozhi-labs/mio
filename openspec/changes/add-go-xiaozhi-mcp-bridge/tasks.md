## 1. MCP Parsing and Responses
- [x] 1.1 Parse MCP JSON-RPC payloads from XiaoZhi
- [x] 1.2 Respond to `initialize` and `tools/list` with capture tools
- [x] 1.3 Handle `tools/call` by triggering capture flow

## 2. Capture Flow
- [x] 2.1 Send `mcp-capture-request` to UI and await `mcp-capture-response`
- [x] 2.2 Decode base64/data URL image payloads
- [x] 2.3 Call vision endpoint and return MCP result

## 3. Validation
- [x] 3.1 Ensure `go test ./...` passes
