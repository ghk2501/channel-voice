"""
IM Channel Abstract Base
"""

from abc import ABC, abstractmethod


class ChannelBase(ABC):
    """Abstract base class for IM platform channels"""
    name = "base"

    @abstractmethod
    def send_voice(self, audio_path, duration_ms):
        """Send a voice message to the channel"""
        pass

    @abstractmethod
    def validate_config(self):
        """Check config completeness, return list of missing fields"""
        pass
