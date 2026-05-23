# BenchBench

BenchBench tests whether models can invent good benchmarks.

A good BenchBench candidate is not merely a task that frontier models fail. It
must be valid, reproducible, human-auditable, externally solvable in principle,
and still hard after strong tool-enabled solvers attack the public evidence.

BenchBench is the harness. Generated benchmarks are candidates inside it. There
is not yet a promoted stable benchmark bank.

## Current Status

One candidate is worth auditing next: **Reimbursement Forensics**.

It was created by GPT-5.2 in the feedback-driven sweep. All six tested solvers
scored between **10/30 and 14/30**. That is the shape BenchBench wants: low
nonzero scores across strong solvers, rather than saturation or an all-zero
row.

It is not accepted yet. Promotion would require a human/audit pass for leakage,
answer evidence, and external solvability.

## Result Grids

Full tables and notes:
[`experiments/result_grids_6x6_20260523.md`](experiments/result_grids_6x6_20260523.md)

![Exp003-style 6x6 creator/solver grid](experiments/figures/exp003_style_6x6_heatmap.svg)

![Feedback-style 6x6 creator/solver grid](experiments/figures/exp004_feedback_6x6_heatmap.svg)

Read rows as benchmark creators and columns as solvers. Cells are exact-match
scores out of 30.

Red means the benchmark saturated and was too easy. Blue is the useful band:
the solver found some answers but did not solve the benchmark. Gray zeros need
audit before they count as hard, because they can also mean an under-specified
public packet, a scoring-contract failure, or an operational failure.

## What The Results Say

- The first five-model sweep did not produce a keeper. Every fresh candidate
  was solved 30/30 by at least one strong solver.
- The feedback sweep was better. It moved the search from saturated rows to one
  audit-worthy low-nonzero row.
- All-zero rows are warnings, not wins. One all-zero row turned out to be a
  hidden answer-contract problem: solvers found the core dates but were zeroed
  by private vocabulary choices.
- Most failures are still mundane: too easy, under-specified, or operationally
  brittle.

## How It Works

Each sweep is a creator-by-solver matrix.

1. Creator models build complete benchmark packages.
2. The controller validates generation, scoring, solver-bundle isolation, and
   obvious leakage.
3. Solver models receive only the public `solver_bundle/`.
4. Scores are computed against private gold answers.
5. Results are interpreted conservatively: too easy, all-zero, under-specified,
   brittle, or worth audit.

Creator models can receive prior-run feedback when the sweep passes a feedback
file. Solver models do not receive prior results.

Full process details:
[`docs/methodology.md`](docs/methodology.md)

## Run The Next Sweep

Give every creator model the current failure report and ask for a benchmark
that beats these results:

```bash
BENCHBENCH_CLAUDE_MAX_BUDGET_USD=25 python run_broad_three_model_sweep.py \
  --feedback-context experiments/feedback_for_next_full_6x6_sweep_20260523.md \
  --models gpt-5.2 gpt-5.4 gpt-5.5 agy:gemini-3.1-pro agy:gemini-3.5-flash-high claude:opus
```

More commands and backend notes:
[`docs/running.md`](docs/running.md)

## Evidence

- [`experiments/result_grids_6x6_20260523.md`](experiments/result_grids_6x6_20260523.md):
  reconstructed 6x6 grids and heatmaps.
- [`experiments/004_feedback_sweep_20260522_225208/`](experiments/004_feedback_sweep_20260522_225208/):
  feedback-driven five-model sweep and current headline evidence.
- [`experiments/003_five_model_sweep_20260522_195526/`](experiments/003_five_model_sweep_20260522_195526/):
  first five-model creator/solver sweep.
- [`experiments/`](experiments/):
  run history, extension notes, and feedback packets.
- [`benchmark_landscape/`](benchmark_landscape/):
  researched eval catalog, score matrix, and similarity method.

## Repo Map

- `run_broad_three_model_sweep.py`: creator/solver sweep harness.
- `run_existing_solver_extension.py`: add solver columns to saved runs.
- `benchbench_model_backends.py`: model backend dispatch.
- `benchbench_results.py`: shared score and prediction parsing helpers.
- `scripts/build_6x6_result_artifacts.py`: regenerates the 6x6 markdown and
  SVG heatmaps.
- `scripts/score_benchmark_similarity.py`: similarity/novelty smoke-check path.
