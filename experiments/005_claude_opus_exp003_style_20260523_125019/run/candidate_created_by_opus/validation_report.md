# Validation Report — String Rewriting Distance (srd_v1)

## Generation

```
python generator.py --sample-count 30 --seed 20260516 --out-dir .
```

Produced 30 items in `gold_private_sample.jsonl` and a leakage-stripped
copy in `solver_bundle/items_private_sample.jsonl`.

Answer distribution (gold):

```
3: 7   4: 4   5: 6   6: 8   7: 2   9: 2   10: 1
```

Mean ≈ 5.1 steps; minimum 3, maximum 10. All items are reachable.

## Verification

```
python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl
```

`OK: 30 items verified, all BFS distances match gold.`

The verifier independently recomputes the BFS distance for every item and
confirms it matches the stored gold answer, so the gold file is internally
consistent with the rule-application semantics.

## Self-score and baselines

| solver | predictions | score |
|---|---|---|
| oracle (gold copied as predictions) | predictions.jsonl | **30 / 30** |
| constant-0 (`answer = 0`) | preds_zero.jsonl | 0 / 30 |
| length-diff (`max(1, len(initial) - len(target))`) | preds_lendiff.jsonl | 10 / 30 |
| greedy shrink-first (prefer rules with replacement length 1) | preds_greedy.jsonl | 9 / 30 |

The oracle perfect score confirms the scorer works. The constant-0 baseline
falls to zero — no item has answer 0. The two heuristic baselines reach
~33 % which is below the difficulty gate; this is the floor that solver
models must beat to demonstrate genuine state-space search rather than a
shallow heuristic.

## External solvability / identifiability

A qualified external solver — another model, a human specialist, or any
combination — receives, for each item, the complete information needed to
mechanically determine the answer:

- the exact alphabet (`{A, B, C, D}`),
- the initial string,
- the target string,
- the full rule list, and
- the operational semantics and length cap stated in
  `solver_bundle/solver_packet.md`.

The answer to an item is *defined* as the minimum number of rule
applications under those semantics, which is computable by breadth-first
search over reachable strings. The reachable graph is finite (string
length is bounded by 12 and the alphabet has size 4, so at most
4 + 16 + … + 4^12 ≈ 22M states), so BFS terminates. There are no hidden
seeds, no private grader logic, and no information in the
generator/verifier that is not reflected in the public packet. The
solver packet even contains a reference BFS implementation, so the
evidence an external solver needs is exhausted by what is shipped.

Items are filtered at generation time to have answers in `[3, 14]`, so
shortcut heuristics cannot dominate, but the search depth remains small
enough that a competent BFS exhausts the relevant subgraph in
milliseconds.

## Leakage check on the solver bundle

```
solver_bundle/
  SOLVER_MANIFEST.json
  items_private_sample.jsonl   # only id / initial / target / rules
  solver_packet.md
```

Inspected `items_private_sample.jsonl`: no `answer` field, no gold,
no audit traces, no generator source, no scorer source. The manifest and
packet describe the public task contract only. The `gold_private_sample.jsonl`,
the BFS-based generator, the verifier, and the scorer all live outside the
bundle and are not exposed to solvers.

## Capability claim

The benchmark measures one narrow capability: shortest-path computation
in a string-rewriting state graph specified by a small set of local rules.
It is not a measure of world knowledge, calibration, or natural-language
understanding. It is hostile to two common LLM failure modes:
(a) silent off-by-one or position-tracking errors during simulated
search, and (b) substituting a greedy heuristic for genuine BFS.

## Reproducibility

Seed `20260516` plus the generator script regenerate the exact same 30
items (Python's `random.Random` is deterministic and the generator does
not depend on system randomness). The verifier and scorer are pure
functions of their inputs.
