"""
Audio utilities - format conversion, caching, text splitting
"""

import os
import hashlib
import subprocess
import tempfile
import time


CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cache")


def convert_to_opus(mp3_path, ffmpeg_path="ffmpeg"):
    """MP3 -> Opus OGG (Feishu format)"""
    ogg_path = mp3_path.replace(".mp3", ".ogg")
    result = subprocess.run(
        [ffmpeg_path, "-y", "-i", mp3_path, "-c:a", "libopus", "-b:a", "24k", "-vbr", "on", ogg_path],
        capture_output=True, timeout=60,
    )
    return ogg_path if result.returncode == 0 else None


def convert_to_amr(mp3_path, ffmpeg_path="ffmpeg"):
    """MP3 -> AMR (DingTalk format)"""
    amr_path = mp3_path.replace(".mp3", ".amr")
    result = subprocess.run(
        [ffmpeg_path, "-y", "-i", mp3_path, "-ar", "8000", "-ac", "1", "-c:a", "libvo_amrwbenc", amr_path],
        capture_output=True, timeout=60,
    )
    return amr_path if result.returncode == 0 else None


def get_ogg_duration_ms(ogg_path, ffmpeg_path="ffmpeg"):
    """Get OGG duration in ms via ffprobe, fallback to estimate"""
    ffprobe_path = ffmpeg_path.replace("ffmpeg", "ffprobe") if ffmpeg_path != "ffmpeg" else "ffprobe"
    try:
        result = subprocess.run(
            [ffprobe_path, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", ogg_path],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(float(result.stdout.strip()) * 1000)
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass
    return int(max(1, os.path.getsize(ogg_path) / 3000) * 1000)


def split_text(text, max_chars=5000, min_chunk=500):
    """Smart text splitting by sentence boundaries"""
    if len(text) <= max_chars:
        return [text]
    chunks = []
    for separator in ["\n\n", "\n", "。", "！", "？", ". ", "! ", "? "]:
        if len(text) <= max_chars:
            break
        parts = []
        for segment in text.split(separator):
            if not segment:
                continue
            if parts and len(parts[-1]) + len(segment) + len(separator) < max_chars:
                parts[-1] = parts[-1] + separator + segment
            else:
                if parts:
                    parts.append(segment)
                else:
                    parts.append(segment)
        text = separator.join(parts)
    while len(text) > 0:
        if len(text) <= max_chars:
            chunks.append(text)
            break
        cut = text.rfind("。", 0, max_chars)
        if cut < min_chunk:
            cut = text.rfind("，", 0, max_chars)
        if cut < min_chunk:
            cut = text.rfind(" ", 0, max_chars)
        if cut < min_chunk:
            cut = max_chars
        else:
            cut += 1
        chunks.append(text[:cut])
        text = text[cut:]
    return [c.strip() for c in chunks if c.strip()]


def cache_key(text, engine, voice):
    """Generate cache key from text + engine + voice"""
    raw = f"{engine}:{voice}:{text}".encode()
    return hashlib.md5(raw).hexdigest()


def get_cached_audio(text, engine, voice, ext=".ogg"):
    """Get cached audio path if available"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = cache_key(text, engine, voice)
    path = os.path.join(CACHE_DIR, f"{key}{ext}")
    return path if os.path.exists(path) else None


def set_cached_audio(text, engine, voice, audio_path, ext=".ogg"):
    """Cache generated audio file"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = cache_key(text, engine, voice)
    dest = os.path.join(CACHE_DIR, f"{key}{ext}")
    if not os.path.exists(dest):
        import shutil
        shutil.copy2(audio_path, dest)
    return dest


def temp_mp3_path():
    """Generate unique temp MP3 path"""
    return os.path.join(tempfile.gettempdir(), f"cv_{int(time.time() * 1000)}_{os.getpid()}.mp3")
