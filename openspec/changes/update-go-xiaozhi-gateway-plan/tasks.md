## 1. Planning Updates
- [x] 1.1 Update `doc/go-backend-migration.md` with XiaoZhi-first architecture, protocol mapping, state rules, observability, and acceptance checklist
- [x] 1.2 Define XiaoZhi gateway acceptance scenarios and risks in spec deltas
- [x] 1.3 Capture interface contract expectations for XiaoZhi (headers, reconnect, error mapping)

## 2. Implementation Prep (No Code Yet)
- [x] 2.1 Identify UI protocol messages used by the frontend (`doc/web-ui.md`)
- [x] 2.2 Outline mapping from XiaoZhi events to UI messages for Go gateway
- [x] 2.3 Enumerate minimal metrics/log fields required for diagnosing XiaoZhi integration
- [x] 2.4 Confirm framework choices (`gin`, `gorilla/websocket`) and repo layout (`mio-server/cmd/main.go`)
- [x] 2.5 Update design/doc with directory layout
