# Go 后端替代 Python 的整体技术方案与实现注意事项

## 目标
将当前 Python 后端（FastAPI + 业务逻辑）替换为 Go 实现，保持现有前端与协议行为一致，最小化功能与接口变更。

## 当前后端职责概览（现状）
- WebSocket 服务：`/client-ws`，处理前端消息类型与路由
- 静态资源托管：`/frontend`、`/live2d-models`、`/backgrounds` 等
- 会话/群组管理：用户连接、群组管理、广播
- 对话编排：ASR -> LLM -> TTS -> 前端播放控制
- 工具调用与浏览器工具：MCP 相关事件/状态
- Web 工具页面：`/web-tool` 静态站点

核心实现入口：`src/open_llm_vtuber/server.py`、`src/open_llm_vtuber/websocket_handler.py`、`src/open_llm_vtuber/conversations/*`

## 迁移总体策略
**分层迁移**（建议）
1) 先保持协议/消息结构不变（前端零改动）
2) Go 实现 WebSocket 与静态资源服务
3) 逐步移植会话编排与 TTS/ASR/LLM 调度
4) 替换或桥接 Python 模块（兼容期可走旁路）

**方案 A：纯 Go 全量替换**
- 优点：性能、部署单一、可控
- 风险：功能迁移成本高、模型生态对接复杂

**方案 B：Go 作为网关/编排层**
- Go 管理连接、协议、缓存、队列
- 语音/LLM 仍由 Python 服务处理（HTTP/gRPC）
- 风险低、可渐进

> 若需快速落地，推荐方案 B，再逐步迁移。

## 架构设计（Go 方案）

### 1) 进程与模块划分
- `cmd/server`: 入口
- `internal/ws`: WebSocket 连接与消息路由
- `internal/http`: 静态文件与 REST
- `internal/conversation`: 会话编排
- `internal/tts`, `internal/asr`, `internal/llm`: 引擎接口与实现
- `internal/group`: 群组管理与广播
- `internal/config`: 配置读取与热更新
- `internal/types`: 协议与消息类型

### 2) 核心数据流
```
Frontend WS -> Go WS Router -> Conversation Orchestrator
  -> ASR -> LLM -> TTS -> Audio Payload -> WS to Frontend
```

### 3) 并发模型建议
- 每个连接一个 goroutine + 读写协程
- 会话编排基于 context + channel
- TTS/ASR/LLM 通过 worker pool 控制并发
- 广播使用非阻塞发送 + 超时回收

## 关键协议与消息类型（必须保持一致）

### Server -> Client
- `control`: `start-mic` / `stop-mic` / `conversation-chain-start` / `conversation-chain-end`
- `full-text`
- `audio`（包含 `actions`, `display_text`）
- `history-data`, `history-list`
- `config-files`, `config-switched`
- `background-files`
- `tool_call_status`
- `backend-synth-complete`
- `force-new-message`
- `interrupt-signal`
- `mcp-capture-request`

### Client -> Server
- `mic-audio-data` / `mic-audio-end`
- `text-input`
- `ai-speak-signal`
- `interrupt-signal`
- `audio-play-start`
- `fetch-configs`, `switch-config`
- `fetch-history-list`, `fetch-and-set-history`, `create-new-history`, `delete-history`
- `fetch-backgrounds`
- `add-client-to-group`, `remove-client-from-group`, `request-group-info`
- `mcp-capture-response`

> 消息格式详见：`doc/web-ui.md`

## 细节注意事项

### 1) WebSocket 保持语义一致
- 前端基于消息 `type` 分发逻辑，字段名必须一致（snake_case）
- `audio` 载荷字段：`audio`, `audio_pcm`, `audio_format`, `audio_sample_rate`, `audio_channels`, `volumes`, `slice_length`, `display_text`, `actions`, `forwarded`
- `display_text` 结构 `{ text, name, avatar }`

### 2) 音频切片与音量
- 需实现 `prepare_audio_payload` 的等价逻辑：
  - audio 编码为 wav/base64
  - 生成 volume 数组用于 lip sync
  - `slice_length` 默认为 20ms

### 3) 对话编排与状态一致
- 前端依赖 `conversation-chain-start/end` 控制 UI 状态
- `backend-synth-complete` 需在 TTS 全部推送完成后发送
- `force-new-message` 用于拆分消息块

### 4) Live2D 表情/动作
- `actions.expressions` 与 `actions.pictures/sounds` 需透传
- 若新增动作控制字段，Go 侧需保持 JSON 字段一致

### 5) 会话与历史
- 历史管理可继续沿用当前文件式或 DB 存储
- 需保证 `history_uid` 生命周期与前端一致

### 6) 配置与资源
- `conf.yaml` 与 `config_templates/` 依旧作为配置源
- 静态目录映射需与 Python 服务一致：
  - `/live2d-models` -> `live2d-models/`
  - `/backgrounds` -> `backgrounds/`
  - `/frontend` -> `frontend/`
  - `/web-tool` -> `web_tool/`

### 7) 与 Python 组件桥接（方案 B）
- 建议 gRPC 或 HTTP：
  - `/asr`：传音频流，返回文本
  - `/llm`：传对话上下文，流式返回
  - `/tts`：传文本，返回音频流/文件
- Go 统一处理 WebSocket + 状态，Python 作为纯模型服务

### 8) 多端兼容
- Electron 与 Web 版本共享协议
- 需保持 CORS 与 HTTPS 约束

## 推荐技术栈（Go）
- WebSocket: `github.com/gorilla/websocket` 或 `nhooyr.io/websocket`
- HTTP: `net/http` + `chi`/`gin`
- 配置: `viper`
- 日志: `zap`/`zerolog`
- 音频处理: `github.com/go-audio/wav`, `github.com/go-audio/audio`

