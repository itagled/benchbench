# Failure Modes

## Known limitations of srd_v1

1. **Code-tool ceiling.** A solver that correctly implements BFS and runs
   it on every item gets 30/30. The benchmark therefore measures whether
   models *deploy* the right algorithm, not whether the algorithm exists.
   If a future model reliably writes correct BFS, this benchmark
   saturates.

2. **Small alphabet, short strings.** With a 4-letter alphabet and length
   cap 12, the full state space is ≈ 22M strings. Items here are designed
   so the *reachable* subgraph is much smaller (answers ≤ 14). A
   sufficiently strong heuristic that prunes by reachability metrics
   could outperform the greedy baseline reported here.

3. **Length-difference partial signal.** For items where each rule
   shrinks the string by exactly one character and no detours are
   required, the answer equals `len(initial) - len(target)`. About a
   third of items happen to satisfy this; that is why the length-diff
   baseline scores 10/30 rather than 0. Future versions could
   adversarially filter against this heuristic.

4. **No proof of uniqueness of optimal paths.** The answer (minimum step
   count) is unique, but there may be multiple optimal rule sequences.
   The benchmark only scores the *count*, not the sequence, so it cannot
   distinguish models that find an optimum from models that guess the
   right number.

5. **Difficulty cap.** Items with answer > 14 are filtered out at
   generation time to keep the benchmark tractable for human auditors
   and to avoid the search horizon ambiguity. This caps how challenging
   a single item can be; the benchmark is challenging in aggregate, not
   per-item.

6. **Rule ambiguity not stressed.** The generator does not deliberately
   construct items with deeply entangled rule interactions (e.g., rules
   whose patterns overlap with each other's replacements in adversarial
   ways). A v2 could mine such adversarial instances.

## How to detect benchmark failure during a run

- If a solver scores ≥ 28/30, suspect that it implemented BFS with code
  execution and the benchmark has saturated for that model.
- If a solver scores 9–11/30 with predictions that match the length-diff
  heuristic, suspect that the model is shortcutting rather than
  reasoning.
- If a solver scores 0/30 with all predictions equal to one number,
  suspect a parsing or output-format error rather than a reasoning
  failure.
