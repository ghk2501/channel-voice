"""
IM Channel Module - Plugin-based architecture
"""

from .base import ChannelBase
from .feishu import FeishuChannel
from .telegram import TelegramChannel


def create_channel(config):
    """Factory: create IM channel from config"""
    channel_name = config.channel or "feishu"
    if channel_name == "feishu":
        return FeishuChannel(config.app_id, config.app_secret, config.chat_id)
    elif channel_name == "telegram":
        return TelegramChannel(config.telegram_bot_token, config.telegram_chat_id)
    else:
        raise ValueError(f"Unsupported channel: {channel_name}")


__all__ = ["ChannelBase", "FeishuChannel", "TelegramChannel", "create_channel"]
