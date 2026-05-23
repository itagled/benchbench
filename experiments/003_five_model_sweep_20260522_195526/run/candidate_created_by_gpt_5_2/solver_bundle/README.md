# LCR v1 Solver Bundle

This bundle contains the only files a solver is allowed to read.

Inputs:
- `items_private_sample.jsonl`: the list of items and relative asset paths
- `items/<id>/ledger.csv`
- `items/<id>/fx_rates.csv`
- `items/<id>/rules.md`

Task: for each item, compute the canonical JSON answer string described in `rules.md`.
