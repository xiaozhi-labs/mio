## 1. Mic Audio Uplink
- [x] 1.1 Convert UI `mic-audio-data` float32 samples to PCM16
- [x] 1.2 Send audio frames to XiaoZhi connection
- [x] 1.3 Start `listen` on first audio frame and stop on `mic-audio-end`
- [x] 1.4 Emit conversation start signals on audio end

## 2. Validation
- [x] 2.1 Ensure `go test ./...` passes
