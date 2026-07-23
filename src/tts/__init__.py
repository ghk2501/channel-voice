"""
TTS Engine Module - Plugin-based architecture
"""

from .base import TTSBase
from .edge import EdgeTTS
from .volc import VolcTTS


def create_engine(config):
    """Factory: create TTS engine from config"""
    if config.tts_engine == "edge-tts":
        return EdgeTTS(voice=config.edge_tts_voice)
    elif config.tts_engine == "volc":
        return VolcTTS(
            api_key=config.volc_api_key,
            resource_id=config.volc_resource_id,
            speaker=config.volc_speaker,
        )
    else:
        raise ValueError(f"Unsupported TTS engine: {config.tts_engine}")


__all__ = ["TTSBase", "EdgeTTS", "VolcTTS", "create_engine"]
