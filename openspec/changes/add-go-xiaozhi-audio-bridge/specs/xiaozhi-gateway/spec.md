## ADDED Requirements
### Requirement: XiaoZhi Audio Bridging
The Go gateway SHALL decode XiaoZhi audio frames to PCM16 and emit UI `audio` messages with required fields.

#### Scenario: Audio frame handling
- **WHEN** XiaoZhi sends a binary audio frame
- **THEN** the gateway emits an `audio` message with `audio_pcm`, `audio_format=pcm16`, `audio_sample_rate`, `audio_channels`, `volumes`, and `slice_length`

### Requirement: Audio Completion Signal
The Go gateway SHALL emit `backend-synth-complete` after the XiaoZhi TTS stream finishes.

#### Scenario: TTS stop
- **WHEN** XiaoZhi emits a `tts` event with `state=stop`
- **THEN** the gateway sends `backend-synth-complete` to the client
