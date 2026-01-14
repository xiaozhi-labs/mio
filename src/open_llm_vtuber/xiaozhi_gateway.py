import asyncio
import base64
import io
import json
import uuid
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

import aiohttp
import numpy as np
import soundfile as sf
from loguru import logger
from opuslib import APPLICATION_AUDIO, Decoder, Encoder
from opuslib.api import decoder as opus_decoder_api

from .agent.output_types import DisplayText
from .message_handler import message_handler
from .xiaozhi_mcp_server import XiaoZhiMcpServer

TTS_STREAM_CHUNK_MS = 300
TTS_FADE_MS = 10


@dataclass
class XiaozhiAudioParams:
    format: str
    sample_rate: int
    channels: int
    frame_duration: int


class XiaozhiGateway:
    def __init__(
        self,
        backend_url: str,
        protocol_version: int,
        audio_params: XiaozhiAudioParams,
        send_text: Callable[[str], Awaitable[None]],
        client_uid: str,
        device_id: Optional[str],
        client_id: Optional[str],
        access_token: Optional[str],
        display_name: str,
        avatar: Optional[str],
    ) -> None:
        self.backend_url = backend_url
        self.protocol_version = protocol_version
        self.audio_params = audio_params
        self._send_text = send_text
        self._client_uid = client_uid
        self._display_name = display_name
        self._avatar = avatar
        self._device_id = device_id or f"mio-{client_uid}"
        self._client_id = client_id or f"mio-client-{client_uid}"
        self._access_token = access_token

        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._recv_task: Optional[asyncio.Task] = None
        self._send_lock = asyncio.Lock()
        self._connect_lock = asyncio.Lock()
        self._reconnect_task: Optional[asyncio.Task] = None

        self._encoder = Encoder(
            audio_params.sample_rate,
            audio_params.channels,
            APPLICATION_AUDIO,
        )
        self._decoder = Decoder(audio_params.sample_rate, audio_params.channels)
        if audio_params.format != "opus":
            logger.warning(
                f"xiaozhi gateway expects opus audio, got {audio_params.format}"
            )

        self._frame_size = (
            audio_params.sample_rate * audio_params.frame_duration // 1000
        )
        self._frame_bytes = self._frame_size * audio_params.channels * 2
        self._tts_chunk_samples = max(
            1, audio_params.sample_rate * TTS_STREAM_CHUNK_MS // 1000
        )
        self._tts_chunk_bytes = self._tts_chunk_samples * audio_params.channels * 2
        self._pcm_buffer = bytearray()
        self._tts_pcm = bytearray()
        self._listening = False
        self._tts_active = False
        self._tts_sent_audio = False
        self._tts_display_sent = False
        self._llm_text = ""
        self._closed = False
        self._mcp_server = XiaoZhiMcpServer(
            send_callback=self._send_mcp_payload,
            capture_callback=self._request_capture_from_web,
            device_id=self._device_id,
            client_id=self._client_id,
        )

    async def connect(self) -> None:
        if self._closed:
            return
        if self._session or self._ws:
            return
        await self._connect_once()
        self._recv_task = asyncio.create_task(self._recv_loop())

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
        if self._recv_task and not self._recv_task.done():
            self._recv_task.cancel()
        await self._disconnect()

    async def _connect_once(self) -> None:
        async with self._connect_lock:
            if self._closed or self._session or self._ws:
                return
            self._session = aiohttp.ClientSession()
            headers = {
                "Protocol-Version": str(self.protocol_version),
                "Client-Id": self._client_id,
                "Device-Id": self._device_id,
            }
            if self._access_token:
                headers["Authorization"] = f"Bearer {self._access_token}"
            try:
                self._ws = await self._session.ws_connect(
                    self.backend_url, headers=headers
                )
            except Exception:
                await self._disconnect()
                raise
            await self._send_hello()

    async def _disconnect(self) -> None:
        if self._ws and not self._ws.closed:
            await self._ws.close()
        if self._session:
            await self._session.close()
        self._ws = None
        self._session = None

    async def handle_audio_data(self, audio: list[float]) -> None:
        if not audio or not self._ws:
            return
        if not self._listening:
            await self._send_listen("start")
            self._listening = True

        pcm_bytes = self._float32_to_pcm16(audio)
        if pcm_bytes:
            self._pcm_buffer.extend(pcm_bytes)
            await self._flush_pcm_buffer()

    async def handle_audio_end(self) -> None:
        if not self._ws:
            return
        self._llm_text = ""
        await self._flush_pcm_buffer(final=True)
        await self._send_listen("stop")
        self._listening = False
        await self._send_conversation_start_signals()

    async def handle_abort(self) -> None:
        if not self._ws:
            return
        await self._send_json({"type": "abort", "reason": "user_interrupt"})
        self._reset_tts_state()

    async def handle_text_input(self, text: str) -> None:
        if not self._ws:
            return
        text = text.strip()
        if not text:
            return
        await self._send_json(
            {
                "type": "listen",
                "state": "detect",
                "mode": "auto",
                "text": text,
                "device_id": self._device_id,
            }
        )

    async def _send_hello(self) -> None:
        hello = {
            "type": "hello",
            "version": self.protocol_version,
            "features": {"mcp": True},
            "transport": "websocket",
            "audio_params": {
                "format": self.audio_params.format,
                "sample_rate": self.audio_params.sample_rate,
                "channels": self.audio_params.channels,
                "frame_duration": self.audio_params.frame_duration,
            },
        }
        await self._send_json(hello)

    async def _send_listen(self, state: str) -> None:
        await self._send_json(
            {
                "type": "listen",
                "state": state,
                "mode": "auto",
                "device_id": self._device_id,
            }
        )

    async def _send_json(self, payload: dict) -> None:
        if not self._ws or self._ws.closed:
            return
        async with self._send_lock:
            await self._ws.send_str(json.dumps(payload))

    async def _flush_pcm_buffer(self, final: bool = False) -> None:
        if not self._ws:
            return
        while len(self._pcm_buffer) >= self._frame_bytes:
            frame = bytes(self._pcm_buffer[: self._frame_bytes])
            del self._pcm_buffer[: self._frame_bytes]
            opus_frame = self._encoder.encode(frame, self._frame_size)
            if opus_frame:
                await self._ws.send_bytes(opus_frame)

        if final and self._pcm_buffer:
            padding = self._frame_bytes - len(self._pcm_buffer)
            frame = bytes(self._pcm_buffer) + b"\x00" * padding
            self._pcm_buffer.clear()
            opus_frame = self._encoder.encode(frame, self._frame_size)
            if opus_frame:
                await self._ws.send_bytes(opus_frame)

    async def _recv_loop(self) -> None:
        assert self._ws is not None
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self._handle_text_message(msg.data)
                elif msg.type == aiohttp.WSMsgType.BINARY:
                    await self._handle_audio_frame(msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error(f"xiaozhi gateway recv error: {exc}")
        finally:
            if not self._closed:
                await self._notify_backend_closed()
                await self._disconnect()
                await self._schedule_reconnect()

    async def _schedule_reconnect(self) -> None:
        if self._closed:
            return
        if self._reconnect_task and not self._reconnect_task.done():
            return
        self._reconnect_task = asyncio.create_task(self._reconnect_loop())

    async def _reconnect_loop(self) -> None:
        delay = 1.0
        max_delay = 30.0
        while not self._closed:
            try:
                await self._connect_once()
                self._recv_task = asyncio.create_task(self._recv_loop())
                return
            except Exception as exc:
                logger.warning(f"xiaozhi gateway reconnect failed: {exc}")
            await asyncio.sleep(delay)
            delay = min(delay * 2, max_delay)

    async def _handle_text_message(self, data: str) -> None:
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            logger.warning("xiaozhi gateway received invalid json")
            return

        msg_type = payload.get("type")
        if msg_type == "hello":
            return
        if msg_type == "mcp":
            mcp_payload = payload.get("payload")
            if mcp_payload is None:
                logger.warning("xiaozhi gateway received MCP message without payload")
                return
            if isinstance(mcp_payload, str):
                try:
                    mcp_payload = json.loads(mcp_payload)
                except json.JSONDecodeError:
                    logger.warning("xiaozhi gateway received invalid MCP payload")
                    return
            await self._mcp_server.parse_message(mcp_payload)
            return
        if msg_type == "stt":
            text = payload.get("text", "")
            if text:
                await self._send_text(json.dumps({"type": "user-input-transcription", "text": text}))
            return
        if msg_type == "llm":
            text = payload.get("text", "")
            if text:
                if payload.get("state") == "stream":
                    self._llm_text += text
                else:
                    self._llm_text = text
                await self._send_text(json.dumps({"type": "full-text", "text": self._llm_text}))
            return
        if msg_type == "text":
            text = payload.get("text", "")
            if text:
                self._llm_text = text
                await self._send_text(json.dumps({"type": "full-text", "text": self._llm_text}))
            return
        if msg_type == "tts":
            await self._handle_tts_state(payload.get("state"), payload.get("text"))
            return
        if msg_type == "goodbye":
            await self.close()
            return

    async def _send_mcp_payload(self, payload: dict) -> None:
        await self._send_json({"type": "mcp", "payload": payload})

    async def _request_capture_from_web(
        self, source: str, question: str, display: Optional[str]
    ) -> dict:
        if not self._send_text:
            return {"success": False, "message": "websocket send is not available"}
        request_id = str(uuid.uuid4())
        request = {
            "type": "mcp-capture-request",
            "request_id": request_id,
            "source": source,
            "question": question,
            "display": display or "",
        }
        await self._send_text(json.dumps(request))
        response = await message_handler.wait_for_response(
            self._client_uid, "mcp-capture-response", request_id=request_id, timeout=30
        )
        if not response:
            return {"success": False, "message": "capture timeout"}
        if not response.get("success"):
            return {
                "success": False,
                "message": response.get("message", "capture failed"),
            }

        image_data = response.get("image", "")
        mime_type = response.get("mime_type", "image/jpeg")
        image_bytes = self._decode_capture_image(image_data)
        if not image_bytes:
            return {"success": False, "message": "empty capture image"}
        return {
            "success": True,
            "image_bytes": image_bytes,
            "mime_type": mime_type,
        }

    @staticmethod
    def _decode_capture_image(image_data: str) -> Optional[bytes]:
        if not image_data or not isinstance(image_data, str):
            return None
        if image_data.startswith("data:"):
            try:
                _, encoded = image_data.split(",", 1)
            except ValueError:
                return None
            try:
                return base64.b64decode(encoded)
            except (ValueError, TypeError):
                return None
        try:
            return base64.b64decode(image_data)
        except (ValueError, TypeError):
            return None

    async def _handle_tts_state(self, state: str | None, text: str | None) -> None:
        if state == "sentence_start" and text:
            if self._llm_text:
                self._llm_text += text
            else:
                self._llm_text = text
            await self._send_text(json.dumps({"type": "full-text", "text": self._llm_text}))
            return
        if state == "start":
            self._tts_active = True
            self._tts_pcm.clear()
            self._tts_sent_audio = False
            self._tts_display_sent = False
            return
        if state == "stop":
            self._tts_active = False
            await self._finalize_tts_audio()
            return

    async def _handle_audio_frame(self, frame: bytes) -> None:
        if not frame:
            return
        if not self._tts_active:
            return
        try:
            frame_size = opus_decoder_api.get_nb_samples(
                self._decoder.decoder_state, frame, len(frame)
            )
            pcm = self._decoder.decode(frame, frame_size)
        except Exception as exc:
            logger.error(f"xiaozhi gateway decode error: {exc}")
            return
        if pcm:
            self._tts_pcm.extend(pcm)
            await self._flush_tts_chunks(final=False)

    async def _flush_tts_chunks(self, final: bool) -> None:
        if self._tts_chunk_bytes <= 0:
            return
        while len(self._tts_pcm) >= self._tts_chunk_bytes:
            chunk = bytes(self._tts_pcm[: self._tts_chunk_bytes])
            del self._tts_pcm[: self._tts_chunk_bytes]
            await self._send_tts_audio_chunk(chunk)
        if final and self._tts_pcm:
            chunk = bytes(self._tts_pcm)
            self._tts_pcm.clear()
            await self._send_tts_audio_chunk(chunk)

    async def _send_tts_audio_chunk(self, pcm_bytes: bytes) -> None:
        if not pcm_bytes:
            return
        pcm_array = np.frombuffer(pcm_bytes, dtype=np.int16)
        pcm_faded = self._apply_tts_fade(pcm_array)
        wav_bytes = self._pcm_to_wav_bytes(pcm_faded)
        include_display_text = not self._tts_display_sent
        audio_payload = self._build_audio_payload(
            wav_bytes, pcm_array, include_display_text
        )
        await self._send_text(json.dumps(audio_payload))
        self._tts_sent_audio = True
        if include_display_text:
            self._tts_display_sent = True

    async def _finalize_tts_audio(self) -> None:
        await self._flush_tts_chunks(final=True)
        if not self._tts_sent_audio:
            await self._send_conversation_end_signals()
            self._reset_tts_state()
            return
        await self._send_text(json.dumps({"type": "backend-synth-complete"}))

        await message_handler.wait_for_response(
            self._client_uid, "frontend-playback-complete", timeout=15
        )
        await self._send_text(json.dumps({"type": "force-new-message"}))
        await self._send_conversation_end_signals()
        self._reset_tts_state()

    async def _send_conversation_start_signals(self) -> None:
        await self._send_text(
            json.dumps({"type": "control", "text": "conversation-chain-start"})
        )
        await self._send_text(json.dumps({"type": "full-text", "text": "Thinking..."}))

    async def _send_conversation_end_signals(self) -> None:
        await self._send_text(
            json.dumps({"type": "control", "text": "conversation-chain-end"})
        )

    async def _notify_backend_closed(self) -> None:
        if self._closed:
            return
        await self._send_text(
            json.dumps({"type": "error", "message": "xiaozhi backend disconnected"})
        )

    def _reset_tts_state(self) -> None:
        self._tts_pcm.clear()
        self._tts_active = False
        self._tts_sent_audio = False
        self._tts_display_sent = False
        self._llm_text = ""

    def _build_audio_payload(
        self, wav_bytes: bytes, pcm_array: np.ndarray, include_display_text: bool
    ) -> dict:
        volumes = self._compute_volumes(pcm_array)
        display_text = None
        if include_display_text:
            display_text = DisplayText(
                text=self._llm_text,
                name=self._display_name,
                avatar=self._avatar,
            ).to_dict()
        return {
            "type": "audio",
            "audio": base64.b64encode(wav_bytes).decode("utf-8"),
            "audio_pcm": base64.b64encode(pcm_array.tobytes()).decode("utf-8"),
            "audio_format": "pcm16",
            "audio_sample_rate": self.audio_params.sample_rate,
            "audio_channels": self.audio_params.channels,
            "volumes": volumes,
            "slice_length": self.audio_params.frame_duration,
            "display_text": display_text,
            "actions": None,
            "forwarded": False,
        }

    def _apply_tts_fade(self, pcm_array: np.ndarray) -> np.ndarray:
        if TTS_FADE_MS <= 0:
            return pcm_array
        channels = self.audio_params.channels
        if channels <= 0:
            return pcm_array
        if pcm_array.size < channels * 2:
            return pcm_array
        frames = pcm_array.size // channels
        fade_frames = min(
            frames // 2,
            max(1, int(self.audio_params.sample_rate * TTS_FADE_MS / 1000)),
        )
        if fade_frames <= 0:
            return pcm_array
        audio = pcm_array.astype(np.float32, copy=True).reshape(frames, channels)
        fade_in = np.linspace(0.0, 1.0, fade_frames, dtype=np.float32)
        fade_out = np.linspace(1.0, 0.0, fade_frames, dtype=np.float32)
        audio[:fade_frames] *= fade_in[:, None]
        audio[-fade_frames:] *= fade_out[:, None]
        audio = np.clip(np.rint(audio), -32768, 32767).astype(np.int16)
        return audio.reshape(-1)

    def _pcm_to_wav_bytes(self, pcm_array: np.ndarray) -> bytes:
        buffer = io.BytesIO()
        sf.write(
            buffer,
            pcm_array,
            self.audio_params.sample_rate,
            format="WAV",
            subtype="PCM_16",
        )
        return buffer.getvalue()

    def _compute_volumes(self, pcm_array: np.ndarray) -> list[float]:
        if pcm_array.size == 0:
            return []
        chunk_size = int(
            self.audio_params.sample_rate * self.audio_params.frame_duration / 1000
        )
        if chunk_size <= 0:
            return []
        volumes = []
        for start in range(0, len(pcm_array), chunk_size):
            chunk = pcm_array[start : start + chunk_size]
            if chunk.size == 0:
                continue
            rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
            volumes.append(rms)
        max_volume = max(volumes, default=0.0)
        if max_volume == 0:
            return [0.0 for _ in volumes]
        return [volume / max_volume for volume in volumes]

    @staticmethod
    def _float32_to_pcm16(audio: list[float]) -> bytes:
        samples = np.asarray(audio, dtype=np.float32)
        if samples.size == 0:
            return b""
        max_abs = float(np.max(np.abs(samples)))
        if max_abs > 1.5:
            samples = np.clip(samples, -32768, 32767)
            pcm = samples.astype(np.int16)
        else:
            samples = np.clip(samples, -1.0, 1.0)
            pcm = (samples * 32767.0).astype(np.int16)
        return pcm.tobytes()
