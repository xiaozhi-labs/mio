<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# Repository Guidelines

## Project Structure & Module Organization
- `src/open_llm_vtuber/` contains the Python backend (FastAPI server, ASR/TTS, gateways, and utilities).
- `web/` hosts the Electron + React/TypeScript frontend; `web/dist/` is the built output.
- `frontend/` receives synced web build artifacts for the server to serve.
- `assets/`, `avatars/`, `backgrounds/`, `live2d-models/`, `models/` hold runtime media and model data.
- `conf.yaml` is the primary runtime configuration; `config_templates/` contains starter configs.
- `scripts/` includes helper scripts (e.g., public start and cert generation).

## Build, Test, and Development Commands
- `uv run run_server.py` starts the backend server using the local `conf.yaml`.
- `scripts/start_public.sh` builds the web UI, syncs to `frontend/`, and launches the server (with HTTPS certs).
- `npm --prefix web install` installs Electron/React dependencies (run once per machine or when lockfile changes).
- `npm --prefix web run dev` launches the desktop Electron app in dev mode.
- `npm --prefix web run build` builds the desktop app binaries via `electron-vite`.
- `npm --prefix web run build:win|build:mac|build:linux` packages platform-specific desktop releases.
- `npm --prefix web run build:unpack` produces an unpacked desktop build for local testing.
- `npm --prefix web run dev:web` runs the web UI in Vite dev mode.
- `npm --prefix web run build:web` builds the web UI for serving via the backend.
- `npm --prefix web run lint` and `npm --prefix web run format` run frontend linting and formatting.

## Coding Style & Naming Conventions
- Python: follow PEP 8, 4-space indentation, `snake_case` functions/variables, `PascalCase` classes.
- Use `ruff` for linting (`pyproject.toml`), and keep imports organized.
- Frontend: TypeScript/React with `eslint` and `prettier`; keep component names `PascalCase` and hooks `useX`.

## Testing Guidelines
- No dedicated test suite is present in this repo. Validate changes by running the server and the web UI.
- If you add tests, prefer `pytest` conventions (`tests/`, `test_*.py`) and document how to run them.

## Commit & Pull Request Guidelines
- Commit history uses Conventional Commits (e.g., `feat:`, `fix:`, `refactor:`, `build:`). Follow that format.
- PRs should describe the change, mention config or model updates, and include screenshots/gifs for UI changes.
- Link related issues and note any required migration or setup steps.

## Security & Configuration Notes
- HTTPS is required for microphone access on non-localhost; see `certs/` and `scripts/gen_self_signed_cert.sh`.
- Avoid committing secrets or API tokens in `conf.yaml`; use local overrides when possible.
