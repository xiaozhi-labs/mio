#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/." && pwd)"
CONF_FILE="${CONF_FILE:-${ROOT_DIR}/conf.yaml}"
CERT_DIR="${ROOT_DIR}/certs"
CERT_KEY="${CERT_DIR}/server.key"
CERT_CRT="${CERT_DIR}/server.crt"

unset ALL_PROXY all_proxy HTTP_PROXY http_proxy HTTPS_PROXY https_proxy

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found; install python3 to parse conf.yaml." >&2
  exit 1
fi

if [[ ! -f "${CERT_KEY}" || ! -f "${CERT_CRT}" ]]; then
  echo "TLS certs not found, generating self-signed certificate..."
  if ! command -v openssl >/dev/null 2>&1; then
    echo "openssl not found; install openssl or run scripts/gen_self_signed_cert.sh manually." >&2
    exit 1
  fi
  mkdir -p "${CERT_DIR}"
  openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
    -keyout "${CERT_KEY}" \
    -out "${CERT_CRT}" \
    -subj "/CN=localhost"
fi

read -r HOST PORT < <(
  python3 - <<'PY' "${CONF_FILE}"
import sys
try:
    import yaml
except Exception:
    print("", "", file=sys.stderr)
    raise SystemExit("PyYAML is required to parse conf.yaml.")

with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = yaml.safe_load(f) or {}

system = data.get("system_config", {}) or {}
print(system.get("host", ""), system.get("port", ""))
PY
)

HOST="${HOST:-0.0.0.0}"
if [[ -z "${PORT}" ]]; then
  echo "Unable to determine port. Fix conf.yaml." >&2
  exit 1
fi

if [[ "${HOST}" != "0.0.0.0" && "${HOST}" != "::" ]]; then
  echo "Warning: conf.yaml host is '${HOST}'. For public access, set it to 0.0.0.0 or ::." >&2
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found; install Node.js to build the web frontend." >&2
  exit 1
fi

echo "Building web frontend..."
(
  cd "${ROOT_DIR}/web"
  npm run build:web
)

echo "Syncing frontend build to ${ROOT_DIR}/frontend"
rm -rf "${ROOT_DIR}/frontend"/*
cp -a "${ROOT_DIR}/web/dist/web/." "${ROOT_DIR}/frontend/"

find_pids() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -tiTCP:"${port}" -sTCP:LISTEN 2>/dev/null || true
    return 0
  fi

  if command -v ss >/dev/null 2>&1; then
    ss -ltnp "sport = :${port}" 2>/dev/null | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' | sort -u
    return 0
  fi

  if command -v fuser >/dev/null 2>&1; then
    fuser -n tcp "${port}" 2>/dev/null || true
    return 0
  fi

  echo ""
}

PIDS="$(find_pids "${PORT}")"
if [[ -n "${PIDS}" ]]; then
  echo "Port ${PORT} is in use; stopping process(es): ${PIDS}"
  kill ${PIDS} || true
  sleep 1
  if PIDS_REMAINING="$(find_pids "${PORT}")"; [[ -n "${PIDS_REMAINING}" ]]; then
    echo "Force-killing remaining process(es): ${PIDS_REMAINING}"
    kill -9 ${PIDS_REMAINING}
  fi
fi

echo "Starting server on ${HOST}:${PORT} using ${CONF_FILE}"
cd "${ROOT_DIR}"
uv run run_server.py
