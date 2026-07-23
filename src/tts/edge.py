"""
Edge-TTS Engine (Microsoft free TTS)
"""

import os
import asyncio
import edge_tts
from .base import TTSBase, MAX_TEXT_LENGTH


class EdgeTTS(TTSBase):
    """Microsoft Edge-TTS - free, no API key needed"""
    name = "edge-tts"

    def __init__(self, voice="zh-CN-XiaoyiNeural"):
        self.voice = voice

    async def synthesize(self, text, output_path):
        if len(text) > MAX_TEXT_LENGTH:
            print(f"[EdgeTTS] Text too long ({len(text)} chars), max {MAX_TEXT_LENGTH}")
            return False
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await asyncio.wait_for(communicate.save(output_path), timeout=120)
            return os.path.exists(output_path) and os.path.getsize(output_path) > 100
        except asyncio.TimeoutError:
            print("[EdgeTTS] Synthesis timeout")
            return False
        except Exception as e:
            print(f"[EdgeTTS] Synthesis failed: {e}")
            return False
