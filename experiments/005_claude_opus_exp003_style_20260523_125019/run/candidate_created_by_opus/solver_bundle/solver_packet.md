# Solver Packet: String Rewriting Distance

## What you receive

`items_private_sample.jsonl` — one item per line. Each item has:

- `id` (string)
- `initial` (string over `{A, B, C, D}`, length 5–7)
- `target` (string over `{A, B, C, D}`, length 2–4)
- `rules` (list of `[pattern, replacement]` pairs; pattern length 2;
  replacement length 1 or 2)

## What you output

A JSONL file `predictions.jsonl`, one line per item:

```json
{"id": "srd_000", "answer": 5}
```

`answer` is the **minimum number of rule applications** that transforms
`initial` into `target`, under these rules of play:

1. A single step chooses one rule `(pat, rep)` and one index `i` such that
   `current[i:i+2] == pat`, and produces
   `current[:i] + rep + current[i+2:]`.
2. The empty string is not allowed as an intermediate (the replacement
   length is at least 1, so this can only happen if you reduce a length-2
   string with a length-1 replacement that is itself the empty string —
   which never appears in the rule set).
3. **Intermediate strings may not exceed 12 characters.** Any path that
   passes through a string of length > 12 is disallowed.
4. The target itself must be exactly matched.

All items in this sample have a reachable target (`answer >= 0`); you do
not need to handle the unreachable case.

## A worked example

Suppose `initial = "ABAB"`, `target = "C"`, and
`rules = [["AB", "C"], ["CB", "A"], ["CA", "B"]]`.

A shortest path is: `ABAB → CAB → CB → A → ...` wait, target is `C`,
let's redo. `ABAB → CAB → CC` — but no rule produces `C` from `CC`.
Better: `ABAB → ACB → AA`? No `ACB` requires `AB→C` at position 1.
This example is just illustrative; in practice you should implement BFS.

## Reference algorithm (BFS)

```python
from collections import deque

def min_steps(initial, target, rules, max_len=12, max_steps=25):
    if initial == target:
        return 0
    visited = {initial}
    frontier = [initial]
    for step in range(1, max_steps + 1):
        nxt = []
        for s in frontier:
            for pat, rep in rules:
                i = 0
                while True:
                    j = s.find(pat, i)
                    if j < 0: break
                    new_s = s[:j] + rep + s[j+2:]
                    if len(new_s) > max_len:
                        i = j + 1; continue
                    if new_s == target:
                        return step
                    if new_s not in visited:
                        visited.add(new_s)
                        nxt.append(new_s)
                    i = j + 1
        if not nxt:
            return -1
        frontier = nxt
    return -1
```

This is a complete reference implementation; running it on each item gives
the gold answer. The benchmark tests whether the model can produce or
faithfully execute equivalent reasoning.
