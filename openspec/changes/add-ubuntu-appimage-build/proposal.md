# Change: Add Ubuntu AppImage desktop builds (x64/arm64)

## Why
We need official Ubuntu desktop artifacts for both x64 and arm64 to simplify distribution and testing.

## What Changes
- Add Electron build configuration to output AppImage for Ubuntu x64 and arm64.
- Add build scripts and documentation for Linux AppImage generation.
- Ensure artifacts are produced for both architectures.

## Impact
- Affected specs: desktop-build
- Affected code: `web/electron-builder.yml`, build scripts and docs
