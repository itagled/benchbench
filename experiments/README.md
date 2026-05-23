# Experiments

This folder keeps the BenchBench run history. The headline evidence is now the
two five-model sweeps: Experiment 003 and Experiment 004. Experiments 001 and
002 are historical support: useful for provenance and prompt evolution, but not
the main result.

## Current Evidence

### `003_five_model_sweep_20260522_195526`

The first full 5x5 run across GPT-5.2, GPT-5.4, GPT-5.5, Gemini 3.1 Pro, and
Gemini 3.5 Flash. It established that the full Codex plus Antigravity creator
and solver harness worked, but all fresh candidates were solved at 30/30 by at
least one strong solver.

### `004_feedback_sweep_20260522_225208`

The feedback-driven 5x5 run. Creator models saw the Experiment 003 failure
report and were asked to build a benchmark that survived those solver
strategies.

Headline:

| creator | benchmark | result |
|---|---|---|
| GPT-5.2 | Reimbursement Forensics | best current candidate; audit next |
| GPT-5.4 | release_packet_arbitration | mostly too easy |
| GPT-5.5 | Cross-Document Obligation Resolution | scoring-contract failure |
| Gemini 3.1 Pro | Corrupted LZ77 Recovery | solvable but narrow/operationally brittle |
| Gemini 3.5 Flash | MFN-Cascade | too easy |

## Historical Support

### `001_three_model_grid_pilot`

The first complete 3-model grid. It is worth keeping because it showed the
visual/topology attractor in early prompts.

Headline:

| creator | benchmark | result |
|---|---|---|
| GPT-5.2 | Folded Strip Order | too easy |
| GPT-5.4 | Occluded Tile Provenance | difficulty pass in this pilot |
| GPT-5.5 | Shadow Weave Topology | too easy |

### `002_broad_sweep_20260515_220653`

The first broad prompt 3-model sweep. It is worth keeping because it produced
three qualitatively different benchmark families without explicit domain
steering. It also became the first fixed reference set for adding Gemini solver
columns.

Headline:

| creator | benchmark | result |
|---|---|---|
| GPT-5.2 | IgnoreSense | hard under tested solvers; novelty not established |
| GPT-5.4 | Spectrum Assembly | too easy |
| GPT-5.5 | Protocol Archaeology | all-zero warning; solvability unresolved |

## Development Archive

`000_development_archive` keeps notes from earlier prompt iterations. Generated
run payloads from that phase are not canonical.

## Cleanup Policy

For canonical runs, keep:

- summary and assessment markdown;
- manifests;
- creator prompts and outputs;
- candidate benchmark packages;
- score JSONs and solver predictions.

Generated isolated solver working directories may be deleted after the
corresponding predictions and score files are preserved.
