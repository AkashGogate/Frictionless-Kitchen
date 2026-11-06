# ARCHITECTURE.md

## 1. Why hosting choice is a correctness issue
The agent needs a persistent, bidirectional, low-latency audio stream (Pipecat over WebRTC, Deepgram STT in the loop). Serverless functions (Vercel-style) have execution timeouts built for request/response, not held-open streaming — they'll work in short tests and die mid-session the first time someone holds a connection open past the timeout.

**Decision:**
- Agent runtime: a persistent-connection host — Pipecat Cloud/Daily's own hosting, or Fly.io, Render, or AWS Fargate/EC2.
- Static frontend: Vercel is fine — it only bootstraps the client, not the real-time stream.

## 2. Public demo surface — requirements
- 2.1 Abuse/cost exposure: per-session time cap, rate limit per IP/session, an easy kill switch.
- 2.2 Live-demo fallback: the demo UI must offer both "Use your own mic" (real live path) and "Play a test scenario" (pre-recorded, pre-validated clips through the same pipeline).

## 3. Data flow (v1)
```
[Kitchen mic/array] -> [Pipecat pipeline: turn-detection/diarization]
   -> [Deepgram STT: live transcript per speaker turn]
   -> [Call-parsing layer: structured order-line object]
   -> [Mismatch detector vs. active ticket queue]
        -> (mismatch) -> [alert: TTS back to line + kitchen display]
   -> [Structured log store: timestamped, speaker-attributed]
```

## 4. Noise-robustness — the actual hard problem
Everything upstream of call-parsing must tolerate overlapping/simultaneous calls, sustained noise beds, and short/shouted/truncated utterances.

## 5. Contribution angle
Scope at least one piece as a real example or small PR against the Pipecat repo.

## 6. Session/abuse controls (implemented in backend/app/session.py)
- `MAX_SESSION_SECONDS` hard cap per session, enforced server-side.
- Per-IP concurrent-session limit.
- A single `kill()` call tears down any session's pipeline immediately.
