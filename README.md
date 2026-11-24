# SDR Voice Studio

A local browser demo for testing a voice agent in a two-way conversation. The source includes the Python voice worker and Next.js interface, but no accounts, transcripts, credentials, or operational history.

**Audio path:** browser microphone → LiveKit → Deepgram Nova-3 → GPT-4o-mini via LiveKit Inference → Cartesia Sonic-3 → browser speaker. Silero detects speech and supports interruption.

## What to look at

- [`agent.py`](agent.py) assembles the voice pipeline and loads the generic demo brief.
- [`web/app/page.tsx`](web/app/page.tsx) is the browser studio.
- [`web/app/api/connect/route.ts`](web/app/api/connect/route.ts) creates a short-lived token for a single test room. It is disabled in production.
- [`tests/`](tests/) covers configuration and the local session endpoint.

## Run locally with your own test accounts

Requires Python 3.13, uv, and Node.js 20.9+. Run from the repository root:

```sh
uv venv --python 3.13
uv pip install --python .venv/bin/python -r requirements.lock.txt
cp .env.example .env
cp web/.env.example web/.env.local
cd web && npm ci
```

Populate the example variables in the two local environment files. Match the LiveKit credentials and agent name. Deepgram and Cartesia require their respective credentials; the model runs through LiveKit Inference.

Start the worker with `.venv/bin/python agent.py dev` from the root. In a second terminal, run `cd web && npm run dev`, open `http://127.0.0.1:3000`, and allow microphone access. Use fictional inputs only: a real test processes audio through configured providers and can incur usage charges.

## Verify without provider calls

```sh
.venv/bin/python -m unittest discover -s tests -p test_config.py
```

The local HTTP regression tests also require the development server. `check_services.py` and `test_room.py` exercise actual provider services and are not needed to review the code.

## Limits

This is a local prototype, not a public voice service. It does not dial a phone, record calls, qualify live prospects, book meetings, or connect to a CRM. Do not host the development endpoint publicly. No third-party dependency is relicensed by this repository.
