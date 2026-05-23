# Solver Extension: Claude Opus

Run root: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/004_feedback_sweep_20260522_225208`
Solver spec: `opus`
Provider: `claude`
Claude max budget per call: `$25`

| creator | benchmark | rows | score | accuracy | Claude cost | Claude cache read | returncode | actual model |
|---|---|---:|---:|---:|---:|---:|---:|---|
| gemini-3.1-pro | Corrupted LZ77 Recovery | 0 | 0/30 | 0.0 | None | 0 | stopped | Claude Opus |
| gemini-3.5-flash-high | MFN-Cascade | 30 | 30/30 | 1.0 | 0.66676475 | 327516 | 0 | Claude Opus |
| gpt-5.2 | Reimbursement Forensics (ReiFor) | 30 | 11/30 | 0.36666666666666664 | 0.52699475 | 259619 | 0 | Claude Opus |
| gpt-5.4 | release_packet_arbitration | 30 | 25/30 | 0.8333333333333334 | 0.71413425 | 280836 | 0 | Claude Opus |

Total reported Claude cost: `$1.9079`
