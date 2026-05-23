# BenchBench

BenchBench evaluates models as benchmark inventors.

The aim is not to make a task that frontier models fail. That is easy to do
badly. The aim is to make a benchmark package that is valid, reproducible,
human-auditable, externally solvable in principle, and still hard after strong
tool-enabled solvers attack it.

BenchBench is the system. Individual generated benchmarks are candidates inside
that system. There is not yet a final promoted stable bank.

## Current Answer

The strongest current candidate is **Reimbursement Forensics**, created by
GPT-5.2 in the feedback-driven sweep. All six tested solvers scored in the low
nonzero band, from **10/30 to 14/30**. That is the shape BenchBench is looking
for: not saturated, not all-zero, and not obviously unknowable.

That does not make it accepted yet. It still needs a human/audit pass for
leakage, answer evidence, and external solvability before promotion.

| Question | Current read |
|---|---|
| Best current candidate | Reimbursement Forensics |
| Best benchmark creator so far | GPT-5.2, because it produced the only current all-solver low-nonzero candidate |
| Claude Opus as creator | No keeper in two attempts; both created tasks saturated or had a scorer artifact |
| Claude Opus as solver | Strengthened the Reimbursement Forensics result with 11/30 |
| Main failure mode | Benchmarks were too easy, under-specified, or operationally brittle |
| Next move | Run a new full creator sweep using the current 6x6 failure report |

## Current 6x6 Results

The current result set is reconstructed: the two original five-model sweeps
plus Claude Opus creator and solver extensions added afterward.

Full tables and notes:
[`experiments/result_grids_6x6_20260523.md`](experiments/result_grids_6x6_20260523.md)

![Exp003-style 6x6 creator/solver grid](experiments/figures/exp003_style_6x6_heatmap.svg)

![Feedback-style 6x6 creator/solver grid](experiments/figures/exp004_feedback_6x6_heatmap.svg)

Read the heatmaps row-first. Rows are benchmark creators. Columns are solvers.
Cells are exact-match scores out of 30.

Red is not good here: it means the benchmark saturated and was easy for that
solver. Blue is the promising band: low but nonzero. Gray zeros need audit,
because they can mean an under-specified public packet, a scoring-contract
failure, or an operational failure.

## What We Learned

- Feedback helped. Experiment 003 produced no keeper: every fresh benchmark was
  solved 30/30 by at least one strong solver. Experiment 004 produced
  Reimbursement Forensics, where every solver got some answers but no solver
  got close to saturation.
- All-zero scores are not automatically good. Cross-Document Obligation
  Resolution looked hard in the grid, but the audit showed solvers recovered
  the core dates and were zeroed by hidden answer-vocabulary choices.
- Claude Opus did not change the headline result. It did not create a stronger
  benchmark in these two attempts, but as a solver it confirmed that
  Reimbursement Forensics remains low-nonzero.
- Most generated benchmarks still fail the acceptance gate. They are often
  formal and plausible, but collapse once a strong solver finds the right
  search, parsing, or simulation strategy.
- The useful claim is narrow: BenchBench is a harness for testing benchmark
  invention. It has one strong candidate for audit, not a finished benchmark
  bank.

## How It Works

Each sweep is a creator-by-solver matrix.

1. Creator models build complete benchmark packages.
2. The controller validates generation, scoring, solver-bundle isolation, and
   obvious leakage.
3. Solver models receive only the public `solver_bundle/` and try to answer all
   30 items.
4. Scores are computed against private gold answers.
5. Results are interpreted conservatively: too easy, all-zero, under-specified,
   brittle, or worth audit.

Creator models can receive prior-run feedback when the sweep passes a feedback
file. Solver models do not receive prior results. They are intentionally blind
to everything except the isolated public bundle for the candidate they are
solving.

For the full process, package contract, and acceptance rules, see
[`docs/methodology.md`](docs/methodology.md).

## Run The Next Sweep

Use the current full feedback packet:

```bash
BENCHBENCH_CLAUDE_MAX_BUDGET_USD=25 python run_broad_three_model_sweep.py \
  --feedback-context experiments/feedback_for_next_full_6x6_sweep_20260523.md \
  --models gpt-5.2 gpt-5.4 gpt-5.5 agy:gemini-3.1-pro agy:gemini-3.5-flash-high claude:opus
```

To add a solver to an existing saved run:

```bash
python run_existing_solver_extension.py \
  --run-root experiments/004_feedback_sweep_20260522_225208 \
  --solver claude:sonnet
```

More commands and backend notes are in [`docs/running.md`](docs/running.md).

## Main Artifacts

- [`experiments/result_grids_6x6_20260523.md`](experiments/result_grids_6x6_20260523.md):
  reconstructed 6x6 grids and heatmaps.
- [`experiments/feedback_for_next_full_6x6_sweep_20260523.md`](experiments/feedback_for_next_full_6x6_sweep_20260523.md):
  feedback packet for the next all-model creator sweep.
- [`experiments/003_five_model_sweep_20260522_195526/`](experiments/003_five_model_sweep_20260522_195526/):
  first five-model creator/solver sweep.
- [`experiments/004_feedback_sweep_20260522_225208/`](experiments/004_feedback_sweep_20260522_225208/):
  feedback-driven five-model sweep and current headline evidence.
- [`experiments/claude_opus_extension_20260523.md`](experiments/claude_opus_extension_20260523.md):
  Claude Opus creator and solver extension summary.
- [`benchmark_landscape/`](benchmark_landscape/):
  researched eval catalog, score matrix, and similarity method.

## Repo Map

- `run_broad_three_model_sweep.py`: creator/solver sweep harness.
- `run_existing_solver_extension.py`: add solver columns to saved runs.
- `run_broad_xhigh_sanity.py`: high-effort solver sanity harness.
- `benchbench_model_backends.py`: Codex, Antigravity, and Claude Code backend
  dispatch.
- `benchbench_results.py`: shared score, JSONL, candidate-title, and prediction
  parsing helpers.
- `scripts/build_6x6_result_artifacts.py`: regenerates the 6x6 markdown and
  SVG heatmaps.
- `scripts/score_benchmark_similarity.py`: similarity/novelty smoke-check path.
