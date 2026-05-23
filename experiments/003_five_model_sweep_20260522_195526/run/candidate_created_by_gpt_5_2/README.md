# Ledger Canonical Reconciliation (LCR) v1

This BenchBench package defines a deterministic, human-auditable reconciliation task.

For each item, the solver receives a small bundle containing:
- `ledger.csv`: transactions in multiple currencies
- `fx_rates.csv`: daily FX rates to USD (by calendar date)
- `rules.md`: the exact scoring rules (shared across items, identical content)

The solver must compute the final balance for every account **in USD cents**, applying:
- transaction de-duplication rules,
- reversal semantics,
- time-indexed FX selection rules,
- and output canonical JSON (sorted keys, no whitespace).

Scoring is exact-match on the canonical JSON string.

## Run the benchmark locally (creator-side)

Generate a private sample (30 items):

`/Users/rohit/.pyenv/versions/global_env/bin/python generator.py --sample-count 30 --seed 20260516 --out-dir .`

Verify format and ids:

`/Users/rohit/.pyenv/versions/global_env/bin/python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl`

Score predictions:

`/Users/rohit/.pyenv/versions/global_env/bin/python scorer.py --gold gold_private_sample.jsonl --predictions predictions.jsonl --out score_report.json`

## What makes it hard

The items are small enough to audit by hand, but contain adversarial-yet-specified cases:
- duplicate `txn_id` rows with conflicting amounts/timestamps,
- reversals that cancel earlier transactions (including duplicate reversals),
- out-of-order timestamps,
- FX rates requiring “most recent prior date” selection,
- rounding rules that must be implemented exactly.

This is “tool-friendly” in principle (a qualified solver can script it), but it punishes sloppy assumptions and partial rule-following.

