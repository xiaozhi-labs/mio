## ADDED Requirements
### Requirement: Static Asset Hosting
The Go gateway SHALL serve frontend and media assets required by the UI.

#### Scenario: Frontend asset load
- **WHEN** the UI requests `/frontend` or `/live2d-models`
- **THEN** the gateway serves static files from the repository directories

### Requirement: Config and History Messages
The Go gateway SHALL implement UI WebSocket messages for configs and history.

#### Scenario: Fetch configs
- **WHEN** the client sends `fetch-configs`
- **THEN** the gateway responds with `config-files`

#### Scenario: History list
- **WHEN** the client sends `fetch-history-list`
- **THEN** the gateway responds with `history-list`

### Requirement: Group Messages
The Go gateway SHALL implement group membership messages for the UI.

#### Scenario: Group update
- **WHEN** the client sends `request-group-info`
- **THEN** the gateway responds with `group-update`

### Requirement: Opus Mic Uplink
The Go gateway SHALL encode mic audio with `github.com/godeps/opus` when XiaoZhi expects Opus.

#### Scenario: Opus uplink
- **WHEN** the client sends `mic-audio-data` and `xiaozhi_audio_format=opus`
- **THEN** the gateway encodes audio to Opus and sends it to XiaoZhi
