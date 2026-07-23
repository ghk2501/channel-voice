"""
Telegram Channel - Voice message send via Bot API
"""

import requests
from .base import ChannelBase


class TelegramChannel(ChannelBase):
    """Telegram voice message channel"""
    name = "telegram"
    MAX_RETRIES = 2

    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_base = f"https://api.telegram.org/bot{bot_token}"

    def send_voice(self, audio_path, duration_ms):
        with open(audio_path, "rb") as f:
            resp = requests.post(
                f"{self.api_base}/sendVoice",
                files={"voice": ("voice.ogg", f, "audio/ogg")},
                data={"chat_id": self.chat_id, "duration": duration_ms // 1000},
                timeout=60,
            )
        resp.raise_for_status()
        return True

    def validate_config(self):
        missing = []
        if not self.bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not self.chat_id:
            missing.append("TELEGRAM_CHAT_ID")
        return missing
