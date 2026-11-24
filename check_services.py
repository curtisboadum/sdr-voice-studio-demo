"""Check credentials and run one tiny LLM and speech request; never print secrets."""
import asyncio
import os
from pathlib import Path

import aiohttp
from dotenv import load_dotenv
from livekit import api
from livekit.agents import inference, llm, utils
from livekit.plugins import cartesia
from config import Settings


async def main() -> None:
    load_dotenv(Path(__file__).with_name('.env'))
    settings = Settings.from_env(os.environ)
    async with api.LiveKitAPI() as client:
        try:
            await client.room.list_rooms(api.ListRoomsRequest())
            print('LiveKit API: OK')
        except Exception as exc:
            print('LiveKit API: FAILED (' + type(exc).__name__ + ')')
    async with aiohttp.ClientSession() as http:
        async with http.get('https://api.deepgram.com/v1/projects', headers={
            'Authorization': 'Token ' + os.environ['DEEPGRAM_API_KEY']}) as response:
            print('Deepgram credentials: HTTP', response.status)
    model = inference.LLM(model=settings.llm_model)
    context = llm.ChatContext()
    context.add_message(role='user', content='Reply with just OK.')
    try:
        output = ''
        async with model.chat(chat_ctx=context) as stream:
            async for chunk in stream:
                if chunk.delta and chunk.delta.content:
                    output += chunk.delta.content
        print('LiveKit ' + settings.llm_model + ': ' + ('OK' if output else 'EMPTY'))
    except Exception as exc:
        print('LiveKit LLM: FAILED (' + type(exc).__name__ + ')')
    finally:
        await model.aclose()
    speech = cartesia.TTS(model='sonic-3', voice=settings.voice_id)
    try:
        size = 0
        async with speech.synthesize('Hello. Your sales assistant is ready.') as stream:
            async for event in stream:
                size += len(event.frame.data)
        print('Cartesia Sonic-3: ' + ('OK' if size else 'EMPTY'))
    except Exception as exc:
        print('Cartesia: FAILED (' + type(exc).__name__ + ')')
    finally:
        await speech.aclose()

async def run() -> None:
    async with utils.http_context.open():
        await main()


if __name__ == '__main__':
    asyncio.run(run())
