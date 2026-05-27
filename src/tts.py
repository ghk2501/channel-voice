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

import edge_tts
import requests

from src.config import Config

# 单次合成文本上限（chars），超长文本走分段
MAX_TEXT_LENGTH = 5000


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
        if len(text) > MAX_TEXT_LENGTH:
            print(
                f"[EdgeTTS] 文本过长 ({len(text)} chars) 超过上限 {MAX_TEXT_LENGTH}，请分段发送",
                file=sys.stderr,
            )
            return False

        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await asyncio.wait_for(communicate.save(output_path), timeout=120)
            return os.path.exists(output_path) and os.path.getsize(output_path) > 100
        except asyncio.TimeoutError:
            print("[EdgeTTS] 语音合成超时", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[EdgeTTS] 合成失败: {e}", file=sys.stderr)
            return False


class VolcTTS(TTSBase):
    """火山引擎 TTS V3（豆包语音大模型）"""

    name = "volc"

    API_URL = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"

    def __init__(self, api_key: str, resource_id: str, speaker: str):
        self.api_key = api_key
        self.resource_id = resource_id
        self.speaker = speaker

    async def synthesize(self, text: str, output_path: str) -> bool:
        if len(text) > MAX_TEXT_LENGTH:
            print(
                f"[VolcTTS] 文本过长 ({len(text)} chars) 超过上限 {MAX_TEXT_LENGTH}，请分段发送",
                file=sys.stderr,
            )
            return False

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
                timeout=(15, 60),
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

        except requests.Timeout:
            print("[VolcTTS] 请求超时", file=sys.stderr)
            return False
        except requests.RequestException as e:
            print(f"[VolcTTS] 请求失败: {e}", file=sys.stderr)
            if hasattr(e, "response") and e.response is not None:
                print(f"  响应: {e.response.text[:300]}", file=sys.stderr)
            return False
        except (json.JSONDecodeError, ValueError) as e:
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


def get_ogg_duration_ms(ogg_path: str, ffmpeg_path: str = "ffmpeg") -> int:
    """
    获取 OGG 文件实际时长（ms）。
    优先用 ffprobe 精确读取，失败则按文件大小估算（opus 24kbps ≈ 3KB/s）。
    """
    # 尝试 ffprobe 精确读取
    ffprobe_path = ffmpeg_path.replace("ffmpeg", "ffprobe") if ffmpeg_path != "ffmpeg" else "ffprobe"
    try:
        result = subprocess.run(
            [ffprobe_path, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", ogg_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(float(result.stdout.strip()) * 1000)
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass

    # 降级：文件大小估算
    return int(max(1, os.path.getsize(ogg_path) / 3000) * 1000)
