# Live2D 指令动作控制技术方案

## 目标
在不破坏现有对话/语音流程的前提下，新增“通过指令控制 Live2D 动作”的能力，支持指定动作组与索引，并兼容当前基于情绪标签的表情控制与默认说话动作。

## 当前现状梳理
- 表情控制：后端从文本中解析情绪标签（如 `[joy]`），转换为 `actions.expressions` 透传到前端，前端在播放音频时设置表情。
  - 入口：`src/open_llm_vtuber/agent/transformers.py` -> `actions_extractor`
  - 数据结构：`src/open_llm_vtuber/agent/output_types.py` -> `Actions`
  - 前端消费：`web/src/renderer/src/hooks/utils/use-audio-task.ts`
- 动作控制：目前没有指令通道，仅在前端播放音频时固定触发 `Talk` 组随机动作。
  - 入口：`web/src/renderer/src/hooks/utils/use-audio-task.ts`
- 交互动作：点击/触控触发 tap 动作（非指令通道）。
  - 入口：`web/src/renderer/src/hooks/canvas/use-live2d-model.ts`

结论：当前不存在“指令 -> 动作”的链路，仅有“情绪标签 -> 表情”与“语音播放 -> Talk 动作”。

## 总体方案
新增“动作指令”通道，沿用现有 `actions` 透传链路，并提供可选的“无语音动作”通道。

方案分两层：
1) **随语音动作**（推荐优先）：通过 `actions` 附带动作信息，跟随每句语音输出执行。
2) **无语音动作**（可选）：新增 WebSocket 消息类型，直接触发动作，不依赖 TTS。

## 数据结构设计
在 `Actions` 新增动作字段：

```ts
// 前后端保持一致
interface MotionAction {
  group: string;
  index?: number;      // 缺省时使用随机动作
  priority?: number;   // 可选，默认 PriorityNormal
}

interface Actions {
  expressions?: string[] | number[];
  pictures?: string[];
  sounds?: string[];
  motion?: MotionAction;      // 单个动作
  motions?: MotionAction[];   // 批量动作（可选）
}
```

备注：优先支持 `motion`，`motions` 可用于多动作串行或扩展需求。

## 指令格式（文本标签模式）
在模型输出文本中解析动作标签，例如：
- `[motion:Talk]` -> 随机播放 `Talk` 组
- `[motion:Wave,1]` -> 播放 `Wave` 组第 1 条
- `[motion:Wave,1,3]` -> 播放 `Wave` 组第 1 条，优先级 3

解析规则：
- 允许空格，大小写不敏感；
- `group` 必填；`index`/`priority` 可选；
- 无效格式应安全跳过，不影响文本输出。

## 链路改动细化

### 1) 后端：Actions 扩展
- 文件：`src/open_llm_vtuber/agent/output_types.py`
- 改动：新增 `motion`/`motions` 字段；`to_dict()` 透传。

### 2) 后端：动作标签解析
- 文件：`src/open_llm_vtuber/agent/transformers.py`
- 改动点：`actions_extractor`
  - 解析 `SentenceWithTags.text` 中的 `[motion:...]` 标签；
  - 将动作写入 `actions.motion`；
  - 可选择是否在展示文本中移除标签（推荐移除，避免用户看到标签）。

### 3) 前端：Actions 类型扩展
- 文件：`web/src/renderer/src/services/websocket-service.tsx`
- 改动：`Actions` 新增 `motion`/`motions` 类型定义。

### 4) 前端：动作执行
- 文件：`web/src/renderer/src/hooks/utils/use-audio-task.ts`
- 改动：
  - 在播放音频前解析 `actions.motion`/`actions.motions`；
  - 如果存在显式动作，执行 `model.startMotion(group, index, priority)`；
  - 若 `index` 缺省，使用 `startRandomMotion(group, priority)`；
  - 若存在显式动作，默认跳过自动 `Talk` 动作（可配置）。

### 5) 可选：无语音动作通道
- 后端：新增 WS 消息 `type: "live2d-action"`
  - 触发位置：`src/open_llm_vtuber/websocket_handler.py` 或会话层
- 前端：`web/src/renderer/src/services/websocket-handler.tsx`
  - 处理 `live2d-action` 消息，直接调用 Live2D 动作

## 兼容性与回滚策略
- 未发出动作标签时，流程与当前一致。
- 动作字段为可选字段，不影响旧客户端与旧服务端。
- 可通过配置开关禁用“动作标签解析”，保证可回滚。

## 失败与异常处理
- `Live2D manager/model` 不存在：输出警告并跳过动作执行。
- 动作组不存在或索引越界：捕获异常，继续播放语音。
- 动作与 `Talk` 冲突：优先显式动作，`Talk` 可配置是否跳过。

## 测试与验收建议
- 基础：`[motion:Talk]` 能触发 Talk 组随机动作。
- 指定：`[motion:Wave,0]` 触发指定动作。
- 优先级：`[motion:Wave,0,3]` 使用高优先级，不被 Idle 打断。
- 回归：无动作标签时行为与现有一致。
- 异常：非法标签不会导致前端报错或卡住。

## 文档与示例
- 示例输出：
  - `今天心情很好。[motion:Wave,0]`
  - `打个招呼吧。[motion:Wave]`
- 推荐提供一个开发者测试入口（console 或隐藏按钮）用于触发动作。

## 可选进阶
- 支持多动作队列：`motions` 依序执行。
- 支持动作时长/冷却等节流控制。
- 支持 `expression` 与 `motion` 组合配置。

