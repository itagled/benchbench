# BenchBench

BenchBench tests whether models can design good benchmarks for other models.

A creator model writes a complete benchmark package: public solver files,
private gold answers, generator, verifier, scorer, and notes on expected
failure modes. Solver models then receive only the public bundle and try to
answer all 30 items.

The goal is a benchmark that strong agents can work on, score exactly, and
still fail to finish.

## Current Read

**GPT-5.2 is the strongest benchmark creator so far.**

Its best candidate, **Reimbursement Forensics**, scored **10/30, 14/30, 11/30,
12/30, 11/30, and 11/30** across GPT-5.2, GPT-5.4, GPT-5.5, Gemini 3.1 Pro,
Gemini 3.5 Flash, and Claude Opus.

Every solver found some answers. None came close to finishing. The row stayed
hard across six different solver models.

Round 3 produced two interesting challengers:

- **Commercial Lease CAM Reconciliation**, from Gemini 3.1 Pro, spread solvers
  from 1/30 to 26/30.
- **Maritime Freight & Customs Audit**, from Gemini 3.5 Flash, spread solvers
  from 4/30 to 25/30.

Both created real separation. Reimbursement Forensics still leads because all
six solvers landed in the low nonzero band.

![Canonical Round 3 6x6 heatmap](experiments/canonical/figures/canonical_round3_6x6_heatmap.svg)

## Strongest Benchmarks So Far

| read | benchmark | creator | score shape | what it shows |
|---|---|---|---|---|
| Current leader | Reimbursement Forensics | GPT-5.2 | 10-14/30 across all six solvers | The cleanest hard-but-solvable shape so far. |
| Round 3 challenger | Commercial Lease CAM Reconciliation | Gemini 3.1 Pro | 1-26/30 | Strong solver separation, with the top end still too high. |
| Round 3 challenger | Maritime Freight & Customs Audit | Gemini 3.5 Flash | 4-25/30 | Strong solver separation, again with too much top-end completion. |
| Diagnostic row | Corrupted LZ77 Recovery | Gemini 3.1 Pro | 0-22/30 | Useful stress signal, narrower and more brittle than the leaders. |

## Where The Hardness Came From

The strongest candidates looked like paperwork forensics: reimbursement claims,
leases, freight records, service credits, royalties, prior authorization, and
construction payments.

They worked because each item had visible evidence, exact answers, and several
small rules interacting at once. Solvers had to track dates, exceptions,
arithmetic, thresholds, and rounding under one record.

GPT-5.2 did this best. Reimbursement Forensics used ordinary evidence, exact
totals, and enough exception handling to slow every solver.

Gemini 3.1 Pro and Gemini 3.5 Flash found the best Round 3 challenger surfaces,
especially leases and freight. Their tasks separated solvers, but top solvers
completed too much.

GPT-5.4 and GPT-5.5 built plausible operational tasks. The strongest solvers
often turned them into checklist work.

Claude Opus built clean contest-style packages. In these runs, that cleanliness
made them easier to solve.

## Completion Proxy

Completion rate is the average exact-match score across solvers. It needs a
companion metric: how many solvers landed in the useful 1-14/30 band.

![Benchmark quality map](experiments/canonical/figures/benchmark_quality_map.svg)

Reimbursement Forensics has the desired shape: 38% average completion and six
useful low-nonzero solver cells. Commercial Lease CAM and Maritime Freight sit
farther right: they separated solvers, while the best solvers completed too
much. Service Credit and Cross-Document Obligation sit at the bottom left:
low completion with no useful solver cells.

## What BenchBench Measures

BenchBench turns model evaluation into a design problem.

A strong creator has to choose a task, package the evidence, define exact
answers, hide the gold data, and build a scorer that rewards the intended work.
Then strong solvers attack it with tools.

That makes BenchBench useful for a different question from ordinary evals:
which model understands failure well enough to write the next hard test?

The current answer is GPT-5.2. The next run asks whether another model can learn
from these results and beat Reimbursement Forensics.

## Reading The Grids

Rows are benchmark creators. Columns are solvers. Cells are exact-match scores
out of 30.

- High scores mean the benchmark was too easy.
- Low nonzero scores are the target band.
- Zero-heavy rows go to review, since they often point to a packet or scorer
  problem rather than useful difficulty.

Canonical grids and notes:
[`experiments/canonical/README.md`](experiments/canonical/README.md)

The canonical results page also includes the round-by-round creator trajectory,
the latest solver leaderboard, and Round 3 matchup summaries.

## Next Challenger Sweep

First review the known scorer and solvability problem cases:
[`experiments/review_queue.md`](experiments/review_queue.md)

Then run a challenger sweep. GPT-5.2 keeps the Reimbursement Forensics incumbent
row. The other creators try to beat it against the full six-model solver panel.

```bash
BENCHBENCH_CLAUDE_MAX_BUDGET_USD=25 python run_broad_three_model_sweep.py \
  --feedback-context experiments/feedback_for_next_challenger_sweep_20260523.md \
  --creator-models gpt-5.4 gpt-5.5 agy:gemini-3.1-pro agy:gemini-3.5-flash-high cursor:claude-opus \
  --solver-models gpt-5.2 gpt-5.4 gpt-5.5 agy:gemini-3.1-pro agy:gemini-3.5-flash-high cursor:claude-opus
```

Use `--models` for a symmetric sweep where creator and solver panels are the
same.

## Evidence

- [`experiments/canonical/README.md`](experiments/canonical/README.md):
  current presentation-layer 6x6 grids and heatmaps.
- [`experiments/benchmark_bank.md`](experiments/benchmark_bank.md): current
  target, diagnostic rows, problem cases, and rejected candidates.
- [`experiments/007_full_feedback_6x6_20260523_172919/`](experiments/007_full_feedback_6x6_20260523_172919/):
  raw latest direct six-creator, six-solver challenger sweep.
- [`experiments/004_feedback_sweep_20260522_225208/`](experiments/004_feedback_sweep_20260522_225208/):
  source run for Reimbursement Forensics.
- [`benchmark_landscape/`](benchmark_landscape/): eval catalog and similarity
  notes used as creator context.

## Method

Full process: [`docs/methodology.md`](docs/methodology.md)

Commands and backend notes: [`docs/running.md`](docs/running.md)

In short:

1. Creators build complete benchmark packages.
2. The controller validates generation, scoring, public/private isolation, and
   obvious leakage.
3. Solvers receive only the public `solver_bundle/`.
4. Scores are computed against private gold answers.
5. Candidates become leaders, challengers, diagnostics, or rejections.

## Repo Map

- `run_broad_three_model_sweep.py`: creator/solver sweep harness.
- `run_existing_solver_extension.py`: add solver columns to saved runs.
- `benchbench_model_backends.py`: model backend dispatch.
- `benchbench_results.py`: shared score and prediction parsing helpers.
- `scripts/build_6x6_result_artifacts.py`: result grids and SVG heatmaps.
- `scripts/score_benchmark_similarity.py`: similarity/novelty smoke check.
