# Experiments

This folder keeps the BenchBench run history. The headline evidence is now the
two five-model sweeps: Experiment 003 and Experiment 004. Experiments 001 and
002 are historical support: useful for provenance and prompt evolution, but not
the main result.

## Current Evidence

### Full 6x6 result set

The complete current result set is reconstructed from the two five-model
sweeps plus Claude Opus extension runs:

- `result_grids_6x6_20260523.md`: full tables and SVG heatmaps.
- `feedback_for_next_full_6x6_sweep_20260523.md`: the feedback packet to use
  for the next all-model creator sweep.

Read each grid as creator rows by solver columns. Cell values are exact-match
scores out of 30. High scores mean the benchmark was easy; low nonzero scores
are the useful signal; all-zero rows need audit before they count as hard.

The key result is stable after adding Claude Opus: Reimbursement Forensics is
the only current candidate where every tested solver lands in the low nonzero
band. The two Claude-created benchmarks are valid packages, but both are too
easy once tested against the full solver set.

### Claude Opus extensions

Claude Opus was added after the two five-model sweeps.

Creator runs:

| run | benchmark | full solver result | result |
|---|---|---|---|
| `005_claude_opus_exp003_style_20260523_125019` | String Rewriting Distance | 0/30, 0/30, 30/30, 30/30, 30/30, 30/30 | scorer type artifact; otherwise saturated |
| `006_claude_opus_feedback_style_20260523_125611` | Conlang Rosetta | 30/30, 30/30, 30/30, 30/30, 30/30, 30/30 | saturated |

The full solver result order is GPT-5.2, GPT-5.4, GPT-5.5, Gemini 3.1 Pro,
Gemini 3.5 Flash, Claude Opus.

Solver extension:

| source run | notable Claude Opus result |
|---|---|
| Experiment 003 | 11/30 on Ledger Canonical Reconciliation; 30/30 on the other four |
| Experiment 004 | 11/30 on Reimbursement Forensics, 25/30 on release_packet_arbitration, 30/30 on MFN-Cascade, operational 0/30 on Corrupted LZ77 Recovery; Cross-Document Obligation Resolution skipped because it was already audited as a scoring-contract failure |

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
