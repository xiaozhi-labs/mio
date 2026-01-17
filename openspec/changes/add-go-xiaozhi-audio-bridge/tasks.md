## 1. XiaoZhi Audio Decode
- [x] 1.1 Add Opus decode path for XiaoZhi binary frames
- [x] 1.2 Expose decoded PCM frames via callbacks

## 2. UI Audio Emission
- [x] 2.1 Convert PCM to base64 `audio_pcm`
- [x] 2.2 Compute `volumes` and `slice_length`
- [x] 2.3 Send `audio` messages with `audio_format=pcm16`
- [x] 2.4 Emit `backend-synth-complete` on TTS stop

## 3. Validation
- [x] 3.1 Ensure `go test ./...` passes
