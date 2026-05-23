# Feedback For Next BenchBench Sweep

This feedback is given to creator models after Experiment 003.

BenchBench is evaluating benchmark invention, not ordinary question answering.
The goal is to create a complete benchmark package that is valid, reproducible,
auditable, externally solvable in principle, and still hard after strong
tool-enabled solvers attack the public solver bundle.

## What Happened In Experiment 003

All five creator models produced structurally valid benchmark packages. That is
good, but every fresh candidate was rejected because at least one strong solver
got 30/30.

| creator | generated benchmark | solver GPT-5.2 | solver GPT-5.4 | solver GPT-5.5 | solver Gemini 3.1 Pro | solver Gemini 3.5 Flash | result |
|---|---|---:|---:|---:|---:|---:|---|
| GPT-5.2 | Ledger Canonical Reconciliation | 11/30 | 30/30 | 30/30 | 30/30 | 30/30 | too easy |
| GPT-5.4 | Patchwork Ordinance Adjudication | 3/30 | 30/30 | 30/30 | 30/30 | 30/30 | too easy, but diagnostic |
| GPT-5.5 | Amendment Ledger Reconciliation | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 | too easy |
| Gemini 3.1 Pro | Polyhedral Surface Traversal | 30/30 | 6/30 | 30/30 | 30/30 | 30/30 | too easy, but diagnostic |
| Gemini 3.5 Flash | Mutative Assembly Inversion | 30/30 | 30/30 | 30/30 | 30/30 | 22/30 | too easy |

The useful signal was model-specific weakness, not a new accepted benchmark:
GPT-5.2 struggled with Patchwork Ordinance Adjudication, GPT-5.4 struggled with
Polyhedral Surface Traversal, and Gemini Flash missed rows on Mutative Assembly
Inversion. But the maximum solver score was 30/30 for every row.

## Stable-Bank Context

Experiment 002 remains the stable-bank reference:

| benchmark | GPT-5.2 | GPT-5.4 | GPT-5.5 | Gemini 3.1 Pro | Gemini 3.5 Flash | read |
|---|---:|---:|---:|---:|---:|---|
| IgnoreSense | 4/30 | 7/30 | 7/30 | 7/30 | 4/30 | hard and nonzero |
| Spectrum Assembly | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 | too easy |
| Protocol Archaeology | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | hard-looking but solvability unresolved |

The lesson is that a useful benchmark should avoid both failure modes:

- Not too easy: if one strong solver can script or abstract the task and get
  30/30, the candidate does not survive.
- Not unknowable: all-zero scores are not automatically good; the public bundle
  must contain enough information for an external solver to identify the
  answers in principle.

## What To Do Differently

Do not merely make a larger version of the previous tasks. Strong solvers are
good at writing scripts, brute-forcing small finite spaces, parsing rule files,
and implementing direct simulations when the rule abstraction is obvious.

Instead, try to design a benchmark where the public evidence is complete but
the successful solver must combine several hard-to-automate capabilities, such
as:

- precise interpretation of messy but finite specifications;
- adversarially chosen edge cases;
- cross-document consistency checks;
- procedural reasoning where shortcuts fail;
- robust handling of ambiguity that is resolved by public evidence;
- multi-stage inference where the right intermediate representation is not
  obvious;
- enough diversity across the 30 items that one brittle script does not solve
  all of them.

The benchmark still must be fair. It must not depend on hidden generator logic,
private seeds, private answer keys, impossible research problems, or arbitrary
author intent. In `validation_report.md`, explain why the public solver bundle
is sufficient for an external solver in principle and what evidence proves each
answer.

A better candidate is one where weak baselines fail, strong solvers cannot get
near-perfect scores in one pass, and at least some answers remain recoverable so
the task is not simply under-specified.
