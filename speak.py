#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Channel Voice - Send TTS voice messages via IM channels

Usage:
  python speak.py "Hello world"
  echo "Hello" | python speak.py
  python speak.py --channel telegram "Hello"
  python speak.py --split "Long article text..."
"""

import sys
import os
import time
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import get_config
from src.tts import create_engine as create_tts
from src.channel import create_channel
from src.audio import convert_to_opus, get_ogg_duration_ms, split_text, temp_mp3_path, get_cached_audio, set_cached_audio
from src.tts.base import MAX_TEXT_LENGTH


def main():
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Parse args
    args = sys.argv[1:]
    channel_name = "feishu"
    do_split = False

    while args and args[0].startswith("--"):
        if args[0] == "--channel" and len(args) > 1:
            channel_name = args[1]
            args = args[2:]
        elif args[0] == "--split":
            do_split = True
            args = args[1:]
        else:
            print(f"Unknown flag: {args[0]}", file=sys.stderr)
            sys.exit(1)

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    cfg = get_config(env_path)

    # Override channel if specified
    if channel_name:
        cfg.channel = channel_name

    missing = cfg.validate()
    if missing:
        print(f"[Error] Missing config: {', '.join(missing)}", file=sys.stderr)
        print(f"        Copy .env.example to .env and fill in the values", file=sys.stderr)
        sys.exit(1)

    if args:
        text = " ".join(args)
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        print("Usage: python speak.py [--channel feishu|telegram] [--split] <text>", file=sys.stderr)
        print("   or: echo 'text' | python speak.py", file=sys.stderr)
        sys.exit(1)

    if not text:
        print("[Error] Text cannot be empty", file=sys.stderr)
        sys.exit(1)

    tts = create_tts(cfg)
    channel = create_channel(cfg)

    # Validate channel config
    chan_missing = channel.validate_config()
    if chan_missing:
        print(f"[Error] Channel '{channel.name}' missing: {', '.join(chan_missing)}", file=sys.stderr)
        sys.exit(1)

    # Split long text if needed
    texts = split_text(text) if do_split else [text]

    for i, chunk in enumerate(texts):
        if not chunk.strip():
            continue
        is_multi = len(texts) > 1
        prefix = f"[{i + 1}/{len(texts)}] " if is_multi else ""

        if len(chunk) > MAX_TEXT_LENGTH:
            print(f"{prefix}[Error] Text too long ({len(chunk)} chars), max {MAX_TEXT_LENGTH}", file=sys.stderr)
            continue

        preview = chunk[:60]
        print(f"{prefix}[Voice] {preview}{'...' if len(chunk) > 60 else ''}")

        # Check cache
        voice_id = getattr(tts, 'voice', '') or getattr(tts, 'speaker', '')
        cached = get_cached_audio(chunk, tts.name, voice_id)
        if cached:
            print(f"{prefix}[Cache] Using cached audio")
            duration_ms = get_ogg_duration_ms(cached, cfg.ffmpeg_path)
            channel.send_voice(cached, duration_ms)
            print(f"{prefix}Sent (cached) | {channel.name} | {duration_ms // 1000}s")
            if is_multi and i < len(texts) - 1:
                time.sleep(1)
            continue

        # Generate TTS
        mp3_path = temp_mp3_path()
        print(f"{prefix}[TTS] Synthesizing...", end=" ", flush=True)
        success = asyncio.run(tts.synthesize(chunk, mp3_path))
        if not success:
            print("FAILED")
            if os.path.exists(mp3_path):
                os.remove(mp3_path)
            continue
        mp3_size = os.path.getsize(mp3_path)
        print(f"OK ({mp3_size / 1024:.0f}KB, {tts.name})")

        # Transcode
        print(f"{prefix}[Transcode] Opus...", end=" ", flush=True)
        ogg_path = convert_to_opus(mp3_path, cfg.ffmpeg_path)
        if not ogg_path:
            print("FAILED")
            if os.path.exists(mp3_path):
                os.remove(mp3_path)
            continue
        duration_ms = get_ogg_duration_ms(ogg_path, cfg.ffmpeg_path)
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
        print(f"OK ({duration_ms // 1000}s)")

        # Cache
        set_cached_audio(chunk, tts.name, voice_id, ogg_path)

        # Send
        print(f"{prefix}[Send] {channel.name}...", end=" ", flush=True)
        try:
            channel.send_voice(ogg_path, duration_ms)
            print("OK")
        except Exception as e:
            print(f"FAILED: {e}")
            continue
        finally:
            if os.path.exists(ogg_path):
                os.remove(ogg_path)

        print(f"{prefix}Sent | {channel.name} | {duration_ms // 1000}s")

        if is_multi and i < len(texts) - 1:
            time.sleep(1)


if __name__ == "__main__":
    main()
