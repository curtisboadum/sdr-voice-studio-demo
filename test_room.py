"""Exercise the voice pipeline with synthetic speech in a disposable test room."""
import asyncio
import gc
import os
from pathlib import Path

import aiohttp
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import utils
from livekit.plugins import cartesia


async def main() -> None:
    load_dotenv(Path(__file__).with_name('.env'))
    async with aiohttp.ClientSession() as http:
        async with http.post('http://127.0.0.1:3000/api/connect', headers={'Origin': 'http://127.0.0.1:3000'}) as response:
            assert response.status == 200, 'Token endpoint failed'
            connection = await response.json()
        async with http.post('http://127.0.0.1:3000/api/connect', headers={'Origin': 'https://example.com'}) as response:
            assert response.status == 403, 'Cross-origin request was not rejected'
    room = rtc.Room()
    received_audio = asyncio.Event()
    greeting = asyncio.Event()
    heard_user = asyncio.Event()
    reply = asyncio.Event()
    tasks = []

    async def listen(track: rtc.RemoteAudioTrack) -> None:
        stream = rtc.AudioStream(track)
        try:
            async for event in stream:
                if any(event.frame.data):
                    received_audio.set()
        finally:
            await stream.aclose()

    @room.on('track_subscribed')
    def subscribed(track, publication, participant):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            tasks.append(asyncio.create_task(listen(track)))

    @room.on('transcription_received')
    def transcribed(segments, participant, publication):
        if participant is None:
            return
        for segment in segments:
            if not segment.final:
                continue
            if participant.identity == room.local_participant.identity:
                heard_user.set()
            elif heard_user.is_set():
                reply.set()
            else:
                greeting.set()

    try:
        await room.connect(connection['serverUrl'], connection['token'])
        source = rtc.AudioSource(24000, 1)
        track = rtc.LocalAudioTrack.create_audio_track('synthetic-microphone', source)
        await room.local_participant.publish_track(track, rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE))
        await asyncio.wait_for(received_audio.wait(), 40)
        await asyncio.wait_for(greeting.wait(), 20)
        await asyncio.sleep(7)  # Let the greeting finish before the synthetic prospect speaks.
        speech = cartesia.TTS(model='sonic-3', sample_rate=24000,
                              voice=os.getenv('CARTESIA_VOICE_ID', 'f786b574-daa5-4673-aa0c-cbe3e8534c02'))
        try:
            async with speech.synthesize('We sell accounting software to small businesses. Can you ask me a qualifying question?') as stream:
                async for event in stream:
                    await source.capture_frame(event.frame)
            silence = rtc.AudioFrame.create(24000, 1, 240)
            for _ in range(200):
                await source.capture_frame(silence)
            await source.wait_for_playout()
            await asyncio.wait_for(heard_user.wait(), 25)
            await asyncio.wait_for(reply.wait(), 25)
        finally:
            await speech.aclose()
            await source.aclose()
        print('PASS: room token and automatic agent dispatch')
        print('PASS: greeting audio, synthetic microphone → Deepgram → GPT-4o-mini → spoken reply')
        print('PASS: cross-origin token requests rejected')
    finally:
        await room.disconnect()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def run() -> None:
    async with utils.http_context.open():
        await main()
        gc.collect()

if __name__ == '__main__':
    asyncio.run(run())
