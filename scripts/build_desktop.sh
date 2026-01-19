#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat << 'USAGE'
Usage: scripts/build_desktop.sh <target>

Targets:
  win                   Build Windows desktop app
  mac                   Build macOS desktop app
  linux                 Build Linux desktop app (AppImage/snap/deb)
  linux-appimage        Build Linux AppImage (default arch for host)
  linux-appimage-x64    Build Linux AppImage for x64
  linux-appimage-arm64  Build Linux AppImage for arm64
  win-pet               Build Windows desktop app (default pet mode)
  mac-pet               Build macOS desktop app (default pet mode)
  linux-pet             Build Linux desktop app (default pet mode)
  linux-appimage-pet    Build Linux AppImage (default pet mode)
  linux-appimage-x64-pet    Build Linux AppImage for x64 (default pet mode)
  linux-appimage-arm64-pet  Build Linux AppImage for arm64 (default pet mode)

Examples:
  scripts/build_desktop.sh linux
  scripts/build_desktop.sh linux-appimage-x64
USAGE
}

if [[ ${1:-} == "" || ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
  exit 0
fi

run_build() {
  local target="$1"
  local mode="${2:-}"
  if [[ "$mode" == "pet" ]]; then
    VITE_DEFAULT_MODE=pet VITE_DEFAULT_MIC_ON=1 VITE_DEFAULT_AUTO_START_MIC_ON_CONV_END=1 \
      npm --prefix web run "$target"
  else
    npm --prefix web run "$target"
  fi
}

case "$1" in
  win)
    run_build build:win
    ;;
  mac)
    run_build build:mac
    ;;
  linux)
    run_build build:linux
    ;;
  linux-appimage)
    run_build build:linux:appimage
    ;;
  linux-appimage-x64)
    run_build build:linux:appimage:x64
    ;;
  linux-appimage-arm64)
    run_build build:linux:appimage:arm64
    ;;
  win-pet)
    run_build build:win pet
    ;;
  mac-pet)
    run_build build:mac pet
    ;;
  linux-pet)
    run_build build:linux pet
    ;;
  linux-appimage-pet)
    run_build build:linux:appimage pet
    ;;
  linux-appimage-x64-pet)
    run_build build:linux:appimage:x64 pet
    ;;
  linux-appimage-arm64-pet)
    run_build build:linux:appimage:arm64 pet
    ;;
  *)
    echo "Unknown target: $1" >&2
    usage
    exit 1
    ;;
 esac
