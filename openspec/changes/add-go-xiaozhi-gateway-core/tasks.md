## 1. XiaoZhi Client
- [x] 1.1 Implement XiaoZhi WS client with headers and hello handshake
- [x] 1.2 Add read loop with JSON parsing for `stt`, `llm`, `text`, `tts`, `goodbye`, `mcp`
- [x] 1.3 Expose callbacks for text and control events

## 2. Frontend WS Bridge
- [x] 2.1 Extend WS handler to parse incoming UI messages
- [x] 2.2 Route `text-input` and `interrupt-signal` to XiaoZhi client
- [x] 2.3 Emit `full-text`, `user-input-transcription`, and `control` messages to UI

## 3. Validation
- [x] 3.1 Ensure `go test ./...` passes
