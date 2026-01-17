## ADDED Requirements
### Requirement: Config Mapping Compatibility
The Go gateway SHALL read XiaoZhi settings from `system_config` in `conf.yaml`.

#### Scenario: System config mapping
- **WHEN** `system_config.xiaozhi_backend_url` is set
- **THEN** the gateway uses it as the XiaoZhi backend URL

### Requirement: Go Gateway Start Script
The repository SHALL provide a way to start the Go gateway via `start.sh` using an explicit flag.

#### Scenario: Go start
- **WHEN** `MIO_USE_GO_GATEWAY=1` is set
- **THEN** `start.sh` launches the Go gateway with `MIO_HTTP_ADDR` derived from `system_config` host/port
