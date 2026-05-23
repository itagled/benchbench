# Feedback For Claude Opus Second Creator Run

This feedback is given to Claude Opus after its first BenchBench creator run
and after the existing Experiment 003/004 results.

BenchBench is evaluating benchmark invention. The goal is not to make an
impossible task. The goal is to create a complete benchmark package that is
valid, reproducible, externally solvable in principle, and still hard after
strong tool-enabled solvers attack the public solver bundle.

## Existing Experiment 003 Result

All five creator models produced structurally valid benchmark packages, but
every fresh candidate was rejected because at least one strong solver got
30/30.

| creator | generated benchmark | max solver result |
|---|---|---:|
| GPT-5.2 | Ledger Canonical Reconciliation | 30/30 |
| GPT-5.4 | Patchwork Ordinance Adjudication | 30/30 |
| GPT-5.5 | Amendment Ledger Reconciliation | 30/30 |
| Gemini 3.1 Pro | Polyhedral Surface Traversal | 30/30 |
| Gemini 3.5 Flash | Mutative Assembly Inversion | 30/30 |

The useful signal was model-specific weakness, not a new accepted benchmark.
The maximum solver score was still perfect for every row.

## Claude Opus First Creator Result

Claude Opus created **String Rewriting Distance** in
`experiments/005_claude_opus_exp003_style_20260523_125019`.

The package passed controller validation:

- gold control: 30/30
- shifted-wrong control: 0/30
- leak scan matches: 0

But Claude Opus then solved its own public solver bundle at 30/30. The
candidate is therefore too easy under the current gate.

The main failure mode was that the public bundle made the right abstraction
too direct: it defined a finite shortest-path problem and even described a
reference BFS approach. Strong tool-enabled solvers can implement or adapt BFS
and recover all answers. Do not build another benchmark where the intended
solution is a single obvious search/simulation algorithm over fully normalized
data.

## Existing Experiment 004 Result

Experiment 004 gave creators the Experiment 003 failure report. It produced one
stronger current candidate and several instructive failures.

| creator | generated benchmark | result |
|---|---|---|
| GPT-5.2 | Reimbursement Forensics | best current candidate; solvers scored 10/30 to 14/30 |
| GPT-5.4 | release_packet_arbitration | mostly too easy; max 27/30 |
| GPT-5.5 | Cross-Document Obligation Resolution | scoring-contract failure, not a keeper |
| Gemini 3.1 Pro | Corrupted LZ77 Recovery | solvable but narrow/operationally brittle; max 22/30 |
| Gemini 3.5 Flash | MFN-Cascade | too easy; 30/30 for every solver |

Post-run audit found that GPT-5.5's all-zero row was not a clean hard
benchmark. Solvers recovered all 30 notification dates, but the scorer required
private exact strings for `evidence_codes` and categorical values that were not
enumerated in the public packet. This is a scoring-contract failure.

The LZ77 benchmark was not unsolvable because two solvers recovered many
answers, but it may be too narrow: it rewards writing a specialized recovery
algorithm and caused operational blank-output/time-out failures.

## What To Do Differently

Do not merely scale up a finite search, exact simulator, or clean parser.
Strong solvers are good at writing scripts, brute-forcing small finite spaces,
parsing rule files, and implementing direct simulations when the abstraction is
obvious.

Try to design a benchmark where the public evidence is complete but successful
solvers must combine several hard-to-automate capabilities:

- precise interpretation of messy but finite specifications;
- adversarial edge cases that punish shallow heuristics;
- cross-document consistency checks;
- public ambiguity that can be resolved by evidence, not private intent;
- multi-stage inference where the useful intermediate representation is not
  obvious;
- enough diversity across the 30 items that one brittle script does not solve
  all of them.

The benchmark still must be fair. It must not depend on hidden generator logic,
private seeds, private answer keys, impossible research problems, or arbitrary
author intent. In `validation_report.md`, explain why the public solver bundle
is sufficient for an external solver in principle and what evidence proves each
answer.

A better candidate is one where weak baselines fail, strong solvers cannot get
near-perfect scores in one pass, and at least some answers remain recoverable
so the task is not simply under-specified.
