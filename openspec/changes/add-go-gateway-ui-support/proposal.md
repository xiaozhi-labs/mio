# Change: Add Go gateway UI support and Opus uplink

## Why
The Go gateway must serve static assets and implement UI protocol features (config/history/group) to be usable, and support Opus mic uplink per XiaoZhi expectations.

## What Changes
- Serve static assets for frontend, models, backgrounds, and web tools
- Implement UI WebSocket messages for configs, history, and group operations
- Support Opus mic uplink using `github.com/godeps/opus`

## Impact
- Affected specs: `xiaozhi-gateway`
- Affected code: `mio-server/internal/http`, `mio-server/internal/ws`, `mio-server/internal/config`, `mio-server/internal/storage`, `mio-server/internal/group`, `mio-server/internal/xiaozhi`
