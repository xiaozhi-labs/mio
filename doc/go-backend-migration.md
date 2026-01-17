# Go 后端替代 Python 的整体技术方案与实现注意事项（对接 XiaoZhi 统一模型服务）

## 目标
将当前 Python 后端（FastAPI + 业务逻辑）替换为 Go 实现，保持现有前端与协议行为一致，最小化功能与接口变更。ASR/LLM/TTS 由 XiaoZhi 统一服务提供，不再自建模型服务。

## 当前后端职责概览（现状）
- WebSocket 服务：`/client-ws`，处理前端消息类型与路由
- 静态资源托管：`/frontend`、`/live2d-models`、`/backgrounds` 等
- 会话/群组管理：用户连接、群组管理、广播
- 对话编排：XiaoZhi -> 前端播放控制（ASR/LLM/TTS 由 XiaoZhi 提供）
- 工具调用与浏览器工具：MCP 相关事件/状态
- Web 工具页面：`/web-tool` 静态站点

核心实现入口：`src/open_llm_vtuber/server.py`、`src/open_llm_vtuber/websocket_handler.py`、`src/open_llm_vtuber/conversations/*`
XiaoZhi 对接参考：`src/open_llm_vtuber/xiaozhi_gateway.py`、`src/open_llm_vtuber/websocket_handler.py`、`src/open_llm_vtuber/xiaozhi_mcp_server.py`

## 迁移总体策略
**分层迁移**（建议）
1) 先保持协议/消息结构不变（前端零改动）
2) Go 实现 WebSocket 与静态资源服务
3) 迁移会话编排、历史/配置/群组管理
4) 将 ASR/LLM/TTS 调用替换为 XiaoZhi 统一服务（不再自建模型服务）

**方案 A：纯 Go 全量替换 + XiaoZhi 模型服务**
- Go 负责协议网关、会话编排、资源托管与业务逻辑
- ASR/LLM/TTS 通过 XiaoZhi 统一 WebSocket 接口
- 风险：需要完整迁移后端逻辑与状态管理，但模型服务风险已降低

**方案 B：Go 作为网关/编排层 + 保留 Python 业务组件（非模型）**
- Go 管理连接、协议、缓存、队列
- Python 仅保留历史/配置/工具等业务组件，模型调用完全走 XiaoZhi
- 风险低、可渐进，适合作为过渡

> 若需快速落地，推荐方案 B；确认业务逻辑稳定后逐步收敛到方案 A。

## 架构设计（Go 方案）

### 1) 进程与模块划分
- `mio-server/cmd/server`: 入口
- `mio-server/internal/ws`: WebSocket 连接与消息路由
- `mio-server/internal/http`: 静态文件与 REST
- `mio-server/internal/conversation`: 会话编排
- `mio-server/internal/xiaozhi`: XiaoZhi 客户端与协议适配
- `mio-server/internal/group`: 群组管理与广播
- `mio-server/internal/config`: 配置读取与热更新
- `mio-server/internal/types`: 协议与消息类型

### 2) 核心数据流
```
Frontend WS -> Go WS Router -> Conversation Orchestrator
  -> XiaoZhi Gateway -> Audio/Full-text/Control -> WS to Frontend
```

### 3) 并发模型建议
- 每个连接一个 goroutine + 读写协程
- 会话编排基于 context + channel
- XiaoZhi 流式处理通过 worker pool 控制并发
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
  - XiaoZhi 输出音频帧需统一到本地协议格式（采样率/声道/封装）

### 3) 对话编排与状态一致
- 前端依赖 `conversation-chain-start/end` 控制 UI 状态
- `backend-synth-complete` 需在 TTS 全部推送完成后发送
- `force-new-message` 用于拆分消息块
 - XiaoZhi 流式文本需驱动 `full-text` 更新（XiaoZhi 模式下前端使用 upsert）

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

### 7) XiaoZhi 接口契约与错误处理
- 连接参数来自 `conf.yaml`：`xiaozhi_backend_url`、`xiaozhi_protocol_version`、`xiaozhi_audio_format`、`xiaozhi_sample_rate`、`xiaozhi_channels`、`xiaozhi_frame_duration`
- 鉴权与标识头：`Device-Id`、`Client-Id`、`Authorization`
- 需明确超时、重试、断线重连策略，避免重复播放或状态错乱
- 错误码/错误消息需映射为前端可识别的 `error` 消息

### 8) 与 Python 组件桥接（方案 B）
Python 不再承载模型服务，仅保留业务组件时的桥接接口需明确：
- 历史/配置/工具调用 API 的路径、请求/响应、错误码
- 统一鉴权（例如共享 token 或内网访问控制）

### 9) 多端兼容
- Electron 与 Web 版本共享协议
- 需保持 CORS 与 HTTPS 约束

### 10) 协议映射与消息序列（XiaoZhi -> UI）
- 映射目标以 `doc/web-ui.md` 为准，保持 `type` 与字段名一致
- 关键序列建议基准化（示例）：
  - `text-input` -> `control:conversation-chain-start` -> `full-text`(流式更新) -> `audio`(分片) -> `backend-synth-complete` -> `control:conversation-chain-end`
