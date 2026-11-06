# kitchen-copilot audio eval scorecard

Mode: **mock**  _(mock mode — proves the scoring harness, not the audio pipeline; see run_eval.py docstring)_

- Call-parse accuracy: **100%** (10/10 expected calls correctly extracted)
- False-trigger count: **0**
- Missed-call count: **0**
- Mean per-clip latency: **0.000s**

| Clip | Pass? | Missed | False triggers | Latency (s) |
|---|---|---|---|---|
| tc1_clean_single_call | ✅ | 0 | 0 | 0.000 |
| tc2_overlapping_two_stations | ✅ | 0 | 0 | 0.000 |
| tc3_three_simultaneous | ✅ | 0 | 0 | 0.000 |
| tc4_noise_bed_ramp | ✅ | 0 | 0 | 0.000 |
| tc5_truncated_shouted | ✅ | 0 | 0 | 0.000 |
| tc6_accented_speech | ✅ | 0 | 0 | 0.000 |
| tc7_false_trigger_chatter | ✅ | 0 | 0 | 0.000 |
