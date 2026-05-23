Done. I created the complete benchmark package in the artifact directory.

Benchmark: **Amendment Ledger Reconciliation (ALR)**. It tests ordered amendment application over a self-contained rule ledger, with exact deterministic grading.

Verified:
- Generated 30 sample items with the required `generator.py` command.
- `verifier.py` passes: `verified 30 items`.
- Gold self-score: `30/30`.
- Weak fallback baseline: `0/30`.
- Solver bundle leakage check passed.
- Python files compile when cache is redirected to `/private/tmp`.

One environment note: the Python executable prints `pyenv: cannot rehash: /Users/rohit/.pyenv/shims isn't writable`, but the required commands themselves run successfully and produce valid outputs.