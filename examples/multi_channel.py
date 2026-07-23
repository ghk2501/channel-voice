"""Multi-channel demo"""

import asyncio
from src import VoiceGateway
from src.config import Config


async def send_to_all(text):
    for ch in ["feishu", "telegram"]:
        cfg = Config.from_env(".env")
        cfg.channel = ch
        gw = VoiceGateway(cfg)
        if getattr(gw.channel, "validate_config", lambda: [1])():
            await gw.send(text)
            print(f"Sent via {ch}")

asyncio.run(send_to_all("broadcast"))
