# Validation Report (LCR v1)

## Summary

LCR v1 is a deterministic reconciliation benchmark: each item provides a small transaction ledger and FX rate table, plus exact rules. The solver must compute exact final per-account balances in USD cents and emit a canonical JSON answer string. Scoring is exact match.

## External solvability / identifiability

This benchmark is solvable in principle by a qualified external solver using only the public solver bundle:
- Every item includes `ledger.csv` and `fx_rates.csv`, which fully determine the numeric inputs.
- The rules specify all required semantics: void filtering, de-duplication, reversal behavior, FX selection, rounding, and output canonicalization.
- A solver can determine correctness by re-implementing the rules and independently reproducing balances.
- Items are small enough to audit: a human can manually check a few transactions, reversals, and FX selections as spot checks, and a specialist can write a short script to compute all items.

## Determinism and grading reliability

- Item generation is seeded (`--seed`) and produces deterministic CSV content.
- Grading is exact match against gold canonical JSON strings.
- FX selection uses “latest date <= posted date”, avoiding ambiguous interpolation.
- Rounding is precisely specified (ties away from zero), preventing language-specific defaults from silently changing results.

## Leakage check (solver bundle)

The solver bundle contains only:
- item asset paths and checksums in `items_private_sample.jsonl`,
- per-item `ledger.csv`, `fx_rates.csv`, and `rules.md`,
- and a short `SOLVER_MANIFEST.json`.

It does **not** contain:
- gold answers,
- generator/verifier/scorer code,
- seeds or hidden labels.

## Baseline sanity checks (to be run by creator)

1. Gold self-score: use gold as predictions and confirm 30/30 (validated in this package via `score_report.json`).
2. Weak baseline: `baseline_naive.py` ignores VOID filtering, de-duplication, and reversal semantics, uses exact-day FX only, and truncates rounding; it scored 0/30 on the generated private sample (see `score_report_naive.json`).

## Novelty vs common eval families

LCR resembles “data wrangling / spec-following” tasks, but differs from typical coding benchmarks by:
- requiring exact reconstruction from adversarial ledger pathologies,
- being fully deterministic and auditable,
- and focusing on correctness under a formalized operational rule-set rather than API knowledge or open-ended program synthesis.
