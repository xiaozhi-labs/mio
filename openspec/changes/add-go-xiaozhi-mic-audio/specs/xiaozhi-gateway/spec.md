## ADDED Requirements
### Requirement: Microphone Audio Uplink
The Go gateway SHALL accept UI `mic-audio-data` samples and forward them to XiaoZhi.

#### Scenario: Mic audio forwarding
- **WHEN** the client sends `mic-audio-data`
- **THEN** the gateway converts float32 samples to PCM16 and sends audio frames to XiaoZhi

### Requirement: Listen State Management
The Go gateway SHALL start and stop XiaoZhi listening based on mic events.

#### Scenario: Mic session lifecycle
- **WHEN** the client sends the first `mic-audio-data`
- **THEN** the gateway sends `listen:start`
- **WHEN** the client sends `mic-audio-end`
- **THEN** the gateway sends `listen:stop` and emits `control:conversation-chain-start`
