import os
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, cli, inference
from livekit.plugins import cartesia, deepgram, silero

from config import Settings

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
os.environ.setdefault('LIVEKIT_LOG_LEVEL', 'info')
settings = Settings.from_env(os.environ)
server = AgentServer()


@server.rtc_session(agent_name=settings.agent_name)
async def entrypoint(ctx: JobContext) -> None:
    session = AgentSession(
        stt=deepgram.STT(model='nova-3', language='en'),
        llm=inference.LLM(model=settings.llm_model),
        tts=cartesia.TTS(model='sonic-3', voice=settings.voice_id),
        vad=silero.VAD.load(),
        turn_handling={
            'turn_detection': 'vad',
            'interruption': {'enabled': True, 'mode': 'vad'},
            'endpointing': {'min_delay': 0.5, 'max_delay': 3.0},
        },
    )
    await session.start(
        room=ctx.room,
        record=False,
        agent=Agent(instructions=(ROOT / 'prompt.md').read_text()),
    )
    await session.generate_reply(
        instructions='Greet the user, identify yourself as an AI sales assistant in a demo, '
        'and ask what their business sells. Keep it brief.'
    )


if __name__ == '__main__':
    cli.run_app(server)
