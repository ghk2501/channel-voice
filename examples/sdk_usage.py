"""SDK usage - integrate into your own Python project"""

import asyncio
from src import VoiceGateway


async def main():
    gw = VoiceGateway()
    await gw.send("Hello via SDK")
    print(f"TTS: {gw.tts.name}, Channel: {gw.channel.name}")

asyncio.run(main())
