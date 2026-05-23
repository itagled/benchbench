Package complete. Summary:

**Benchmark: String Rewriting Distance (srd_v1)** — 30 procedurally generated items. Each gives an initial string, target string, and small rule set over `{A,B,C,D}`; the answer is the minimum number of 2→1/2 char rule applications transforming initial → target, under a length-12 cap.

**Validation results:**
- Verifier: 30/30 items, all BFS distances match gold
- Gold self-score: 30/30
- Constant-0 baseline: 0/30
- Length-diff heuristic: 10/30
- Greedy shrink-first: 9/30

**Why it's interesting:** Cleanly deterministic (BFS-defined gold), externally solvable in principle (full reference algorithm shipped), but exercises the exact failure modes LLMs show — position tracking, length-cap enforcement, and resisting greedy shortcuts. Not a duplicate of existing evals (closest is BBH state-tracking, but this is numeric shortest-path over an unbounded string space rather than narrative classification).