## Context
Desktop mode currently relies on a Go gateway for protocol handling. The goal is to embed an equivalent gateway in the Electron main process for a simpler desktop distribution.

## Goals / Non-Goals
- Goals:
  - Provide a TypeScript gateway module that mirrors the Go gateway protocol.
  - Run the gateway inside the Electron main process with controlled lifecycle.
  - Keep renderer protocol usage unchanged.
- Non-Goals:
  - Replacing the Python backend.
  - Extending protocol behavior beyond the Go gateway.

## Decisions
- Decision: Implement a Node WebSocket server in Electron main process.
- Decision: Reuse the existing protocol message types and payloads to avoid renderer changes.

## Risks / Trade-offs
- Node single-threaded runtime may have different performance characteristics than Go.
- Extra care needed to avoid blocking the Electron main process with audio or heavy work.

## Migration Plan
1. Implement TS gateway in isolation and add feature flag or config to opt-in.
2. Switch desktop mode to use embedded gateway by default once stable.
3. Keep Go gateway as fallback for debugging until parity is verified.

## Open Questions
- Which parts of the Go gateway are mandatory for the desktop mode MVP?
- Should the embedded gateway proxy to external services or load configuration locally?
