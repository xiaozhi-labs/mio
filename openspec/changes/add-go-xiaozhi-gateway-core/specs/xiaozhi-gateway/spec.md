## ADDED Requirements
### Requirement: XiaoZhi WS Client
The Go gateway SHALL connect to XiaoZhi using WebSocket headers and send a hello handshake with audio params.

#### Scenario: XiaoZhi connection
- **WHEN** the gateway starts a XiaoZhi session
- **THEN** it connects with `Protocol-Version`, `Client-Id`, `Device-Id`, and optional `Authorization` headers

### Requirement: UI Text Bridging
The Go gateway SHALL map XiaoZhi text events to UI messages.

#### Scenario: Streaming LLM output
- **WHEN** XiaoZhi sends `llm` stream events
- **THEN** the gateway emits `full-text` messages with accumulated text

#### Scenario: Speech transcription
- **WHEN** XiaoZhi sends `stt` events
- **THEN** the gateway emits `user-input-transcription`

### Requirement: Control Lifecycle
The Go gateway SHALL send UI `control` messages to indicate conversation start and end.

#### Scenario: Conversation lifecycle
- **WHEN** XiaoZhi starts and ends a response
- **THEN** the gateway emits `control:conversation-chain-start` and `control:conversation-chain-end`
