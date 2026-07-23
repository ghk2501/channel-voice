"""
配置管理 - 从 .env 加载配置
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    # 飞书
    app_id: str = ""
    app_secret: str = ""
    chat_id: str = ""

    # FFmpeg（用于音频转码）
    ffmpeg_path: str = "ffmpeg"

    # TTS 引擎: edge-tts / volc
    tts_engine: str = "edge-tts"

    # Edge-TTS 音色
    edge_tts_voice: str = "zh-CN-XiaoyiNeural"

    # 火山引擎 TTS V3（豆包语音大模型）
    volc_api_key: str = ""
    volc_resource_id: str = "seed-tts-2.0"
    volc_speaker: str = ""

    # Channel: feishu / telegram / dingtalk
    channel: str = "feishu"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    dingtalk_key: str = ""
    dingtalk_secret: str = ""
    dingtalk_chat_id: str = ""

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Config":
        if env_file and os.path.exists(env_file):
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
            except ImportError:
                pass

        cfg = cls()
        cfg.app_id = os.getenv("APP_ID", "")
        cfg.app_secret = os.getenv("APP_SECRET", "")
        cfg.chat_id = os.getenv("CHAT_ID", "")
        cfg.ffmpeg_path = os.getenv("FFMPEG_PATH", "ffmpeg")
        cfg.tts_engine = os.getenv("TTS_ENGINE", "edge-tts")

        voice = os.getenv("EDGE_TTS_VOICE", "")
        if voice:
            cfg.edge_tts_voice = voice

        cfg.volc_api_key = os.getenv("VOLC_API_KEY", "")
        rid = os.getenv("VOLC_RESOURCE_ID", "")
        if rid:
            cfg.volc_resource_id = rid
        spk = os.getenv("VOLC_SPEAKER", "")
        if spk:
            cfg.volc_speaker = spk

        cfg.channel = os.getenv("CHANNEL", "feishu")
        cfg.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        cfg.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        cfg.dingtalk_key = os.getenv("DINGTALK_KEY", "")
        cfg.dingtalk_secret = os.getenv("DINGTALK_SECRET", "")
        cfg.dingtalk_chat_id = os.getenv("DINGTALK_CHAT_ID", "")

        return cfg

    def validate(self) -> list[str]:
        missing = []
        if not self.app_id:
            missing.append("APP_ID")
        if not self.app_secret:
            missing.append("APP_SECRET")
        if not self.chat_id:
            missing.append("CHAT_ID")
        if self.tts_engine == "volc":
            if not self.volc_api_key:
                missing.append("VOLC_API_KEY")
            if not self.volc_speaker:
                missing.append("VOLC_SPEAKER")
        if self.channel == "telegram":
            if not self.telegram_bot_token:
                missing.append("TELEGRAM_BOT_TOKEN")
            if not self.telegram_chat_id:
                missing.append("TELEGRAM_CHAT_ID")
        if self.channel == "dingtalk":
            if not self.dingtalk_key:
                missing.append("DINGTALK_KEY")
            if not self.dingtalk_secret:
                missing.append("DINGTALK_SECRET")
            if not self.dingtalk_chat_id:
                missing.append("DINGTALK_CHAT_ID")
        return missing


_config: Optional[Config] = None


def get_config(env_file: Optional[str] = None) -> Config:
    global _config
    if _config is None:
        _config = Config.from_env(env_file)
    return _config
