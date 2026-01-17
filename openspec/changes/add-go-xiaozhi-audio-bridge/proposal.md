# Change: Add XiaoZhi audio bridge to UI audio messages

## Why
The Go gateway currently maps only text/control events. Audio frames from XiaoZhi must be decoded, normalized, and forwarded as UI `audio` messages for playback and lip sync.

## What Changes
- Decode XiaoZhi audio frames to PCM16 and emit UI `audio` messages
- Compute `volumes` and `slice_length` for lip sync
- Emit `backend-synth-complete` on TTS stop

## Impact
- Affected specs: `xiaozhi-gateway`
- Affected code: `mio-server/internal/xiaozhi`, `mio-server/internal/ws`