- XiaoZhi 音频分片需补齐 `volumes` 与 `slice_length`，保证 lip sync 与播放节奏一致
- XiaoZhi 若返回独立的“结束”事件，需映射为 `backend-synth-complete`

### 11) UI 协议消息清单（前端实际使用）
> 参考 `doc/web-ui.md`，需保持兼容
- Server -> Client：`control`、`full-text`、`audio`、`history-data`、`history-list`、`config-files`、`config-switched`、`background-files`、`tool_call_status`、`backend-synth-complete`、`force-new-message`、`interrupt-signal`、`mcp-capture-request` 等
- Client -> Server：`text-input`、`mic-audio-data`、`mic-audio-end`、`interrupt-signal`、`fetch-configs`、`switch-config`、`fetch-history-list`、`fetch-and-set-history`、`create-new-history`、`delete-history`、`fetch-backgrounds`、`add-client-to-group`、`remove-client-from-group`、`request-group-info`、`mcp-capture-response` 等

### 12) XiaoZhi 事件到 UI 消息映射（当前 Python 对接参考）
- `stt` -> `user-input-transcription`
- `llm` / `text` -> `full-text`（流式累计）
- `tts: start` -> 启动音频流状态
- `tts: sentence_start` -> `full-text` 追加
- `tts: stop` + 二进制音频帧 -> `audio` + `backend-synth-complete` + `force-new-message`
- `goodbye` / 断线 -> `error` + `control:conversation-chain-end`
- XiaoZhi `mcp` -> `tool_call_status` / `mcp-capture-request`（视 MCP 事件）
- Client `interrupt-signal` -> XiaoZhi `abort`（并终止 UI 会话）
- Client `text-input` -> XiaoZhi `listen:detect`（文本模式）
- Client `mic-audio-data`/`mic-audio-end` -> XiaoZhi `listen:start/stop` + 音频帧

### 13) 状态机与并发控制
- 每个客户端维护单独会话状态机，防止 interrupt 与 audio 并发造成 UI 卡死
- 强制 `conversation-chain-start/end` 成对出现，异常中断也需发送 `conversation-chain-end`
- 连接断开时清理网关状态与待发送队列，避免重连后串话

### 14) 可观测性与诊断
- 建议日志字段：`client_uid`、`history_uid`、`request_id`、`xiaozhi_session_id`
- 关键指标：WS 连接数、XiaoZhi RTT、音频队列长度、重连次数、错误码分布

### 15) 安全与鉴权
- XiaoZhi 鉴权信息来自 `conf.yaml`，避免前端直连暴露 token
- Go 网关与 XiaoZhi 通信需限制外部网络访问范围

## 推荐技术栈（Go）
- WebSocket: `github.com/gorilla/websocket`
- HTTP: `gin`
- 配置: `viper`
- 日志: `zap`/`zerolog`
- 音频处理: `github.com/go-audio/wav`, `github.com/go-audio/audio`
- XiaoZhi 客户端：建议封装为独立包，支持自动重连与心跳

## 迁移实施步骤（建议）
1) **实现 Go WebSocket 路由与协议透传**（不做业务）
2) **迁移静态资源托管与配置读取**
3) **实现 XiaoZhi 网关**：连接管理、鉴权、音频与文本流对接
4) **实现会话编排**：`text-input -> XiaoZhi -> audio/full-text`
5) **补齐群组管理、历史/配置、工具调用**
6) **回归验证与性能压测**

## 风险与验证点
- 音频切片 RMS 算法偏差导致 lip sync 不自然
- 对话状态同步不一致导致 UI 卡死
- 消息字段遗漏导致前端报错或静默失败
- XiaoZhi 断线/重连导致消息乱序或状态不一致

## 验收清单
- 能连通前端（Web/Electron）
- 文本输入能语音播报
- Live2D 表情能随语音变化
- 历史记录与配置切换正常
- 中断、重连、群组广播正常
- XiaoZhi 断线重连后状态恢复且消息顺序正确

## 验收与回归建议（最小集合）
1) 启动 Go 网关，Web UI 连通
2) `text-input` 发起对话，确认 `control/full-text/audio/backend-synth-complete` 顺序正确
3) 中断并立即重启对话，确认状态机可重入
4) 切换配置与历史记录，确认 UI 同步更新
5) 触发 MCP 工具调用与回传，确认状态与显示一致

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
mio-server/cmd/main.go
mio-server/internal/http/router.go
mio-server/internal/ws/hub.go
mio-server/internal/ws/handler.go
mio-server/internal/ws/types.go
mio-server/internal/conversation/orchestrator.go
mio-server/internal/conversation/state.go
mio-server/internal/xiaozhi/client.go
mio-server/internal/xiaozhi/types.go
mio-server/internal/group/group.go
mio-server/internal/config/config.go
mio-server/internal/storage/history.go
mio-server/internal/media/audio.go
mio-server/internal/observability/metrics.go
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
