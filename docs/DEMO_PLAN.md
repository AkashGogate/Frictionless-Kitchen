# DEMO_PLAN.md

Where: frontend on Vercel (public link), backend/agent runtime on Fly.io (or Render/AWS) — a real persistent endpoint, not localhost-only.

## How the live interview demo runs
1. Open with the Coval scorecard, not the mic.
2. Narrate one specific failure-and-fix from the eval history.
3. Live, own mic: a simple clean fire call, proving the end-to-end path works.
4. Live, hard case: "play a test scenario" to run a noisy/overlapping clip through the same live pipeline.
5. Let the interviewer try it themselves on the same public link.

## Fallbacks if something breaks live
The test-scenario path exists precisely for a flaky mic/network moment; keep a short screen recording of a full successful run as the last resort.

## What not to do
Don't open with an unscripted live mic attempt; don't imply real POS/kitchen deployment if it hasn't happened.
