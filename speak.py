#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Echo Voice - 通过飞书发送 TTS 语音消息

用法:
  python speak.py "要说的话"
  echo "要说的话" | python speak.py
"""

import sys
import os
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import get_config
from src.tts import create_engine, convert_to_opus, estimate_ogg_duration_ms
from src.feishu import FeishuClient


def main():
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    cfg = get_config(env_path)

    missing = cfg.validate()
    if missing:
        print(f"[错误] 缺少必要配置: {', '.join(missing)}", file=sys.stderr)
        print(f"       请复制 .env.example 为 .env 并填写", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) >= 2:
        text = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        print("用法: python speak.py <文本>", file=sys.stderr)
        print("  或: echo '文本' | python speak.py", file=sys.stderr)
        sys.exit(1)

    if not text:
        print("[错误] 文本不能为空", file=sys.stderr)
        sys.exit(1)

    preview = text[:60]
    print(f"[语音] {preview}{'...' if len(text) > 60 else ''}")

    import asyncio

    tts = create_engine(cfg)
    mp3_path = os.path.join(tempfile.gettempdir(), f"evo_{int(time.time())}.mp3")

    print("[TTS] 生成语音...", end=" ", flush=True)
    success = asyncio.run(tts.synthesize(text, mp3_path))
    if not success:
        print("失败")
        sys.exit(1)
    print(f"完成 ({os.path.getsize(mp3_path) / 1024:.0f}KB, {tts.name})")

    print("[转码] Opus...", end=" ", flush=True)
    ogg_path = convert_to_opus(mp3_path, cfg.ffmpeg_path)
    if not ogg_path:
        print("失败")
        sys.exit(1)
    ogg_size = os.path.getsize(ogg_path)
    duration_ms = estimate_ogg_duration_ms(ogg_path)
    os.remove(mp3_path)
    print(f"完成 ({ogg_size / 1024:.0f}KB, {duration_ms // 1000}s)")

    print("[飞书] 获取凭证...", end=" ", flush=True)
    client = FeishuClient(cfg.app_id, cfg.app_secret, cfg.chat_id)
    print("完成")

    print("[飞书] 上传...", end=" ", flush=True)
    file_key = client.upload_audio(ogg_path, duration_ms)
    print("完成")

    print("[飞书] 发送...", end=" ", flush=True)
    result = client.send_voice(file_key)
    print("完成")

    os.remove(ogg_path)
    print(f"\n语音已发送 | 引擎: {tts.name} | 时长: {duration_ms // 1000}s")


if __name__ == "__main__":
    main()
