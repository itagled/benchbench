# Patchwork Ordinance Adjudication (POA) v1

Patchwork Ordinance Adjudication is a deterministic document-compilation benchmark. Each item gives a small fictional ordinance packet split across a base charter, later amendments, and a case file. The solver must reconstruct the operative rules and emit one exact adjudication string.

Required answer format:

`verdict=<ALLOW|REVIEW|DENY>;lane=<GREEN|AMBER|RED>;fee=<integer>`

## Why this benchmark is interesting

This package targets a failure mode that many strong tool-enabled models still show: they can read the documents, but they often miss precedence, replacement-vs-additive distinctions, one-of-many waiver rules, or final-stage overrides. The items are small enough to audit by hand, yet structured so that shallow reading and naive extraction both fail.

Closest existing families:
- document understanding / expert QA: it requires integrating several small texts into one answer.
- tool-agent / coding-adjacent tasks: a solver can script the rules if it translates them correctly.

Why it is not a duplicate:
- it is not open-ended QA, browsing, or essay judging;
- it is not a pure coding task with hidden tests;
- and it is not a standard logic puzzle set, because the key challenge is compiling amendment packets into an exact executable interpretation.

## Files

- `generator.py`: deterministic item and solver-bundle generator.
- `verifier.py`: checks bundle integrity and id alignment.
- `scorer.py`: exact-match scorer.
- `gold_private_sample.jsonl`: creator-side gold answers for the private sample.
- `solver_bundle/`: isolated public solver packet.

## CLI

Generate a 30-item sample:

`/Users/rohit/.pyenv/versions/global_env/bin/python generator.py --sample-count 30 --seed 20260516 --out-dir .`

Verify:

`/Users/rohit/.pyenv/versions/global_env/bin/python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl`

Score predictions:

`/Users/rohit/.pyenv/versions/global_env/bin/python scorer.py --gold gold_private_sample.jsonl --predictions predictions.jsonl --out score_report.json`
