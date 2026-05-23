# String Rewriting Distance (srd_v1)

A benchmark of small string-rewriting puzzles. For each item the solver is
given an initial string, a target string, and a small set of
pattern→replacement rules over the alphabet `{A, B, C, D}`. The task is to
output the **minimum number of rule applications** needed to transform the
initial string into the target string under the rule
`intermediate strings may not exceed length 12`.

Each rule has a 2-character pattern and a 1- or 2-character replacement. A
single rule application replaces one occurrence of a rule's pattern,
anywhere it appears in the current string, with that rule's replacement.

## CLI

```
python generator.py --sample-count 30 --seed 20260516 --out-dir .
python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl
python scorer.py   --gold gold_private_sample.jsonl --predictions predictions.jsonl --out score_report.json
```

## Data contract

- `gold_private_sample.jsonl`: one JSON per line with exactly `id` and `answer`.
- `predictions.jsonl`: one JSON per line with exactly `id` and `answer` (integer).
- `solver_bundle/items_private_sample.jsonl`: one JSON per line with `id`,
  `initial`, `target`, `rules` (no answer key).

## Relationship to existing benchmarks

Closest in spirit to BIG-Bench Hard items that test multi-step state
tracking (e.g. `tracking_shuffled_objects`, `web_of_lies`) and to ARC-style
program-trace puzzles. It is not a duplicate: the state space is an
unbounded string space rather than a fixed enumeration, the answer is a
numeric shortest-path distance, items are procedurally generated, gold is
mechanically derived by BFS, and there is no narrative, world-knowledge, or
arithmetic-word-problem component. The capability isolated is purely
local-rewrite shortest-path reasoning.

## Why this is hard for tool-enabled LLMs

A model with a code-execution tool can in principle solve every item by
implementing BFS over strings. In practice, models tend to:

- Misread the operation (apply replacement at a wrong position, or
  conflate concurrent applications),
- Mishandle the `length ≤ 12` cap during search,
- Write greedy heuristics that don't yield the minimum (the greedy
  shrink-first baseline scores 9/30 here),
- Produce inconsistent BFS implementations that re-explore states or stop
  early.

A careful BFS, however, is sufficient: the answer is well-defined and
checkable.
