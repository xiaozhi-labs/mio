# Change: Auto-generate in-memory TLS for Go server

## Why
Local HTTPS access currently fails when the certificate is missing, causing TLS handshake errors and blocking microphone access in browsers. We want HTTPS to “just work” without manual cert management in dev.

## What Changes
- Default to TLS when no cert files are provided.
- If TLS is required but no cert exists, generate a self-signed certificate in memory (no disk writes).
- Certificate should include SANs for loopback and the configured host.

## Impact
- Affected specs: http-server
- Affected code: `mio-server/cmd/main.go`, `mio-server/internal/config/config.go`
