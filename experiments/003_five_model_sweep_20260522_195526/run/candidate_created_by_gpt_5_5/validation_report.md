# Validation Report

## Package Status

Generated 30 private-sample items with:

```bash
/Users/rohit/.pyenv/versions/global_env/bin/python generator.py --sample-count 30 --seed 20260516 --out-dir .
```

The package verifier passed:

```text
verified 30 items
```

## Scoring Checks

Gold self-score:

```text
30/30
```

Weak baseline:

```text
0/30
```

The weak baseline predicted the same fallback-shaped answer for every item:

```text
rule=R0|fee_units=35|deadline_days=45|notice=yes|waiver=none
```

This confirms that format compliance alone is not enough, and that the sample does not collapse to the fallback rule.

## Solver Bundle Leakage Check

The solver bundle contains only:

```text
solver_bundle/solver_packet.md
solver_bundle/items_private_sample.jsonl
solver_bundle/SOLVER_MANIFEST.json
```

The verifier checks that the bundle does not contain private answer keys, private audit traces, generator/verifier/scorer code, validation reports, or failure-mode notes. It also checks that no gold answer appears verbatim in the solver-visible item JSON.

A targeted text search for private filenames, answer-key patterns, and `solution` label wording inside `solver_bundle/` found no leakage.

## External Solvability And Identifiability

ALR is hard but externally solvable. A qualified external solver has all needed evidence in `solver_bundle/items_private_sample.jsonl` and `solver_bundle/solver_packet.md`:

- the initial definitions, rules, and fee caps
- every amendment in chronological order
- the case file
- the complete decision rules
- the exact answer format

The answer for each item is identifiable by a finite audit procedure:

1. Initialize the public base code.
2. Apply each listed amendment in order.
3. Discard suspended rules unless later replaced in full.
4. Evaluate active rule conditions against the case file using final definitions.
5. Pick the matching rule with highest priority, breaking ties by rule id.
6. Apply the final fee cap for the case region and request class.
7. Apply notice waiver rules to the final case tokens.
8. Emit the exact answer string.

No private generator state, hidden seed, external corpus, legal background, or open research result is needed to determine the answers. The private audit traces are only for benchmark-author inspection; they are not required for solving.

## Determinism

For fixed `--seed` and `--sample-count`, `generator.py` deterministically emits the same solver-visible item file, private gold file, private audit trace file, and solver manifest.

## Human Auditability

Each item is small enough for a human to audit by hand: it has a compact base code, 7-11 amendments, one case file, and a single exact output. The private audit trace records the generated final state for spot checks, while the public item remains self-contained.

## Closest Existing Benchmarks

ALR is closest to MuSR and BIG-Bench Hard because it requires multi-step state tracking over text. It is also adjacent to legal-rule interpretation benchmarks because the surface form resembles statutory amendment reconciliation. It is not a duplicate because it is fully synthetic, self-contained, exact-match graded, and focused on ordered amendment application rather than legal knowledge, broad QA, or chain-of-thought judging.