## 迁移实施步骤（建议）
1) **实现 Go WebSocket 路由与协议透传**（不做业务）
2) **迁移静态资源托管与配置读取**
3) **实现简化会话编排**：先支持 `text-input -> tts -> audio`
4) **加入 ASR 与 LLM**（或桥接 Python）
5) **补齐群组管理与工具调用**
6) **回归验证与性能压测**

## 风险与验证点
- 音频切片 RMS 算法偏差导致 lip sync 不自然
- 对话状态同步不一致导致 UI 卡死
- 消息字段遗漏导致前端报错或静默失败

## 验收清单
- 能连通前端（Web/Electron）
- 文本输入能语音播报
- Live2D 表情能随语音变化
- 历史记录与配置切换正常
- 中断、重连、群组广播正常

---

## 追加：消息协议字段清单（精简版）

### Server -> Client
**control**
```json
{ "type": "control", "text": "start-mic|stop-mic|conversation-chain-start|conversation-chain-end" }
```

**full-text**
```json
{ "type": "full-text", "text": "string" }
```

**audio**
```json
{
  "type": "audio",
  "audio": "base64-wav-or-null",
  "audio_pcm": "base64-pcm16-or-null",
  "audio_format": "pcm16|wav|...",
  "audio_sample_rate": 16000,
  "audio_channels": 1,
  "volumes": [0.1, 0.2],
  "slice_length": 20,
  "display_text": { "text": "...", "name": "...", "avatar": "..." },
  "actions": { "expressions": [0], "pictures": [], "sounds": [] },
  "forwarded": false
}
```

**history-list / history-data**
```json
{ "type": "history-list", "histories": [ { "uid": "...", "latest_message": "...", "timestamp": "..." } ] }
{ "type": "history-data", "messages": [ { "id": "...", "role": "ai|human", "content": "...", "timestamp": "..." } ] }
```

**config-files / config-switched**
```json
{ "type": "config-files", "configs": [ { "name": "...", "uid": "..." } ] }
{ "type": "config-switched", "success": true }
```

**background-files**
```json
{ "type": "background-files", "files": [ { "name": "...", "url": "..." } ] }
```

**tool_call_status**
```json
{
  "type": "tool_call_status",
  "tool_id": "...",
  "tool_name": "...",
  "status": "running|completed|error",
  "content": "...",
  "timestamp": "..."
}
```

**misc**
```json
{ "type": "backend-synth-complete" }
{ "type": "force-new-message" }
{ "type": "interrupt-signal" }
{ "type": "mcp-capture-request", "request_id": "...", "source": "camera|screen" }
```

### Client -> Server
**mic audio**
```json
{ "type": "mic-audio-data", "audio": [0.1, -0.2, ...] }
{ "type": "mic-audio-end" }
```

**text input**
```json
{ "type": "text-input", "text": "..." }
```

**conversation control**
```json
{ "type": "ai-speak-signal" }
{ "type": "interrupt-signal" }
{ "type": "audio-play-start", "display_text": { "text": "...", "name": "...", "avatar": "..." } }
```

**config & history**
```json
{ "type": "fetch-configs" }
{ "type": "switch-config", "conf_uid": "..." }
{ "type": "fetch-history-list" }
{ "type": "fetch-and-set-history", "history_uid": "..." }
{ "type": "create-new-history" }
{ "type": "delete-history", "history_uid": "..." }
```

**group & background**
```json
{ "type": "add-client-to-group", "uids": ["..."] }
{ "type": "remove-client-from-group", "uids": ["..."] }
{ "type": "request-group-info" }
{ "type": "fetch-backgrounds" }
```

**mcp capture**
```json
{ "type": "mcp-capture-response", "request_id": "...", "success": true, "image": "...", "mime_type": "image/png" }
```

---

## 追加：Go 端目录结构模板
```
cmd/server/main.go
internal/http/router.go
internal/ws/hub.go
internal/ws/handler.go
internal/ws/types.go
internal/conversation/orchestrator.go
internal/conversation/state.go
internal/tts/tts.go
internal/asr/asr.go
internal/llm/llm.go
internal/group/group.go
internal/config/config.go
internal/storage/history.go
internal/media/audio.go
```

---

## 追加：关键实现细节清单

### WebSocket 读写与错误处理
- 读写分离协程，写通道加缓冲并限制大小，防止慢客户端拖死。\n
- 写超时与断线处理：超时直接关闭连接并清理状态。\n
- 解析错误需返回 `error` 消息给前端（格式一致）。\n

### 心跳与重连
- 建议实现 `heartbeat` 消息（客户端已有 handler），Go 侧可用于保活。\n
- 服务器定期发送 ping，客户端断线自动重连需兼容。\n

### 音频处理与切片
- PCM 音频需要统一 sample rate 与 channels。\n
- RMS 计算与 Python 保持一致（chunk size = slice_length）。\n

### 状态机与竞态
- 同一客户端同时触发 `interrupt` 与 `audio` 需要可重入处理。\n
- 对话链 `start/end` 必须严格配对。\n

### 资源与 CORS
- 静态资源路径与 Python 保持一致，避免前端路径改动。\n
- HTTPS + CORS 与当前行为一致（麦克风权限依赖）。\n

---

## 追加：迁移后的验证步骤（建议脚本）
1) 启动 Go 服务，打开 Web UI\n
2) 输入文本，确认 `audio` + `full-text` + `control` 顺序正确\n
3) 切换角色与背景文件\n
4) 打断与恢复\n
5) 群组邀请与广播\n

