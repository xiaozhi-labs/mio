# Web UI Layout and Components

This document describes the current web UI layout and main React components in `web/src/renderer/src`.

## High-level layout

Entry: `web/src/renderer/src/App.tsx`

Window mode layout (`mode === "window"`):
- Left sidebar: `Sidebar` (collapsible)
- Main content area:
  - `Background` (camera or static image)
  - `WebSocketStatus` badge (top-left)
  - `Subtitle` overlay (bottom center; image panel on right when markdown images are present)
  - `Footer` (input + controls)
- Live2D canvas is rendered behind the window UI in its own full-size layer.

Pet mode layout (`mode === "pet"`):
- Live2D canvas only
- `InputSubtitle` floating input widget (Electron)

Shared layer:
- `Live2D` canvas wrapper is always present (independent from window UI).

### Layout diagram (window mode)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Live2D canvas layer (always present)                                      │
│  - <Live2D /> renders to #canvas                                          │
└──────────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────┐
│ Window UI (mode === "window")                                            │
│                                                                          │
│ ┌───────────────┐  ┌───────────────────────────────────────────────────┐ │
│ │ Sidebar       │  │ Main content                                      │ │
│ │ - History     │  │ - Background (image/camera)                       │ │
│ │ - Settings    │  │ - WS status badge (top-left)                      │ │
│ │ - Group       │  │ - Subtitle overlay (bottom-center)                │ │
│ └───────────────┘  │   - Markdown images panel (right side)            │ │
│                    │ - Footer (input + controls)                       │ │
│                    └───────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

### Layout diagram (pet mode)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Live2D canvas layer (always present)                                      │
│  - <Live2D /> renders to #canvas                                          │
└──────────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────┐
│ Pet UI (mode === "pet")                                                   │
│  - InputSubtitle floating widget (Electron only)                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## App composition and providers

App providers and side effects (outer to inner):
- `ModeProvider`: window vs pet mode and global styles
- `CameraProvider`: camera streams (background or live)
- `ScreenCaptureProvider`: screen capture stream
- `CharacterConfigProvider`: character config
- `ChatHistoryProvider`: messages and history list
- `AiStateProvider`: AI state machine
- `ProactiveSpeakProvider`: proactive speak control
- `Live2DConfigProvider`: Live2D model info/config
- `SubtitleProvider`: subtitle text + show/hide
- `VADProvider`: voice activity detection
- `BgUrlProvider`: background image and camera background toggle
- `GroupProvider`: group session state
- `BrowserProvider`: browser view context for tool calls
- `WebSocketHandler`: websocket lifecycle + message routing

## Main UI components

### Live2D canvas
- Component: `web/src/renderer/src/components/canvas/live2d.tsx`
- Hooks:
  - `useLive2DResize` to resize canvas on layout changes
  - `useLive2DModel` to load/instantiate model
  - `useAudioTask` for TTS audio playback + lip sync
  - `useInterrupt` to allow interrupting playback
  - `useLive2DExpression` to reset expressions on idle

### Background layer
- Component: `web/src/renderer/src/components/canvas/background.tsx`
- Uses camera background stream if enabled, otherwise uses image from `BgUrlProvider`.

### Subtitle overlay
- Component: `web/src/renderer/src/components/canvas/subtitle.tsx`
- Shows subtitle text from `SubtitleContext` when enabled.
- Markdown image handling:
  - Detects `![alt](url)` in subtitle text.
  - Removes markdown from subtitle text.
  - Renders images in a right-side panel inside the canvas overlay.

### WebSocket status badge
- Component: `web/src/renderer/src/components/canvas/ws-status.tsx`
- Shows websocket state (connected/connecting) and supports click-to-reconnect.

### Sidebar
- Component: `web/src/renderer/src/components/sidebar/sidebar.tsx`
- Key panels:
  - Chat history panel: `components/sidebar/chat-history-panel.tsx`
  - History drawer: `components/sidebar/history-drawer.tsx`
  - Group drawer: `components/sidebar/group-drawer.tsx`
  - Settings UI: `components/sidebar/setting/setting-ui.tsx`

### Footer
- Component: `web/src/renderer/src/components/footer/footer.tsx`
- Contains input field, mic controls, camera/screen controls, and action buttons.

### Electron input subtitle (pet mode)
- Component: `web/src/renderer/src/components/electron/input-subtitle.tsx`
- Draggable widget for text input and status indicators.

## Component tree (window mode)

