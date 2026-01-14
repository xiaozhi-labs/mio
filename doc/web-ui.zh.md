# Web UI 界面与组件文档

本文档描述 `web/src/renderer/src` 中的当前 Web UI 布局与主要组件。

## 总体布局

入口文件：`web/src/renderer/src/App.tsx`

窗口模式（`mode === "window"`）：
- 左侧侧边栏：`Sidebar`（可折叠）
- 主内容区：
  - `Background`（摄像头或静态背景图）
  - `WebSocketStatus` 徽标（左上角）
  - `Subtitle` 叠层（底部居中；若含 markdown 图片则在右侧显示图片）
  - `Footer`（输入与控制区）
- Live2D 画布位于 UI 下层独立渲染。

宠物模式（`mode === "pet"`）：
- 仅 Live2D 画布
- `InputSubtitle` 浮动输入组件（Electron）

共享层：
- `Live2D` 画布层始终存在（不依赖 window UI）。

### 布局示意（窗口模式）

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Live2D 画布层（始终存在）                                                 │
│  - <Live2D /> 渲染到 #canvas                                              │
└──────────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────┐
│ Window UI（mode === "window"）                                           │
│                                                                          │
│ ┌───────────────┐  ┌───────────────────────────────────────────────────┐ │
│ │ Sidebar       │  │ 主内容区                                           │ │
│ │ - 历史记录     │  │ - Background（背景图/摄像头）                      │ │
│ │ - 设置         │  │ - WS 状态徽标（左上）                             │ │
│ │ - 群组         │  │ - Subtitle（底部居中）                            │ │
│ └───────────────┘  │   - Markdown 图片面板（右侧）                      │ │
│                    │ - Footer（输入与控制）                             │ │
│                    └───────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

### 布局示意（宠物模式）

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Live2D 画布层（始终存在）                                                 │
│  - <Live2D /> 渲染到 #canvas                                              │
└──────────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────┐
│ Pet UI（mode === "pet"）                                                  │
│  - InputSubtitle 浮动输入组件（仅 Electron）                              │
└──────────────────────────────────────────────────────────────────────────┘
```

## App 结构与 Providers

Provider 由外到内：
- `ModeProvider`：窗口/宠物模式与全局样式
- `CameraProvider`：摄像头流（背景或前景）
- `ScreenCaptureProvider`：屏幕捕获流
- `CharacterConfigProvider`：角色配置
- `ChatHistoryProvider`：消息与历史列表
- `AiStateProvider`：AI 状态机
- `ProactiveSpeakProvider`：主动发言控制
- `Live2DConfigProvider`：Live2D 模型配置
- `SubtitleProvider`：字幕文本与显隐
- `VADProvider`：语音活动检测
- `BgUrlProvider`：背景图/摄像头背景开关
- `GroupProvider`：群组会话
- `BrowserProvider`：工具调用的浏览器上下文
- `WebSocketHandler`：WebSocket 生命周期与消息路由

## 主要组件

### Live2D 画布
- 文件：`web/src/renderer/src/components/canvas/live2d.tsx`
- 关键 Hook：
  - `useLive2DResize`：画布尺寸自适应
  - `useLive2DModel`：模型加载
  - `useAudioTask`：TTS 音频与口型同步
  - `useInterrupt`：打断播放
  - `useLive2DExpression`：空闲时重置表情

### 背景层
- 文件：`web/src/renderer/src/components/canvas/background.tsx`
- 摄像头背景或静态背景图。

### 字幕层
- 文件：`web/src/renderer/src/components/canvas/subtitle.tsx`
- 从 `SubtitleContext` 获取字幕文本。
- Markdown 图片处理：
  - 识别 `![alt](url)`
  - 从字幕中移除 markdown 文本
  - 在画布右侧渲染图片

### WebSocket 状态徽标
- 文件：`web/src/renderer/src/components/canvas/ws-status.tsx`
- 显示连接状态，支持点击重连。

### 侧边栏
- 文件：`web/src/renderer/src/components/sidebar/sidebar.tsx`
- 关键子面板：
  - `chat-history-panel.tsx`（对话面板）
  - `history-drawer.tsx`（历史列表）
  - `group-drawer.tsx`（群组）
  - `setting-ui.tsx`（设置）

### Footer
- 文件：`web/src/renderer/src/components/footer/footer.tsx`
- 输入、麦克风、摄像头/屏幕等控制。

### Electron 输入字幕（宠物模式）
- 文件：`web/src/renderer/src/components/electron/input-subtitle.tsx`
- 可拖拽输入组件与状态显示。

## 组件树（窗口模式）

```
App
└─ AppWithGlobalStyles
   └─ Providers
      └─ WebSocketHandler
         └─ AppContent
            ├─ Live2D（画布层）
            └─ Window UI
               ├─ TitleBar（仅 Electron）
               └─ Layout（Flex）
                  ├─ Sidebar
                  │  ├─ ChatHistoryPanel
                  │  ├─ HistoryDrawer
                  │  ├─ GroupDrawer
                  │  └─ SettingUI
                  └─ MainContent
                     ├─ Background
                     ├─ WebSocketStatus
                     ├─ Subtitle（文本 + 右侧图片）
                     └─ Footer
