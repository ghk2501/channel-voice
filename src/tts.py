"""
TTS 引擎封装 - 支持 Edge-TTS / 火山引擎 TTS V3
"""

import sys
import os
import json
import base64
import asyncio
import subprocess
from typing import Optional

import requests

from src.config import Config


class TTSBase:
    """TTS 引擎基类"""
    name = "base"

    async def synthesize(self, text: str, output_path: str) -> bool:
        raise NotImplementedError


class EdgeTTS(TTSBase):
    """Edge-TTS（微软免费 TTS）"""
    name = "edge-tts"

    def __init__(self, voice: str = "zh-CN-XiaoyiNeural"):
        self.voice = voice

    async def synthesize(self, text: str, output_path: str) -> bool:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "edge_tts",
            "--voice", self.voice,
            "--text", text,
            "--write-media", output_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        return proc.returncode == 0


class VolcTTS(TTSBase):
    """火山引擎 TTS V3（豆包语音大模型）"""
    name = "volc"

    API_URL = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"

    def __init__(self, api_key: str, resource_id: str, speaker: str):
        self.api_key = api_key
        self.resource_id = resource_id
        self.speaker = speaker

    async def synthesize(self, text: str, output_path: str) -> bool:
        payload = {
            "req_params": {
                "text": text,
                "speaker": self.speaker,
                "additions": json.dumps({
                    "disable_markdown_filter": True,
                    "enable_language_detector": True,
                }),
                "audio_params": {
                    "format": "mp3",
                    "sample_rate": 24000,
                }
            }
        }

        headers = {
            "x-api-key": self.api_key,
            "X-Api-Resource-Id": self.resource_id,
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(
                self.API_URL,
                json=payload,
                headers=headers,
                stream=True,
                timeout=60,
            )
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
                    print(f"[VolcTTS] 错误 code={code}: {obj.get('message', '')}", file=sys.stderr)
                    return False

                b64 = obj.get("data")
                if b64:
                    audio_parts.append(base64.b64decode(b64))

            if not audio_parts:
                print("[VolcTTS] 未获取到音频数据", file=sys.stderr)
                return False

            with open(output_path, "wb") as f:
                f.write(b"".join(audio_parts))
            return True

        except requests.RequestException as e:
            print(f"[VolcTTS] 请求失败: {e}", file=sys.stderr)
            if hasattr(e, "response") and e.response is not None:
                print(f"  响应: {e.response.text[:300]}", file=sys.stderr)
            return False
        except (json.JSONDecodeError, ValueError, base64.binascii.Error) as e:
            print(f"[VolcTTS] 解析失败: {e}", file=sys.stderr)
            return False


def create_engine(config: Config) -> TTSBase:
    """根据配置创建 TTS 引擎实例"""
    if config.tts_engine == "edge-tts":
        return EdgeTTS(voice=config.edge_tts_voice)
    elif config.tts_engine == "volc":
        return VolcTTS(
            api_key=config.volc_api_key,
            resource_id=config.volc_resource_id,
            speaker=config.volc_speaker,
        )
    else:
        raise ValueError(f"不支持的 TTS 引擎: {config.tts_engine}")


def convert_to_opus(mp3_path: str, ffmpeg_path: str) -> Optional[str]:
    """MP3 → Opus OGG（飞书语音格式要求）"""
    ogg_path = mp3_path.replace(".mp3", ".ogg")
    result = subprocess.run(
        [ffmpeg_path, "-y", "-i", mp3_path,
         "-c:a", "libopus", "-b:a", "24k", "-vbr", "on", ogg_path],
        capture_output=True, timeout=60
    )
    return ogg_path if result.returncode == 0 else None


def estimate_ogg_duration_ms(ogg_path: str) -> int:
    """基于文件大小估算 OGG 时长（opus 24kbps ≈ 3KB/s）"""
    return int(max(1, os.path.getsize(ogg_path) / 3000) * 1000)