```
App
└─ AppWithGlobalStyles
   └─ Providers
      └─ WebSocketHandler
         └─ AppContent
            ├─ Live2D (canvas layer)
            └─ Window UI
               ├─ TitleBar (Electron only)
               └─ Layout (Flex)
                  ├─ Sidebar
                  │  ├─ ChatHistoryPanel
                  │  ├─ HistoryDrawer
                  │  ├─ GroupDrawer
                  │  └─ SettingUI
                  └─ MainContent
                     ├─ Background
                     ├─ WebSocketStatus
                     ├─ Subtitle (text + right-side images)
                     └─ Footer
```

## Component tree (pet mode)

```
App
└─ AppWithGlobalStyles
   └─ Providers
      └─ WebSocketHandler
         └─ AppContent
            ├─ Live2D (canvas layer)
            └─ InputSubtitle (Electron only)
```

## Messaging and state flow

### WebSocket handling
- `web/src/renderer/src/services/websocket-handler.tsx`
  - Routes server messages to contexts (subtitle, history, config, group, etc.)
  - Updates subtitle via `setSubtitleText`.
  - In XiaoZhi mode, `full-text` updates update the latest AI message via `upsertAIMessage`.

### Chat history
- Context: `web/src/renderer/src/context/chat-history-context.tsx`
  - `appendHumanMessage`, `appendAIMessage`, `upsertAIMessage`, `appendOrUpdateToolCallMessage`.
  - Used by sidebar history panel and history drawer.
- History drawer list data: `HistoryInfo` via `web/src/renderer/src/context/websocket-context.tsx`.

### Audio playback and subtitle updates
- `web/src/renderer/src/hooks/utils/use-audio-task.ts`
  - Plays audio (wav or pcm).
  - Updates subtitle from `display_text` and appends to chat history.
  - Signals playback completion to backend.

## Styling and layout configuration

- Layout styles: `web/src/renderer/src/layout.tsx`
- Canvas styles: `web/src/renderer/src/components/canvas/canvas-styles.tsx`
- Sidebar styles: `web/src/renderer/src/components/sidebar/sidebar-styles.tsx`
- Footer styles: `web/src/renderer/src/components/footer/footer-styles.tsx`

## Notes

- Subtitle rendering is suppressed when `showSubtitle` is false.
- Markdown image rendering is supported in:
  - Chat history panel (`chat-history-panel.tsx`)
  - Canvas subtitle overlay (`subtitle.tsx`)

## WebSocket message types (UI-facing)

Server → client (handled in `web/src/renderer/src/services/websocket-handler.tsx`):
- `control`: `{ text }` control signals (`conversation-chain-start`, `conversation-chain-end`, `start-mic`, `stop-mic`)
- `set-model-and-conf`: `{ model_info, conf_name, conf_uid, client_uid }`
- `full-text`: `{ text }` subtitle + XiaoZhi full-text sync
- `config-files`: `{ configs }`
- `config-switched`: `{}` triggers reload + history reset
- `background-files`: `{ files }`
- `audio`: `{ audio?, audio_pcm?, audio_format?, audio_sample_rate?, audio_channels?, volumes?, slice_length?, display_text?, actions?, forwarded? }`
- `history-data`: `{ messages }`
- `new-history-created`: `{ history_uid }`
- `history-deleted`: `{ history_uid, success }`
- `history-list`: `{ histories }`
- `user-input-transcription`: `{ text }`
- `error`: `{ message }`
- `group-update`: `{ members, is_owner }`
- `group-operation-result`: `{ message, success }`
- `backend-synth-complete`: `{}`
- `conversation-chain-end`: `{}`
- `force-new-message`: `{}`
- `interrupt-signal`: `{ text }` forwarded interrupt
- `tool_call_status`: `{ tool_id, tool_name, name?, status, content?, timestamp?, browser_view? }`
- `mcp-capture-request`: `{ request_id, source, question?, display? }`

Client → server (sent via `wsService.sendMessage` and handled in `src/open_llm_vtuber/websocket_handler.py`):
- `fetch-history-list`: `{}`
- `fetch-and-set-history`: `{ history_uid }`
- `create-new-history`: `{}`
- `delete-history`: `{ history_uid }`
- `text-input`: `{ text }`
- `mic-audio-data`: `{ audio: float[] }`
- `mic-audio-end`: `{}`
- `raw-audio-data`: `{ audio: number[] }`
- `interrupt-signal`: `{ text? }`
- `audio-play-start`: `{ display_text, forwarded }` (group sync)
- `fetch-configs`: `{}`
- `switch-config`: `{ file }`
- `fetch-backgrounds`: `{}`
- `request-init-config`: `{}`
- `heartbeat`: `{}`
- `mcp-capture-response`: `{ request_id, success, image?, mime_type?, message? }`
- `add-client-to-group` / `remove-client-from-group`: `{ action?, uids? }`
- `request-group-info`: `{}`
- `ai-speak-signal`: `{}` (rejected in XiaoZhi mode)
