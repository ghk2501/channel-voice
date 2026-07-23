"""
Volcengine TTS Engine (豆包语音大模型)
"""

import os
import json
import base64
import requests
from .base import TTSBase, MAX_TEXT_LENGTH


class VolcTTS(TTSBase):
    """Volcengine TTS V3 - premium Chinese TTS"""
    name = "volc"
    API_URL = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"

    def __init__(self, api_key, resource_id, speaker):
        self.api_key = api_key
        self.resource_id = resource_id
        self.speaker = speaker

    async def synthesize(self, text, output_path):
        if len(text) > MAX_TEXT_LENGTH:
            print(f"[VolcTTS] Text too long ({len(text)} chars), max {MAX_TEXT_LENGTH}")
            return False
        payload = {
            "req_params": {
                "text": text,
                "speaker": self.speaker,
                "additions": json.dumps({
                    "disable_markdown_filter": True,
                    "enable_language_detector": True,
                }),
                "audio_params": {"format": "mp3", "sample_rate": 24000}
            }
        }
        headers = {
            "x-api-key": self.api_key,
            "X-Api-Resource-Id": self.resource_id,
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post(self.API_URL, json=payload, headers=headers, stream=True, timeout=(15, 60))
            resp.raise_for_status()
            raw = b"".join(resp.iter_content(4096))
            audio_parts = []
            for line in raw.split(b"\n"):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                code = obj.get("code")
                if code != 0:
                    print(f"[VolcTTS] Error code={code}: {obj.get('message', '')}")
                    return False
                b64 = obj.get("data")
                if b64:
                    audio_parts.append(base64.b64decode(b64))
            if not audio_parts:
                print("[VolcTTS] No audio data received")
                return False
            with open(output_path, "wb") as f:
                f.write(b"".join(audio_parts))
            return True
        except requests.Timeout:
            print("[VolcTTS] Request timeout")
            return False
        except requests.RequestException as e:
            print(f"[VolcTTS] Request failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"  Response: {e.response.text[:300]}")
            return False
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[VolcTTS] Parse failed: {e}")
            return False
