<!--
  Channel Voice — AI Agent → IM Voice Messages
  GitHub: https://github.com/ghk2501/channel-voice
  SEO: This project converts AI Agent text replies into voice messages via TTS
  and sends them to Feishu/Lark chat channels. Supports Edge-TTS and Volcengine.
-->

<p align="center">
  <h1 align="center">Channel Voice</h1>
  <p align="center"><i>Let Agent Speak In Channel</i></p>
  <p align="center">
    <b>AI Agent → TTS → IM Voice Messages</b>
    <br>
    Convert AI text replies into voice messages for Feishu/Lark channels.
    <br>
    Supported TTS: <b>Edge-TTS</b> (free, no API key) · <b>Volcengine</b> (豆包语音, premium Chinese TTS)
    <br>
    <a href="https://github.com/ghk2501/channel-voice"><strong>Explore the docs »</strong></a>
  </p>
  <p align="center">
    <a href="#channel-voice"><img src="https://img.shields.io/badge/python-%3E%3D3.8-blue?logo=python&logoColor=white" alt="Python"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="#"><img src="https://img.shields.io/badge/TTS-Edge--TTS%20%7C%20Volcengine-orange" alt="TTS"></a>
  </p>
</p>

---

> **Why Channel Voice?** Feishu/Lark does not natively support sending voice messages. This tool bridges the gap: your AI Agent generates speech via TTS, transcodes it to Opus format, and delivers it as a playable voice message in your Feishu channel. Designed with a dual-audience README — follow the instructions for AI Agents (Claude Code, etc.) to self-configure, or follow the human guide for manual setup.

### ✨ Features

| Capability | Details |
|------------|---------|
| 🎙️ **TTS Engines** | Edge-TTS (free, 400+ voices) · Volcengine (豆包, best Chinese TTS) |
| 📱 **Target Platform** | Feishu / Lark (飞书) — voice message (Opus) |
| 🤖 **AI-Friendly Setup** | `setup.py` wizard — AI Agents can auto-configure step by step |
| 🔄 **Auto Transcode** | MP3 → Opus via FFmpeg (required by Feishu) |
| 🔐 **Retry & Resilience** | Token auto-refresh, retry logic, error handling |
| 📜 **License** | MIT — free to use, modify, and distribute |

### 🔧 Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your credentials
python speak.py "Hello, this is a voice message"
```

### 🔍 Alternatives

| Project | Platform | Engines | SDK |
|---------|----------|---------|-----|
| **Channel Voice (this)** | Feishu/Lark | 2 | Python |
| tts-feishu | Feishu | 11 | Python + TS |
| feishu-voice | Feishu (OpenClaw) | 1 | Shell |
| agent-voice | Telegram | 1 | Shell |

---

**Have an AI Agent?** Read the [AI Agent Guide](#如果你是-ai-agentclaude-code-等请读这里) below — it can configure itself.
**Are you human?** Jump to the [Human Guide](#如果你是人类请读这里).

---


