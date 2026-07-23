"""
TTS Engine Abstract Base
"""

MAX_TEXT_LENGTH = 5000


class TTSBase:
    """Abstract base class for TTS engines"""
    name = "base"

    async def synthesize(self, text, output_path):
        """Synthesize text to audio file. Returns True on success."""
        raise NotImplementedError
