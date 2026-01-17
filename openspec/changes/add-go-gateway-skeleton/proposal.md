# Change: Add Go gateway skeleton under mio-server

## Why
We need a compile-ready Go gateway skeleton using gin + gorilla/websocket to start implementation under the approved XiaoZhi gateway plan.

## What Changes
- Add Go module under `mio-server/` with `mio-server/cmd/main.go` entrypoint
- Scaffold `mio-server/internal/` packages for HTTP, WS, XiaoZhi, config, and observability
- Provide minimal health endpoint and WS upgrade handler

## Impact
- Affected specs: `xiaozhi-gateway`
- Affected code: new Go sources under `mio-server/cmd/` and `mio-server/internal/`
