"""
Channel Voice - AI Agent -> TTS -> IM Voice Messages
"""

__version__ = "0.2.0"

from .tts import TTSBase, EdgeTTS, VolcTTS, create_engine as create_tts_engine
from .channel import ChannelBase, FeishuChannel, TelegramChannel, create_channel
from . import audio


class VoiceGateway:
    """Unified entry point: text -> TTS -> IM channel"""

    def __init__(self, config=None):
        if config is None:
            from .config import get_config
            config = get_config()
        self.config = config
        self.tts = create_tts_engine(config)
        self.channel = create_channel(config)

    async def send(self, text):
        """One-liner: text -> voice -> send"""
        import tempfile, time, os

        # Check cache
        cached = audio.get_cached_audio(text, self.tts.name,
                                         getattr(self.tts, 'voice', '') or
                                         getattr(self.tts, 'speaker', ''))
        if cached:
            return self.channel.send_voice(cached, audio.get_ogg_duration_ms(cached, self.config.ffmpeg_path))

        # Generate
        mp3_path = audio.temp_mp3_path()
        success = await self.tts.synthesize(text, mp3_path)
        if not success:
            raise RuntimeError("TTS synthesis failed")

        # Transcode
        ogg_path = audio.convert_to_opus(mp3_path, self.config.ffmpeg_path)
        if not ogg_path:
            raise RuntimeError("Audio transcoding failed")
        if os.path.exists(mp3_path):
            os.remove(mp3_path)

        duration_ms = audio.get_ogg_duration_ms(ogg_path, self.config.ffmpeg_path)

        # Cache
        audio.set_cached_audio(text, self.tts.name,
                               getattr(self.tts, 'voice', '') or
                               getattr(self.tts, 'speaker', ''),
                               ogg_path)

        return self.channel.send_voice(ogg_path, duration_ms)


__all__ = [
    "TTSBase", "EdgeTTS", "VolcTTS",
    "ChannelBase", "FeishuChannel", "TelegramChannel",
    "VoiceGateway", "audio",
]
