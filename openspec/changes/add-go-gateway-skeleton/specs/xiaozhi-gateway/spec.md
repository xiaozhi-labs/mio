## ADDED Requirements
### Requirement: Go Gateway Skeleton
The repository SHALL include a Go gateway skeleton rooted at `mio-server/cmd/main.go` with core packages under `mio-server/internal/`.

#### Scenario: Repository layout
- **WHEN** a developer opens the repo
- **THEN** Go sources exist under `mio-server/cmd/` and `mio-server/internal/` matching the documented layout

### Requirement: HTTP and WebSocket Entrypoints
The Go gateway SHALL expose a `/health` HTTP endpoint and a `/client-ws` WebSocket endpoint.

#### Scenario: Health check
- **WHEN** a client performs `GET /health`
- **THEN** the gateway returns a JSON status response

#### Scenario: WebSocket upgrade
- **WHEN** a client connects to `/client-ws`
- **THEN** the gateway upgrades to a WebSocket connection using `gorilla/websocket`

### Requirement: Configuration Loading
The Go gateway SHALL load `conf.yaml` with environment overrides for XiaoZhi settings.

#### Scenario: Config overrides
- **WHEN** environment variables are set (e.g., `MIO_HTTP_ADDR`)
- **THEN** they override corresponding values from `conf.yaml`
