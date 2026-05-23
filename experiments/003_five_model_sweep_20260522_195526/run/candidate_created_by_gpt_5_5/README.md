# Amendment Ledger Reconciliation (ALR)

ALR tests whether a solver can apply a base rule code plus a chronological amendment ledger, then compute the final result for a specific case file.

Each item is self-contained. The solver sees:

- initial definitions, rules, and fee caps
- ordered amendments that can replace, suspend, add, redefine, cap, or waive
- one case file
- exact decision rules and answer format

The answer is an exact string:

```text
rule=<RULE>|fee_units=<INT>|deadline_days=<INT>|notice=<yes/no>|waiver=<none or + joined waiver ids>
```

## Why This Is Interesting

This is closest to MuSR/BIG-Bench Hard style stateful reasoning and to legal-rule interpretation tasks, but it is not a duplicate of either. The task is generated, self-contained, deterministic, and exactly graded. It does not require legal knowledge. It requires careful public-evidence reconciliation: applying ordered edits, tracking definitions, choosing the highest-priority active matching rule, applying fee caps, and handling notice waivers.

## Files

- `generator.py`: deterministic item and gold generator
- `verifier.py`: validates item/gold structure and checks solver-bundle leakage
- `scorer.py`: exact-match scorer
- `benchmark_spec.json`: machine-readable benchmark summary
- `gold_private_sample.jsonl`: private answer key
- `solver_bundle/items_private_sample.jsonl`: solver-visible items
- `solver_bundle/solver_packet.md`: solver instructions
- `validation_report.md`: validation results and solvability argument
- `failure_modes.md`: expected failure modes and shortcut checks

## Required Commands

```bash
/Users/rohit/.pyenv/versions/global_env/bin/python generator.py --sample-count 30 --seed 20260516 --out-dir .
/Users/rohit/.pyenv/versions/global_env/bin/python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl
/Users/rohit/.pyenv/versions/global_env/bin/python scorer.py --gold gold_private_sample.jsonl --predictions predictions.jsonl --out score_report.json
```

Gold rows and prediction rows must contain exactly `id` and `answer`.
