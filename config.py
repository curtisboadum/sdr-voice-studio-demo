from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    llm_model: str
    voice_id: str
    agent_name: str

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> 'Settings':
        required = ('LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET',
                    'DEEPGRAM_API_KEY', 'CARTESIA_API_KEY')
        missing = [name for name in required if not env.get(name)]
        if missing:
            raise ValueError('Missing environment variables: ' + ', '.join(missing))
        if not env['LIVEKIT_URL'].startswith('wss://'):
            raise ValueError('LIVEKIT_URL must start with wss://')
        model = env.get('LLM_MODEL', env.get('OPENAI_MODEL', 'gpt-4o-mini'))
        if '/' not in model:
            model = 'openai/' + model
        return cls(model, env.get('CARTESIA_VOICE_ID', 'f786b574-daa5-4673-aa0c-cbe3e8534c02'),
                   env.get('AGENT_NAME', 'ai-sdr'))
