# Cross-Document Obligation Resolution Solver Packet

You receive one markdown dossier per item. Each dossier contains all facts and all live rules needed to answer the item.

For each item, submit one JSONL row with exactly:

```json
{"id":"cdor-001","answer":{"notify_by":"YYYY-MM-DD","board_review":"required","remediation":"...","hold":"...","evidence_codes":["..."]}}
```

The `answer` may also be a JSON-encoded string containing the same object. Use only the public dossier. Do not infer from item order or from any generator.

Business days exclude Saturdays and Sundays. No public holidays are used.
