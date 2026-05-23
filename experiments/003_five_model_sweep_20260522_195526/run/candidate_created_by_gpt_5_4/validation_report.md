# Validation Report (POA v1)

## Summary

Patchwork Ordinance Adjudication (POA) v1 is a deterministic benchmark for multi-document rule compilation. Each item asks the solver to reconstruct the operative ordinance from a base charter, an amendments packet, and a case file, then emit one exact adjudication string.

Required answer format:

`verdict=<ALLOW|REVIEW|DENY>;lane=<GREEN|AMBER|RED>;fee=<integer>`

## External solvability / identifiability

This benchmark is solvable in principle by a qualified external solver using only the public solver bundle.

- Every item exposes all necessary evidence: `shared_rules.md`, per-item `charter.md`, per-item `amendments.md`, and per-item `case_file.json`.
- The public rules specify the full execution order, including replacement rules, additive rules, capped waivers, fee floor, verdict thresholds, and lane thresholds.
- A human auditor can work item-by-item from the visible documents and check whether each condition fires.
- A specialist external solver can also write a short script against the public bundle alone and reproduce the answers without seeing any private files.

The benchmark is hard because the solver must compile several interacting textual rules correctly, not because any information is missing.

## Determinism and grading reliability

- Generation is seeded through `generator.py`.
- Gold rows contain exactly `id` and `answer`.
- Scoring is exact match on one canonical answer string.
- The verifier rejects malformed JSONL rows, duplicate ids, path traversal, absolute paths, and missing bundle files.
- The scorer rejects malformed answer rows, duplicate ids, and prediction/gold id mismatches before grading.

## Validation runs completed

Commands rerun from this artifact directory after the repair:

- Generator: `/Users/rohit/.pyenv/versions/global_env/bin/python generator.py --sample-count 30 --seed 20260516 --out-dir .`
- Verifier: `/Users/rohit/.pyenv/versions/global_env/bin/python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl`
- Controller gold score: `/Users/rohit/.pyenv/versions/global_env/bin/python scorer.py --gold gold_private_sample.jsonl --predictions predictions_gold_controller.jsonl --out score_gold_controller.json`
- Controller shifted-wrong score: `/Users/rohit/.pyenv/versions/global_env/bin/python scorer.py --gold gold_private_sample.jsonl --predictions predictions_wrong_shifted_controller.jsonl --out score_wrong_shifted_controller.json`

Observed results:

- Verifier: passed with 30 aligned items.
- Controller gold score: 30/30.
- Controller shifted-wrong score: 0/30.

## Leakage inspection

I inspected the public solver bundle for answer leakage and private implementation leakage.

Included:
- solver-facing rules
- per-item public assets
- file checksums and manifest metadata

Not included:
- gold answers
- generator, verifier, or scorer code
- seeds
- private validation notes
- hidden labels or solution traces

A text scan of `solver_bundle/` found only the public answer-format string, not gold answer rows or creator-side code names.

## Distribution notes

The generated 30-item sample is not label-balanced:

- Verdicts: 23 `DENY`, 6 `REVIEW`, 1 `ALLOW`
- Lanes: 19 `RED`, 8 `AMBER`, 3 `GREEN`

This is a limitation worth noting. Still, the benchmark is not cheaply solved by majority guessing because the exact-match answer also requires the correct fee and lane, and the weak baseline scored 0/30.

## Closest existing benchmark families

POA is closest to document understanding and expert-QA style tasks, with some overlap with tool-assisted exact reasoning benchmarks.

It is not merely a duplicate because:

- the output is deterministic and exactly graded;
- the core challenge is amendment compilation under precedence rules rather than open-ended question answering;
- and success depends on turning textual rule packets into the correct operational interpretation, not on browsing or hidden-test coding.
