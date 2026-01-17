## 1. Go Skeleton
- [x] 1.1 Create Go module and dependencies (gin + gorilla/websocket + viper + zap)
- [x] 1.2 Add `mio-server/cmd/main.go` bootstrap with config load and HTTP server
- [x] 1.3 Add HTTP router with `/health` and `/client-ws` routes
- [x] 1.4 Add WS handler stub using gorilla/websocket
- [x] 1.5 Add config loader for `conf.yaml` and env overrides
- [x] 1.6 Scaffold placeholder packages for XiaoZhi, conversation, group, storage, media, observability

## 2. Validation
- [x] 2.1 Ensure `go test ./...` passes (no tests, just build)
