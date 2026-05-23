# Feedback For Next Full 6x6 BenchBench Sweep

This feedback is for the next creator sweep after the GPT, Gemini, and Claude
Opus runs through 2026-05-23.

BenchBench is evaluating benchmark invention. The goal is not to make an
impossible task. The goal is to create a complete benchmark package that is
valid, reproducible, externally solvable in principle, and still hard after
strong tool-enabled solvers attack the public solver bundle.

## Current Full Result Set

The current evidence is a reconstructed 6x6 set. The first five rows in each
grid came from the original five-model sweep. The Claude Opus row and Claude
Opus solver column were added afterward by extension runs.

### Exp003-style grid

| creator | benchmark | GPT-5.2 | GPT-5.4 | GPT-5.5 | Gemini 3.1 Pro | Gemini 3.5 Flash | Claude Opus |
|---|---|---:|---:|---:|---:|---:|---:|
| GPT-5.2 | Ledger Canonical Reconciliation | 11/30 | 30/30 | 30/30 | 30/30 | 30/30 | 11/30 |
| GPT-5.4 | Patchwork Ordinance Adjudication | 3/30 | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 |
| GPT-5.5 | Amendment Ledger Reconciliation | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 |
| Gemini 3.1 Pro | Polyhedral Surface Traversal | 30/30 | 6/30 | 30/30 | 30/30 | 30/30 | 30/30 |
| Gemini 3.5 Flash | Mutative Assembly Inversion | 30/30 | 30/30 | 30/30 | 30/30 | 22/30 | 30/30 |
| Claude Opus | String Rewriting Distance | 0/30 | 0/30 | 30/30 | 30/30 | 30/30 | 30/30 |

Every Exp003-style row is rejected. Each one is solved perfectly by at least
four solvers. Claude Opus's String Rewriting Distance is not a hard benchmark:
GPT-5.2 and GPT-5.4 returned the right integer values as JSON strings, and the
scorer rejected those type-mismatched answers.

### Feedback-style grid

| creator | benchmark | GPT-5.2 | GPT-5.4 | GPT-5.5 | Gemini 3.1 Pro | Gemini 3.5 Flash | Claude Opus |
|---|---|---:|---:|---:|---:|---:|---:|
| GPT-5.2 | Reimbursement Forensics | 10/30 | 14/30 | 11/30 | 12/30 | 11/30 | 11/30 |
| GPT-5.4 | release_packet_arbitration | 27/30 | 25/30 | 27/30 | 0/30 | 27/30 | 25/30 |
| GPT-5.5 | Cross-Document Obligation Resolution | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | skip |
| Gemini 3.1 Pro | Corrupted LZ77 Recovery | 0/30 | 22/30 | 17/30 | 0/30 | 0/30 | 0/30 |
| Gemini 3.5 Flash | MFN-Cascade | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 |
| Claude Opus | Conlang Rosetta | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 |

Reimbursement Forensics is the best current candidate. Every tested solver
gets some answers, so it does not look unknowable, but no solver gets close to
saturation. This is the target shape.

Cross-Document Obligation Resolution is not a keeper. The public packet lets
solvers recover the core dates, but the scorer requires private exact labels
and evidence-code strings. That is a scoring-contract failure, not a hard
benchmark.

Corrupted LZ77 Recovery is not unknowable, because GPT-5.4 got 22/30 and
GPT-5.5 got 17/30. But it is narrow and operationally brittle: several solvers
returned blanks, no parsed rows, or timed out. Treat it as a caution, not as
the benchmark shape to copy.

## What The Next Creator Should Do

Build something closer to Reimbursement Forensics and farther from the failure
cases.

A strong candidate should have:

- complete public evidence, with no hidden generator trick needed to answer;
- a closed or clearly normalizable answer contract;
- messy cross-document evidence that rewards careful reading and tool use;
- adversarial edge cases that punish one-pass heuristics;
- enough item diversity that one brittle script cannot solve all 30 rows;
- partial recoverability, so weak or incomplete solvers get nonzero scores;
- no obvious single algorithm such as BFS, direct simulation, exact parsing, or
  brute-force search over a clean finite state space.

Avoid these traps:

- Do not rely on type strictness, casing, private labels, or hidden vocabulary
  to create low scores.
- Do not create an all-zero benchmark unless the public bundle contains clear
  evidence that a human or strong external solver can recover the answers.
- Do not make a clean puzzle where the README tells the solver the intended
  abstraction.
- Do not make a narrow recovery task whose main difficulty is getting a tool
  run to finish.
- Do not make a task that is just larger. Strong solvers can script large clean
  tasks.

In `validation_report.md`, prove the benchmark is fair. For each answer field,
say what public evidence identifies it and how an external solver could verify
it without seeing private gold answers.

The benchmark should be rejected if any strong solver gets 30/30. It should
also be rejected if all strong solvers get 0/30 and the package cannot show
external solvability from the public bundle.
