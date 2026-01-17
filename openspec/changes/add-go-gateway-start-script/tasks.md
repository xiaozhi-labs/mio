## 1. Config Mapping
- [x] 1.1 Map `system_config` host/port and XiaoZhi settings into Go config
- [x] 1.2 Compute HTTP listen address from host/port when `http_addr` is unset

## 2. Start Script
- [x] 2.1 Add `MIO_USE_GO_GATEWAY=1` path in `start.sh`
- [x] 2.2 Set `MIO_HTTP_ADDR` from conf host/port when launching Go

## 3. Validation
- [x] 3.1 Ensure `go test ./...` passes
