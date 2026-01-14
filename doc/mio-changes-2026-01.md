# Mio Local Changes (2026-01)

This document tracks local changes applied in this workspace for troubleshooting and future tuning.

## Runtime & Startup

- Public bind: `conf.yaml` uses `system_config.host: "::"` for IPv4/IPv6 dual stack.
- HTTPS enabled: `run_server.py` serves with self-signed certs (`certs/server.key`, `certs/server.crt`).
- Quick start script: `scripts/start_public.sh` now
  - unsets proxy env
  - generates self-signed cert if missing
  - builds web (`npm run build:web`) and syncs `web/dist/web` → `frontend/`
  - checks/clears port and launches `uv run run_server.py`
- Cert helper: `scripts/gen_self_signed_cert.sh`

## XiaoZhi Gateway & MCP

- MCP JSON-RPC support (initialize/tools/list/tools/call) with tools:
  - `take_photo`
  - `take_screenshot`
- Web capture request/response:
  - Server → web: `mcp-capture-request`
  - Web → server: `mcp-capture-response` (base64 image + mime)
- Vision call: uses MCP initialize capabilities `vision.url` / `vision.token` to POST multipart image.

Key files:
- `src/open_llm_vtuber/xiaozhi_gateway.py`
- `src/open_llm_vtuber/xiaozhi_mcp_server.py`
- `src/open_llm_vtuber/websocket_handler.py`
- `web/src/renderer/src/services/websocket-handler.tsx`
- `web/src/renderer/src/hooks/utils/use-media-capture.tsx`

## Frontend WebSocket Reconnect

- Auto reconnect with exponential backoff in `web/src/renderer/src/services/websocket-service.tsx`.
- Manual `disconnect()` disables reconnect.

## Audio Streaming (PCM) & TTS

- Backend now sends both WAV + raw PCM in `audio` payload.
- Web prefers PCM playback via `AudioWorklet/AudioContext` with queueing.
- PCM playback now resumes AudioContext; if resume fails, fallback to WAV.

Key files:
- `src/open_llm_vtuber/xiaozhi_gateway.py`
- `web/src/renderer/src/utils/pcm-player.ts`
- `web/src/renderer/src/hooks/utils/use-audio-task.ts`

## Voice Interruption

- Added setting: “Voice Interrupt AI” (default OFF).
- When OFF: VAD ignores speech during AI playback; no auto-interrupt.
- When ON: user speech can interrupt if AI is currently playing audio.

Key files:
- `web/src/renderer/src/context/vad-context.tsx`
- `web/src/renderer/src/hooks/sidebar/setting/use-asr-settings.ts`
- `web/src/renderer/src/components/sidebar/setting/asr.tsx`
- `web/src/renderer/src/locales/en/translation.json`
- `web/src/renderer/src/locales/zh/translation.json`

## HTTPS & CORS Notes

- IPv6 access required dynamic base URL/WS URL to avoid 127.0.0.1 CORS issues.
- Web now derives base/WS URLs from `window.location` (same-origin).

## Build Artifacts

- Web build output is synced to `frontend/` after each change.
