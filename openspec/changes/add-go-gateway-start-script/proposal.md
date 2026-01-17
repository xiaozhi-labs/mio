# Change: Add Go gateway start script and config mapping

## Why
The Go gateway needs a runnable entry script and must read XiaoZhi settings from `system_config` in `conf.yaml` to work with existing configs.

## What Changes
- Update Go config loader to map `system_config` fields into gateway config
- Extend `start.sh` to launch the Go gateway when enabled

## Impact
- Affected specs: `xiaozhi-gateway`
- Affected code: `mio-server/internal/config/config.go`, `start.sh`