```

## 组件树（宠物模式）

```
App
└─ AppWithGlobalStyles
   └─ Providers
      └─ WebSocketHandler
         └─ AppContent
            ├─ Live2D（画布层）
            └─ InputSubtitle（仅 Electron）
```

## 消息与状态流

### WebSocket 处理
- 文件：`web/src/renderer/src/services/websocket-handler.tsx`
  - 将服务端消息分发到各 Context（字幕、历史、配置、群组等）
  - 更新字幕 `setSubtitleText`
  - XiaoZhi 模式下 `full-text` 会更新最新 AI 消息

### 聊天历史
- Context：`web/src/renderer/src/context/chat-history-context.tsx`
  - `appendHumanMessage` / `appendAIMessage`
  - `upsertAIMessage`（full-text 覆盖式更新）
  - `appendOrUpdateToolCallMessage`

### 音频与字幕
- 文件：`web/src/renderer/src/hooks/utils/use-audio-task.ts`
  - 播放音频（wav/pcm）
  - 从 `display_text` 更新字幕与历史
  - 播放完成后通知后端

## 样式与布局

- 布局样式：`web/src/renderer/src/layout.tsx`
- 画布样式：`web/src/renderer/src/components/canvas/canvas-styles.tsx`
- 侧边栏样式：`web/src/renderer/src/components/sidebar/sidebar-styles.tsx`
- Footer 样式：`web/src/renderer/src/components/footer/footer-styles.tsx`

## 备注

- `showSubtitle` 为 false 时字幕不显示。
- Markdown 图片支持：
  - 聊天历史面板：`chat-history-panel.tsx`
  - 画布字幕层：`subtitle.tsx`

## WebSocket 消息类型（UI 侧）

服务端 → 客户端（`websocket-handler.tsx` 处理）：
- `control`：`{ text }` 控制信号（`conversation-chain-start`、`conversation-chain-end`、`start-mic`、`stop-mic`）
- `set-model-and-conf`：`{ model_info, conf_name, conf_uid, client_uid }`
- `full-text`：`{ text }` 字幕 + XiaoZhi 全文同步
- `config-files`：`{ configs }`
- `config-switched`：`{}` 触发重载 + 历史重置
- `background-files`：`{ files }`
- `audio`：`{ audio?, audio_pcm?, audio_format?, audio_sample_rate?, audio_channels?, volumes?, slice_length?, display_text?, actions?, forwarded? }`
- `history-data`：`{ messages }`
- `new-history-created`：`{ history_uid }`
- `history-deleted`：`{ history_uid, success }`
- `history-list`：`{ histories }`
- `user-input-transcription`：`{ text }`
- `error`：`{ message }`
- `group-update`：`{ members, is_owner }`
- `group-operation-result`：`{ message, success }`
- `backend-synth-complete`：`{}`
- `conversation-chain-end`：`{}`
- `force-new-message`：`{}`
- `interrupt-signal`：`{ text }`
- `tool_call_status`：`{ tool_id, tool_name, name?, status, content?, timestamp?, browser_view? }`
- `mcp-capture-request`：`{ request_id, source, question?, display? }`

客户端 → 服务端（`wsService.sendMessage` 发送，`src/open_llm_vtuber/websocket_handler.py` 处理）：
- `fetch-history-list`：`{}`
- `fetch-and-set-history`：`{ history_uid }`
- `create-new-history`：`{}`
- `delete-history`：`{ history_uid }`
- `text-input`：`{ text }`
- `mic-audio-data`：`{ audio: float[] }`
- `mic-audio-end`：`{}`
- `raw-audio-data`：`{ audio: number[] }`
- `interrupt-signal`：`{ text? }`
- `audio-play-start`：`{ display_text, forwarded }`（群组同步）
- `fetch-configs`：`{}`
- `switch-config`：`{ file }`
- `fetch-backgrounds`：`{}`
- `request-init-config`：`{}`
- `heartbeat`：`{}`
- `mcp-capture-response`：`{ request_id, success, image?, mime_type?, message? }`
- `add-client-to-group` / `remove-client-from-group`：`{ action?, uids? }`
- `request-group-info`：`{}`
- `ai-speak-signal`：`{}`（XiaoZhi 模式下会拒绝）
