## ADDED Requirements
### Requirement: Embedded TS Gateway Startup
The system SHALL provide a TypeScript gateway module that starts inside the Electron main process for desktop mode.

#### Scenario: Desktop app launches
- **WHEN** the desktop app starts in desktop mode
- **THEN** the embedded gateway starts and listens for renderer WebSocket connections

#### Scenario: Desktop app exits
- **WHEN** the desktop app exits
- **THEN** the embedded gateway stops and releases its resources

### Requirement: Protocol Compatibility With Go Gateway
The embedded TypeScript gateway SHALL mirror the Go gateway message types, payloads, and routing behavior used by the desktop renderer.

#### Scenario: Renderer connects to embedded gateway
- **WHEN** the renderer opens a WebSocket connection to the embedded gateway
- **THEN** the gateway accepts the connection and handles messages using the Go gateway protocol
