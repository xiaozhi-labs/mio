## Context
The current migration plan assumes local ASR/LLM/TTS services, but XiaoZhi provides a unified model service via WebSocket. The gateway design must preserve the UI protocol while adapting XiaoZhi streams, handling reconnects, and maintaining stable conversation state.

## Goals / Non-Goals
- Goals:
  - Keep UI protocol stable and map XiaoZhi events into existing message types
  - Define state rules and reconnection behaviors for XiaoZhi streaming
  - Provide observability and acceptance criteria for XiaoZhi integration
- Non-Goals:
  - Implement Go gateway code in this change
  - Change frontend protocol or UI state management

## Decisions
- Decision: Go gateway remains the protocol adapter and state owner; XiaoZhi is the only model provider.
- Decision: Use explicit mapping rules for `control`, `full-text`, `audio`, and `backend-synth-complete` sequences.
- Decision: Use `gin` for HTTP routing and `gorilla/websocket` for WebSocket handling.
- Decision: Place Go sources under `mio-server/` with `mio-server/cmd/main.go` as the entry point.

## Alternatives considered
- Frontend direct-to-XiaoZhi integration: rejected due to protocol mismatch, security exposure, and UI state risk.

## Risks / Trade-offs
- XiaoZhi disconnects can desynchronize UI state; mitigated by strict start/end pairing and error mapping.
- Audio frame differences can affect lip sync; mitigated by conversion and RMS verification.

## Migration Plan
1) Update migration doc and spec deltas
2) Review/approve plan before any implementation

## Directory Layout
```
mio-server/cmd/main.go
mio-server/internal/http/router.go
mio-server/internal/ws/hub.go
mio-server/internal/ws/handler.go
mio-server/internal/ws/types.go
mio-server/internal/conversation/orchestrator.go
mio-server/internal/conversation/state.go
mio-server/internal/xiaozhi/client.go
mio-server/internal/xiaozhi/types.go
mio-server/internal/group/group.go
mio-server/internal/config/config.go
mio-server/internal/storage/history.go
mio-server/internal/media/audio.go
mio-server/internal/observability/metrics.go
```

## Open Questions
- Exact XiaoZhi error codes and end-of-stream semantics to map into UI messages
