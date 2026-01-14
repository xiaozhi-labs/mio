# Mio MCP Capture Tools

This document describes the MCP capture tools exposed by the `mio` XiaoZhi gateway.

## Supported Tools

- `take_photo`: Capture a frame from the active camera stream.
- `take_screenshot`: Capture a frame from the active screen-share stream.

## How It Works

- The backend sends MCP JSON-RPC messages over the XiaoZhi WebSocket.
- The gateway forwards `take_photo`/`take_screenshot` to the web client as
  `mcp-capture-request`.
- The web client captures a frame from the corresponding media stream and replies
  with `mcp-capture-response`.
- The gateway submits the image to the vision endpoint from MCP `initialize`
  capabilities and returns the text result.

## Notes

- The web client must have an active camera or screen-share stream, or the capture
  will fail.
- Vision analysis requires the backend to provide `capabilities.vision.url` during
  MCP `initialize`.
