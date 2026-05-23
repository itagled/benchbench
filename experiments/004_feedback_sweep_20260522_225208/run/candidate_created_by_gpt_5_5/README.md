# Cross-Document Obligation Resolution

CDOR is a text-only benchmark for procedural reconciliation. Each item gives a public incident dossier with facts, older rules, amendments, board/hold rules, remediation rules, and an exact answer schema. The solver must determine the notification due date and required operational actions.

The benchmark is closest to GAIA-style evidence combination, document-understanding tasks, and instruction-following evals. It is not a duplicate of those benchmarks because the task is not open web research, visual extraction, or generic QA. The core capability is resolving live procedural obligations from complete but messy local evidence, including superseded clauses, strictest-deadline precedence, business-day arithmetic, and exception ordering.

## Required Commands

Generate the sample:

```bash
/Users/rohit/.pyenv/versions/global_env/bin/python generator.py --sample-count 30 --seed 20260516 --out-dir .
```

Verify structure and leakage:

```bash
/Users/rohit/.pyenv/versions/global_env/bin/python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl
```

Score predictions:

```bash
/Users/rohit/.pyenv/versions/global_env/bin/python scorer.py --gold gold_private_sample.jsonl --predictions predictions.jsonl --out score_report.json
```

## Solver Task

The isolated solver bundle is `solver_bundle/`. It contains `SOLVER_MANIFEST.json`, `items_private_sample.jsonl`, `solver_packet.md`, and one markdown dossier per item under `assets/`.

Predictions must be JSONL rows with exactly `id` and `answer`. The answer can be either a JSON object or a JSON-encoded string with exactly:

```json
{"notify_by":"YYYY-MM-DD","board_review":"required","remediation":"...","hold":"...","evidence_codes":["..."]}
```

Business days exclude Saturday and Sunday. There are no public holidays.

## Intended Difficulty

A brittle script that extracts one field or applies only the first rule should fail. A qualified solver can still solve every item by reading the dossier, applying the live amendments, checking exception ordering, and doing weekday-only date arithmetic.
