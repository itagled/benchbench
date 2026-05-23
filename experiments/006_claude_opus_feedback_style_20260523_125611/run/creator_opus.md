Package complete. Summary:

**Conlang Rosetta** — Linguistics-Olympiad-style benchmark. Each of 30 items is a freshly generated fictional language with a lexicon + ~7 interlinear-glossed example sentences. Solver must infer word order, suffix ordering, adjective position, tense, and negation from minimal pairs, then translate a held-out gloss to an exact conlang string.

- Generator/verifier/scorer pass ✓
- Gold self-score: **30/30**
- Naive stem-lookup baseline: **0/30**
- Solver bundle contains no gold/code/audit
- External solvability proven by construction: every test feature appears in examples; lexicon makes stem-vs-suffix segmentation observable

Avoids the prior failure mode (clean BFS-over-state-space): no single algorithm solves all 30, each item exposes a different random grammar combination, and the task requires combining several morphological capabilities. Not a duplicate of LINGOLY/Linguini since languages are procedurally generated (no training-data leakage possible).