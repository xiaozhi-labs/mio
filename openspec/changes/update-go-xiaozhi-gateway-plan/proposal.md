# Change: Update Go gateway plan to align with XiaoZhi unified model service

## Why
Current migration plan assumes local ASR/LLM/TTS services. XiaoZhi already provides a unified model interface, so the gateway design, risks, and acceptance criteria must align to that reality.

## What Changes
- Reframe the Go gateway plan around XiaoZhi as the sole ASR/LLM/TTS provider
- Define protocol mapping, state handling, and reconnection expectations
- Add acceptance and observability requirements for XiaoZhi integration

## Impact
- Affected specs: new `xiaozhi-gateway` capability
- Affected docs: `doc/go-backend-migration.md`
- Affected code: none in this change (planning/spec only)
