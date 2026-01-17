## ADDED Requirements
### Requirement: UI Protocol Compatibility
The Go gateway SHALL preserve the UI WebSocket protocol defined in `doc/web-ui.md` and keep message `type` and field names consistent.

#### Scenario: Text input with streaming output
- **WHEN** the client sends a `text-input` message
- **THEN** the gateway emits `control:conversation-chain-start`, streaming `full-text`, `audio` chunks, `backend-synth-complete`, and `control:conversation-chain-end` in order

### Requirement: XiaoZhi Connection Management
The Go gateway SHALL manage XiaoZhi connections using configuration headers and support reconnect with backoff.

#### Scenario: XiaoZhi disconnect
- **WHEN** XiaoZhi disconnects mid-stream
- **THEN** the gateway sends an `error` message to the client and closes the conversation with `control:conversation-chain-end`

### Requirement: Audio Normalization
The Go gateway SHALL normalize XiaoZhi audio frames into the UI `audio` message format, including `volumes` and `slice_length`.

#### Scenario: XiaoZhi audio frame
- **WHEN** XiaoZhi returns an audio frame
- **THEN** the gateway emits an `audio` message with `audio_format`, `audio_sample_rate`, `audio_channels`, `volumes`, and `slice_length`

### Requirement: Conversation State Integrity
The Go gateway SHALL maintain per-client conversation state and handle interrupt signals safely.

#### Scenario: Interrupt during playback
- **WHEN** the client sends `interrupt-signal` while audio is streaming
- **THEN** the gateway stops streaming, emits `interrupt-signal`, and finalizes the conversation with `control:conversation-chain-end`

### Requirement: Observability and Diagnostics
The Go gateway SHALL emit structured logs and metrics to support diagnosing XiaoZhi integration issues.

#### Scenario: Error diagnosis
- **WHEN** a XiaoZhi error occurs
- **THEN** logs include `client_uid`, `history_uid`, and an error code or message for root cause analysis

### Requirement: Go Framework Choices
The Go gateway SHALL use `gin` for HTTP routing and `gorilla/websocket` for WebSocket handling.

#### Scenario: Framework verification
- **WHEN** the gateway is initialized
- **THEN** the HTTP server uses `gin` and WebSocket handlers use `gorilla/websocket`
