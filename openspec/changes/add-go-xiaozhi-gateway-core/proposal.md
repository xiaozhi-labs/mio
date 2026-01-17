# Change: Implement Go XiaoZhi gateway core bridging

## Why
We need the Go gateway to establish a XiaoZhi connection and map core text/control events to the existing UI WebSocket protocol.

## What Changes
- Add XiaoZhi WebSocket client with headers, hello handshake, and read loop
- Implement frontend WS session to route `text-input` and `interrupt-signal`
- Map XiaoZhi text events to UI `full-text` and `user-input-transcription`

## Impact
- Affected specs: `xiaozhi-gateway`
- Affected code: `mio-server/internal/ws`, `mio-server/internal/xiaozhi`, `mio-server/cmd/main.go`
