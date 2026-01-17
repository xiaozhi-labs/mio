# Change: Add mic audio uplink to XiaoZhi

## Why
The Go gateway should forward microphone audio from the UI to XiaoZhi so speech input works end-to-end.

## What Changes
- Convert UI `mic-audio-data` float32 frames to PCM16
- Send audio frames to XiaoZhi and manage listen start/stop
- Emit conversation start signals on audio end

## Impact
- Affected specs: `xiaozhi-gateway`
- Affected code: `mio-server/internal/ws`, `mio-server/internal/xiaozhi`
