# Change: Add Electron-embedded TypeScript gateway module

## Why
The desktop client should run without requiring an external Go service while keeping protocol behavior aligned with the existing Go gateway.

## What Changes
- Add a TypeScript gateway module that runs inside the Electron main process.
- Implement the same WebSocket protocol behavior as the Go gateway for desktop mode.
- Wire Electron startup/shutdown to start and stop the gateway module.
- Update desktop client configuration to connect to the embedded gateway.

## Impact
- Affected specs: run-ts-gateway
- Affected code: `web/src/main/`, `web/src/renderer/`, new `web/src/main/gateway/`
