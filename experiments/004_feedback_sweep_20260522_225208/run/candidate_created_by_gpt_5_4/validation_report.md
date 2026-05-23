# Validation Report

## What this benchmark measures

`release_packet_arbitration` measures cross-document procedural reasoning over finite operational evidence. A solver has to read a policy manual, then reconcile a release request, amendments, approvals, delegation windows, freeze notices, and incident evidence to determine the highest-priority governing rule.

The intended capability is careful evidence integration under precedence rules rather than raw coding, retrieval, or single-document QA.

## Package validation

Commands run from this directory:

```bash
/Users/rohit/.pyenv/versions/global_env/bin/python generator.py --sample-count 30 --seed 20260516 --out-dir .
/Users/rohit/.pyenv/versions/global_env/bin/python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl
/Users/rohit/.pyenv/versions/global_env/bin/python scorer.py --gold gold_private_sample.jsonl --predictions predictions_gold_controller.jsonl --out score_gold_controller.json
/Users/rohit/.pyenv/versions/global_env/bin/python scorer.py --gold gold_private_sample.jsonl --predictions predictions_wrong_shifted_controller.jsonl --out score_wrong_shifted_controller.json
```

Observed results:

- Generator completed with a deterministic sample of `30` items from seed `20260516`.
- Verifier status: `ok`
- Solver bundle item count: `30`
- Gold self-score: `30/30`
- Wrong shifted controller score: `0/30`

## Solver-bundle isolation

The solver bundle is intentionally self-contained and public-only.

- Every item row uses relative paths inside `solver_bundle`.
- Solver-visible artifacts include only the policy manual, item manifest, and packet evidence.
- Gold answers, generator logic, verifier code, and scorer code stay outside `solver_bundle`.

## Sample composition

The generated 30-item private sample has this rule distribution:

- `A1`: 5
- `R1`: 4
- `R2`: 4
- `R3`: 4
- `R4`: 4
- `R5`: 4
- `R6`: 3
- `R7`: 2

Decision distribution:

- `approve`: 5
- `reject`: 25
- `escalate`: 0

## External solvability and identifiability

This benchmark is externally solvable from the public solver bundle alone.

Why:

1. The entire governing ruleset is public in `solver_bundle/policy/release_governance_manual.md`.
2. Every item points to a packet directory inside the solver bundle.
3. Each packet contains the evidence needed to determine requester identity, final schedule, amendments, approvals, delegations, freeze applicability, and incident timing.
4. The answer is determined by those public rules plus those public timestamps and role tables.

## Leakage inspection

The solver bundle intentionally contains policy rule names and answer-field names, but it does not contain the gold file or grading code.

## Closest existing benchmarks

- GAIA: multi-artifact, tool-friendly reasoning
- BrowseComp-style cross-document synthesis: answers depend on integrating several public files rather than a single prompt

Why it is not a duplicate:

- the evidence is synthetic and self-contained rather than web-native;
- grading is deterministic exact match;
- the task focuses on governance-rule arbitration under explicit precedence, not general browsing competence.
