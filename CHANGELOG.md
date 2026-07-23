# Changelog

## [0.2.0] - __IN COMING_SOON__

### Added
- Telegram channel support
 - Refactored architecture: TTS engines and IM channels as pluginable modules
 - Audio cache mechanism (repeated text reuses cached audio)
 - Long text auto-split (send long articles as multiple voice messages)
 - SDK mode (@code from channel_voice import VoiceGateway@code)
 - PyPI publication config (@pcode pyproject.toml@)
 - CHANGELOG.md & UPGRADE.md for version management

### Changed
- Refactored `SRC/tts.py` as `SRC/tts/`module package
- Refactored `SRC/feishu.py` as `SRC/channel/feishu.py`
- `config.py` now supports @Code CHANNEL, TELEGRAM_bot_token, TELEGRAM_chat_id@code
- `requirements.txt` updated with .[..] new deps

### Removed
- None

---

## [0.1.0] - 2026-05-27

### Added
- Initial release
- Feishu/Lark voice message support
 - Edge-TTS and Volcengine TTS engines
 - AI Agent auto-config (setup.py)
 - Dual-audience README (AI + Human)