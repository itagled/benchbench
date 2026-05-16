# BenchBench

BenchBench is an experiment in evaluating models as benchmark inventors.

The object is not simply to make a task that frontier models fail. The object
is to make a benchmark package that is valid, reproducible, human-auditable,
hard under strong solver attempts, and useful as a measurement axis.

## Core Loop

1. A creator model builds a complete benchmark package.
2. The package is validated for generation, solver-bundle isolation, scoring,
   and leakage.
3. Solver models attack the public solver bundle with tools.
4. Easy benchmarks are rejected.
5. Benchmarks must be externally solvable in principle from the public solver
   bundle; impossible, under-specified, or private-keyed tasks do not count.
6. Benchmarks that nobody can solve are flagged for solvability audit, not
   automatically accepted.
7. Surviving candidates are compared against existing evals using rank
   correlations and regression predictability.

BenchBench itself is the system. Individual generated benchmarks are candidate
artifacts inside that system; there is no single "current live candidate."

## Current Results

We have run two small 3x3 creator/solver sweeps through Codex. In each row, the
creator model built a benchmark package and the solver models tried to solve
the public solver bundle.

### Experiment 001: Visual/Topology-Attracted Pilot

This first complete grid was useful, but the creator prompt was influenced by
an earlier visual-trace success and pulled models toward visual/topology tasks.

| creator | generated benchmark | solver GPT-5.2 | solver GPT-5.4 | solver GPT-5.5 | status |
|---|---|---:|---:|---:|---|
| GPT-5.2 | Folded Strip Order | 16/30 | 14/30 | 19/30 | too easy |
| GPT-5.4 | Occluded Tile Provenance | 7/30 | 4/30 | 5/30 | difficulty pass in pilot |
| GPT-5.5 | Shadow Weave Topology | 15/30 | 24/30 | 26/30 | too easy |

Extra sanity check: GPT-5.5 at `xhigh` scored 10/30 on Occluded Tile
Provenance.

### Experiment 002: Broad Creator Prompt Sweep

The second 3x3 sweep removed the visual/domain nudge. Creators saw benchmark
landscape notes and the prior pilot, but were asked in broad terms to make the
best benchmark package they could.

| creator | generated benchmark | benchmark type | solver GPT-5.2 | solver GPT-5.4 | solver GPT-5.5 | status |
|---|---|---|---:|---:|---:|---|
| GPT-5.2 | IgnoreSense | `.gitignore` semantics / software spec following | 4/30 | 7/30 | 7/30 | hard under tested solvers; novelty unmeasured |
| GPT-5.4 | Spectrum Assembly | constrained string reconstruction | 30/30 | 30/30 | 30/30 | too easy |
| GPT-5.5 | Protocol Archaeology | trace-based byte-protocol inference | 0/30 | 0/30 | 0/30 | hard under tested solvers; solvability unresolved |

Extra GPT-5.5 `xhigh` sanity checks:

| benchmark | GPT-5.5 xhigh |
|---|---:|
| IgnoreSense | 7/30 |
| Protocol Archaeology | 0/30 |

Protocol Archaeology also has two specialist baseline scores at 0/30. That is
not a final rejection, but it is a warning: all-zero scores may indicate that
the public packet is under-specified rather than that the benchmark found a
deep missing capability. It needs a separate solvability and identifiability
audit.

## What We Think We Learned

- The broad prompt is better than the visual-attractor prompt: it produced
  software-spec, combinatorial, and trace-inference benchmarks instead of three
  visual puzzles.
- A benchmark can fail by being too easy: Spectrum Assembly looked formal, but
  every solver got 30/30 once the right search abstraction was obvious.
- A benchmark can also fail by being too unknowable: Protocol Archaeology may
  be private-keyed or under-specified from the solver packet.
- The right acceptance gate is not "frontier model got less than 50%." It is:
  externally solvable, well-specified, reproducible, hard under strong solver
  attempts, and then useful as a measurement axis.
- Similarity/novelty still needs more model coverage. The current data is
  enough for a smoke test, not a serious regression claim.

## Current Useful Artifacts

- `benchmark_landscape/`: researched eval catalog, public score tables, model
  score matrix, and similarity method.
- `run_broad_three_model_sweep.py`: creator/solver sweep harness.
- `run_broad_xhigh_sanity.py`: extra high-effort solver sanity harness.
- `experiments/001_three_model_grid_pilot/`: first 3-model grid pilot.
- `experiments/002_broad_sweep_20260515_220653/`: broad prompt 3-model sweep.

## Running A Sweep

```bash
python run_broad_three_model_sweep.py
```

The creator prompt reads `benchmark_landscape/creator_prompt_landscape_pack.md`
when present, plus the Experiment 001 pilot summary.

## Similarity / Novelty Check

```bash
python scripts/score_benchmark_similarity.py \
  --target-benchmark benchbench_ignoresense \
  --out benchmark_landscape/similarity_ignoresense_smoke.md
```

The current local solver set is too small for serious regression novelty
claims. The method is ready; the data is not yet broad enough.
