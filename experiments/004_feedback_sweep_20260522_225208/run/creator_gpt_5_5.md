Built the benchmark package in the specified artifact directory.

Created **Cross-Document Obligation Resolution (CDOR)**: a text-only benchmark where solvers reconcile messy procedural dossiers with amendments, exceptions, business-day deadlines, board review rules, holds, and remediation priority.

Verification completed:

- Generated 30 sample items.
- `verifier.py`: `verified 30 items`
- Gold self-score: `30/30`
- Weak baseline: `0/30`
- Solver bundle inspected: contains only manifest, public item list, solver packet, and 30 public dossier files.
- `validation_report.md` includes the external solvability/identifiability argument and audit notes.

One minor environment note: the required Python command prints `pyenv: cannot rehash: /Users/rohit/.pyenv/shims isn't writable`, but all commands exit successfully and produce the expected outputs.