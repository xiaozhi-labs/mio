# Open LLM Vtuber

An Electron application with React and TypeScript

## Recommended IDE Setup

- [VSCode](https://code.visualstudio.com/) + [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) + [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)

## Project Setup

### Install

```bash
$ npm install
```

### Development

```bash
$ npm run dev
```

### Build

```bash
# For windows
$ npm run build:win

# For macOS
$ npm run build:mac

# For Linux
$ npm run build:linux

# Or use the helper script from repo root
$ ./scripts/build_desktop.sh linux

# For Ubuntu AppImage (x64)
$ npm run build:linux:appimage:x64

# For Ubuntu AppImage (arm64)
$ npm run build:linux:appimage:arm64
```

Notes:
- AppImage artifacts are written to `web/release/<version>/`.
- AppImage filenames include the CPU arch (e.g. `open-llm-vtuber-<version>-arm64.AppImage`).
- To run AppImage on Ubuntu, ensure `libfuse2` is installed.

Smoke test checklist (Ubuntu AppImage):
- Launch the AppImage and confirm the window opens.
- Switch between window mode and pet mode.
- Verify WebSocket connects and audio playback works.
