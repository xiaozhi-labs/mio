"""Minimal MCP server for XiaoZhi device-side tools."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union

import aiohttp
from loguru import logger

ReturnValue = Union[bool, int, str]


class PropertyType(Enum):
    BOOLEAN = "boolean"
    INTEGER = "integer"
    STRING = "string"


@dataclass
class Property:
    name: str
    type: PropertyType
    default_value: Optional[Any] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None

    @property
    def has_default_value(self) -> bool:
        return self.default_value is not None

    @property
    def has_range(self) -> bool:
        return self.min_value is not None and self.max_value is not None

    def value(self, value: Any) -> Any:
        if self.type == PropertyType.INTEGER and self.has_range:
            if value < self.min_value:
                raise ValueError(
                    f"Value {value} is below minimum allowed: {self.min_value}"
                )
            if value > self.max_value:
                raise ValueError(
                    f"Value {value} exceeds maximum allowed: {self.max_value}"
                )
        return value

    def to_json(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"type": self.type.value}
        if self.has_default_value:
            result["default"] = self.default_value
        if self.type == PropertyType.INTEGER:
            if self.min_value is not None:
                result["minimum"] = self.min_value
            if self.max_value is not None:
                result["maximum"] = self.max_value
        return result


@dataclass
class PropertyList:
    properties: List[Property] = field(default_factory=list)

    def add_property(self, prop: Property) -> None:
        self.properties.append(prop)

    def __getitem__(self, name: str) -> Property:
        for prop in self.properties:
            if prop.name == name:
                return prop
        raise KeyError(f"Property not found: {name}")

    def get_required(self) -> List[str]:
        return [prop.name for prop in self.properties if not prop.has_default_value]

    def to_json(self) -> Dict[str, Any]:
        return {prop.name: prop.to_json() for prop in self.properties}

    def parse_arguments(self, arguments: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for prop in self.properties:
            if arguments and prop.name in arguments:
                value = arguments[prop.name]
                if prop.type == PropertyType.BOOLEAN and isinstance(value, bool):
                    result[prop.name] = value
                elif prop.type == PropertyType.INTEGER and isinstance(value, (int, float)):
                    result[prop.name] = prop.value(int(value))
                elif prop.type == PropertyType.STRING and isinstance(value, str):
                    result[prop.name] = value
                else:
                    raise ValueError(f"Invalid type for property {prop.name}")
            elif prop.has_default_value:
                result[prop.name] = prop.default_value
            else:
                raise ValueError(f"Missing required argument: {prop.name}")
        return result


@dataclass
class McpTool:
    name: str
    description: str
    properties: PropertyList
    callback: Callable[[Dict[str, Any]], Awaitable[str]]

    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.properties.to_json(),
                "required": self.properties.get_required(),
            },
        }

    async def call(self, arguments: Dict[str, Any]) -> str:
        try:
            parsed_args = self.properties.parse_arguments(arguments)
            result = await self.callback(parsed_args)
            if isinstance(result, bool):
                text = "true" if result else "false"
            elif isinstance(result, int):
                text = str(result)
            else:
                text = str(result)
            return json.dumps(
                {"content": [{"type": "text", "text": text}], "isError": False}
            )
        except Exception as exc:
            logger.error(f"Error calling tool {self.name}: {exc}", exc_info=True)
            return json.dumps(
                {"content": [{"type": "text", "text": str(exc)}], "isError": True}
            )


class XiaoZhiMcpServer:
    def __init__(
        self,
        send_callback: Callable[[Dict[str, Any]], Awaitable[None]],
        capture_callback: Callable[[str, str, Optional[str]], Awaitable[Dict[str, Any]]],
        device_id: str,
        client_id: str,
    ) -> None:
        self._send_callback = send_callback
        self._capture_callback = capture_callback
        self._device_id = device_id
        self._client_id = client_id
        self._vision_url: str = ""
        self._vision_token: str = ""
        self.tools: List[McpTool] = []
        self._init_tools()

    def _init_tools(self) -> None:
        vision_desc = (
            "【图像/识图/OCR/问答】当用户提到：拍照、识图、读取/提取文字、OCR、翻译图片文字、"
            "看一下这张图/截图、这是什么、数一数、识别二维码/条码、对比两张图、分析场景/报错截图、"
            "表格/票据信息抽取、图片问答 时调用本工具。"
            "功能：①拍照或接收已有图片/截图/URL；②物体/场景/标签识别；③OCR(多语)与翻译；④计数/位置；"
            "⑤二维码/条码读取；⑥关键信息抽取(表格/票据)；⑦两图对比；⑧就图回答问题。"
            "输入建议：{ question? }。"
        )
        self.add_tool(
            McpTool(
                name="take_photo",
                description=vision_desc,
                properties=PropertyList(
                    [Property("question", PropertyType.STRING, default_value="")]
                ),
                callback=self._tool_take_photo,
            )
        )

        screenshot_desc = (
            "【桌面截图/屏幕分析】当用户提到：截屏、截图、看看桌面、分析屏幕、桌面上有什么、"
            "屏幕截图、查看当前界面、分析当前页面、读取屏幕内容、屏幕OCR 时调用本工具。"
            "参数说明：{ question: '关于屏幕的问题', display: '显示器选择(可选)' }。"
        )
        self.add_tool(
            McpTool(
                name="take_screenshot",
                description=screenshot_desc,
                properties=PropertyList(
                    [
                        Property("question", PropertyType.STRING, default_value=""),
                        Property("display", PropertyType.STRING, default_value=""),
                    ]
                ),
                callback=self._tool_take_screenshot,
            )
        )

    def add_tool(self, tool: McpTool) -> None:
        if any(existing.name == tool.name for existing in self.tools):
            logger.warning(f"Tool {tool.name} already added")
            return
        self.tools.append(tool)

    async def parse_message(self, message: Union[str, Dict[str, Any]]) -> None:
        try:
            data = json.loads(message) if isinstance(message, str) else message
        except json.JSONDecodeError:
            logger.warning("MCP message is not valid JSON")
            return

        if data.get("jsonrpc") != "2.0":
            logger.error(f"Invalid JSONRPC version: {data.get('jsonrpc')}")
            return

        method = data.get("method")
        if not method:
            logger.error("Missing method")
            return

        if method.startswith("notifications"):
            logger.debug(f"Ignoring notification: {method}")
            return

        params = data.get("params", {})
        request_id = data.get("id")
        if request_id is None:
            logger.error(f"Invalid id for method: {method}")
            return

        if method == "initialize":
            await self._handle_initialize(request_id, params)
        elif method == "tools/list":
            await self._handle_tools_list(request_id, params)
        elif method == "tools/call":
            await self._handle_tool_call(request_id, params)
        else:
            await self._reply_error(request_id, f"Method not implemented: {method}")

    async def _handle_initialize(self, request_id: int, params: Dict[str, Any]) -> None:
        capabilities = params.get("capabilities", {})
        vision = capabilities.get("vision", {}) if isinstance(capabilities, dict) else {}
        if isinstance(vision, dict):
            self._vision_url = vision.get("url", "") or ""
            self._vision_token = vision.get("token", "") or ""
            if self._vision_url:
                logger.info(f"Vision service configured: {self._vision_url}")

        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "open-llm-vtuber",
                "version": "1.0",
            },
        }
        await self._reply_result(request_id, result)

    async def _handle_tools_list(self, request_id: int, params: Dict[str, Any]) -> None:
        cursor = params.get("cursor", "")
        max_payload_size = 8000

        tools_json: List[Dict[str, Any]] = []
        total_size = 0
        found_cursor = not cursor
        next_cursor = ""

        for tool in self.tools:
            if not found_cursor:
                if tool.name == cursor:
                    found_cursor = True
                else:
                    continue

            tool_json = tool.to_json()
            tool_size = len(json.dumps(tool_json, ensure_ascii=False))
            if total_size + tool_size + 100 > max_payload_size:
                next_cursor = tool.name
                break

            tools_json.append(tool_json)
            total_size += tool_size

        result: Dict[str, Any] = {"tools": tools_json}
        if next_cursor:
            result["nextCursor"] = next_cursor

        await self._reply_result(request_id, result)

    async def _handle_tool_call(self, request_id: int, params: Dict[str, Any]) -> None:
        tool_name = params.get("name")
        if not tool_name:
            await self._reply_error(request_id, "Missing tool name")
            return

        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            await self._reply_error(request_id, f"Unknown tool: {tool_name}")
            return

        arguments = params.get("arguments", {})
        try:
            result = await tool.call(arguments)
            await self._reply_result(request_id, json.loads(result))
        except Exception as exc:
            logger.error(f"Tool {tool_name} failed: {exc}", exc_info=True)
            await self._reply_error(request_id, str(exc))

    async def _tool_take_photo(self, arguments: Dict[str, Any]) -> str:
        question = arguments.get("question", "")
        capture = await self._capture_callback("camera", question, None)
        return await self._analyze_capture(capture, question)

    async def _tool_take_screenshot(self, arguments: Dict[str, Any]) -> str:
        question = arguments.get("question", "")
        display = arguments.get("display") or None
        capture = await self._capture_callback("screen", question, display)
        return await self._analyze_capture(capture, question)

    async def _analyze_capture(self, capture: Dict[str, Any], question: str) -> str:
        if not capture.get("success"):
            return json.dumps(
                {
                    "content": [
                        {"type": "text", "text": capture.get("message", "capture failed")}
                    ],
                    "isError": True,
                }
            )

        if not self._vision_url:
            return json.dumps(
                {
                    "content": [
                        {"type": "text", "text": "Vision service URL is not configured"}
                    ],
                    "isError": True,
                }
            )

        image_bytes = capture.get("image_bytes")
        mime_type = capture.get("mime_type") or "image/jpeg"
        if not image_bytes:
            return json.dumps(
                {
                    "content": [
                        {"type": "text", "text": "No image data received"}
                    ],
                    "isError": True,
                }
            )

        headers = {
            "Device-Id": self._device_id,
            "Client-Id": self._client_id,
        }
        if self._vision_token:
            headers["Authorization"] = f"Bearer {self._vision_token}"

        try:
            form = aiohttp.FormData()
            form.add_field("question", question or "")
            form.add_field("file", image_bytes, filename="capture.jpg", content_type=mime_type)
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self._vision_url, data=form, headers=headers) as resp:
                    text = await resp.text()
                    if resp.status != 200:
                        return json.dumps(
                            {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"Vision request failed: {resp.status} {text}",
                                    }
                                ],
                                "isError": True,
                            }
                        )
                    return text
        except Exception as exc:
            return json.dumps(
                {
                    "content": [{"type": "text", "text": f"Vision error: {exc}"}],
                    "isError": True,
                }
            )

    async def _reply_result(self, request_id: int, result: Any) -> None:
        payload = {"jsonrpc": "2.0", "id": request_id, "result": result}
        await self._send_callback(payload)

    async def _reply_error(self, request_id: int, message: str) -> None:
        payload = {"jsonrpc": "2.0", "id": request_id, "error": {"message": message}}
        await self._send_callback(payload)
