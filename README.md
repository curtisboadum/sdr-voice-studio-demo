# SDR Voice Studio

**A browser test bench for a real-time sales discovery agent.** Rehearse an inbound conversation with a fictional prospect and review how the agent asks questions, handles interruptions and responds when it doesn’t know the answer, before adding a phone line or CRM.

The demo pairs a **Next.js browser studio** with a **Python LiveKit worker**. The two pieces are small enough to follow from the Start button to the first spoken reply.

## Two-minute walkthrough

1. Select **Start a test conversation** and allow microphone access. The studio shows when the agent is listening, thinking or speaking.
2. Say: “We sell accounting software to small businesses. Most of our leads come from referrals.” The [demo brief](prompt.md) asks the agent to identify itself and ask one concise discovery question at a time.
3. Speak while the agent is answering to try the interruption path. Then ask “Can you book a meeting?” The intended behaviour is to explain that booking is unavailable rather than claim a meeting was booked.

These are scenarios to try, not benchmark results. The brief guides model behaviour; it does not guarantee what the model will say.

## How it works

```text
Browser microphone → LiveKit room → Python worker
                     Deepgram Nova-3 → GPT-4o-mini → Cartesia Sonic-3
Browser speaker    ← LiveKit room ← Synthesised reply
```

| Part | What to inspect |
| --- | --- |
| [Browser studio](web/app/page.tsx) | Requests a session, connects microphone and speaker audio, and renders assistant state and controls. |
| [Session endpoint](web/app/api/connect/route.ts) | Signs a 10-minute token scoped to one randomly named, two-participant room and specifies the named agent to dispatch. Rejects non-loopback hosts, present mismatched origins and production mode. Secrets stay on the server. |
| [Voice worker](agent.py) | Connects Deepgram speech-to-text, the default GPT-4o-mini model through LiveKit Inference, and Cartesia speech synthesis. Silero voice activity detection drives turn handling and interruptions. |
| [Brief and config](prompt.md) | The brief defines conversation boundaries; [config.py](config.py) validates required settings and resolves the model, voice and worker name. |

## Run locally

Requires **Python 3.13**, **uv** and **Node.js 20.9+**. From the repository root:

```sh
uv venv --python 3.13
uv pip install --python .venv/bin/python -r requirements.lock.txt
cp .env.example .env
cp web/.env.example web/.env.local
(cd web && npm ci)
```

Set `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` and `AGENT_NAME` consistently in both environment files. Add `DEEPGRAM_API_KEY` and `CARTESIA_API_KEY` to the root `.env`. The default model uses LiveKit Inference, so the LiveKit project must have access to it; no separate OpenAI key is used by the default setup.

Run these in **two terminals**, both starting in the repository root:

```sh
# Terminal 1: worker
.venv/bin/python agent.py dev

# Terminal 2: browser studio
cd web && npm run dev
```

Open [http://127.0.0.1:3000](http://127.0.0.1:3000). Use fictional inputs: a real session sends audio or text through the configured providers and can incur usage charges.

## Verify without provider calls

```sh
python3 -m unittest discover -s tests -p test_config.py -v
(cd web && npm run typecheck)
```

For the **local HTTP regression tests**, run the web server on port 3000. It only signs tokens for these tests, so placeholder nonempty LiveKit values are sufficient and no worker is needed:

```sh
# Terminal 1 (repository root)
cd web && LIVEKIT_URL=wss://example.invalid LIVEKIT_API_KEY=demo-key LIVEKIT_API_SECRET=demo-secret npm run dev

# Terminal 2 (repository root)
python3 -m unittest discover -s tests -p test_local_endpoint.py -v
```

The tests check same-origin loopback requests and reject external hosts, external origins and mismatched local origins. Stop the placeholder server before trying a real voice session.

The optional `.venv/bin/python check_services.py` makes provider requests. With the configured worker and studio both running, `.venv/bin/python test_room.py` exercises greeting audio, a synthetic caller turn and a spoken reply. Both can incur usage charges.

## Scope

The browser and token endpoint are for local development. The worker sets `record=False`; that setting does not describe provider retention. The prototype does not dial phone numbers, book meetings or write CRM records. The loopback checks are development safeguards, not a substitute for authentication and authorisation on a public service.
