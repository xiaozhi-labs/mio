# config_manager/system.py
from pydantic import Field, model_validator
from typing import Dict, ClassVar, Optional
from .i18n import I18nMixin, Description


class SystemConfig(I18nMixin):
    """System configuration settings."""

    conf_version: str = Field(..., alias="conf_version")
    host: str = Field(..., alias="host")
    port: int = Field(..., alias="port")
    config_alts_dir: str = Field(..., alias="config_alts_dir")
    tool_prompts: Dict[str, str] = Field(..., alias="tool_prompts")
    enable_proxy: bool = Field(False, alias="enable_proxy")
    xiaozhi_backend_url: str = Field(..., alias="xiaozhi_backend_url")
    xiaozhi_protocol_version: int = Field(1, alias="xiaozhi_protocol_version")
    xiaozhi_audio_format: str = Field("opus", alias="xiaozhi_audio_format")
    xiaozhi_sample_rate: int = Field(16000, alias="xiaozhi_sample_rate")
    xiaozhi_channels: int = Field(1, alias="xiaozhi_channels")
    xiaozhi_frame_duration: int = Field(20, alias="xiaozhi_frame_duration")
    xiaozhi_device_id: Optional[str] = Field(None, alias="xiaozhi_device_id")
    xiaozhi_client_id: Optional[str] = Field(None, alias="xiaozhi_client_id")
    xiaozhi_access_token: Optional[str] = Field(None, alias="xiaozhi_access_token")

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "conf_version": Description(en="Configuration version", zh="配置文件版本"),
        "host": Description(en="Server host address", zh="服务器主机地址"),
        "port": Description(en="Server port number", zh="服务器端口号"),
        "config_alts_dir": Description(
            en="Directory for alternative configurations", zh="备用配置目录"
        ),
        "tool_prompts": Description(
            en="Tool prompts to be inserted into persona prompt",
            zh="要插入到角色提示词中的工具提示词",
        ),
        "enable_proxy": Description(
            en="Enable proxy mode for multiple clients",
            zh="启用代理模式以支持多个客户端使用一个 ws 连接",
        ),
        "xiaozhi_backend_url": Description(
            en="XiaoZhi backend WebSocket URL",
            zh="XiaoZhi 后端 WebSocket 地址",
        ),
        "xiaozhi_protocol_version": Description(
            en="XiaoZhi protocol version",
            zh="XiaoZhi 协议版本",
        ),
        "xiaozhi_audio_format": Description(
            en="XiaoZhi audio format",
            zh="XiaoZhi 音频格式",
        ),
        "xiaozhi_sample_rate": Description(
            en="XiaoZhi sample rate",
            zh="XiaoZhi 采样率",
        ),
        "xiaozhi_channels": Description(
            en="XiaoZhi audio channels",
            zh="XiaoZhi 声道数",
        ),
        "xiaozhi_frame_duration": Description(
            en="XiaoZhi frame duration (ms)",
            zh="XiaoZhi 帧时长（毫秒）",
        ),
        "xiaozhi_device_id": Description(
            en="XiaoZhi device id (Device-Id header)",
            zh="XiaoZhi 设备 ID（Device-Id 头）",
        ),
        "xiaozhi_client_id": Description(
            en="XiaoZhi client id (Client-Id header)",
            zh="XiaoZhi 客户端 ID（Client-Id 头）",
        ),
        "xiaozhi_access_token": Description(
            en="XiaoZhi access token (Authorization header)",
            zh="XiaoZhi 访问令牌（Authorization 头）",
        ),
    }

    @model_validator(mode="after")
    def check_port(cls, values):
        port = values.port
        if port < 0 or port > 65535:
            raise ValueError("Port must be between 0 and 65535")
        return values
