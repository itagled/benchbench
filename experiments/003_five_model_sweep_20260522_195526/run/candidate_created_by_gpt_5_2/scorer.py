#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_jsonl_exact(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}: line {i}: invalid JSON: {e}") from e
            if not isinstance(obj, dict):
                raise SystemExit(f"{path}: line {i}: expected JSON object")
            rows.append(obj)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True, type=str)
    ap.add_argument("--predictions", required=True, type=str)
    ap.add_argument("--out", required=True, type=str)
    args = ap.parse_args()

    gold_path = Path(args.gold)
    pred_path = Path(args.predictions)
    out_path = Path(args.out)

    gold_rows = _load_jsonl_exact(gold_path)
    pred_rows = _load_jsonl_exact(pred_path)

    gold: dict[str, str] = {}
    for i, row in enumerate(gold_rows, start=1):
        if set(row.keys()) != {"id", "answer"}:
            raise SystemExit(f"{gold_path}: line {i}: keys must be exactly {{'id','answer'}}")
        if not isinstance(row["id"], str) or not isinstance(row["answer"], str):
            raise SystemExit(f"{gold_path}: line {i}: 'id' and 'answer' must be strings")
        if row["id"] in gold:
            raise SystemExit(f"{gold_path}: duplicate id: {row['id']}")
        gold[row["id"]] = row["answer"]

    preds: dict[str, str] = {}
    for i, row in enumerate(pred_rows, start=1):
        if set(row.keys()) != {"id", "answer"}:
            raise SystemExit(f"{pred_path}: line {i}: keys must be exactly {{'id','answer'}}")
        if not isinstance(row["id"], str) or not isinstance(row["answer"], str):
            raise SystemExit(f"{pred_path}: line {i}: 'id' and 'answer' must be strings")
        preds[row["id"]] = row["answer"]

    total = len(gold)
    correct = 0
    per_item: list[dict[str, object]] = []
    for item_id, gold_ans in gold.items():
        pred_ans = preds.get(item_id)
        is_correct = pred_ans == gold_ans
        if is_correct:
            correct += 1
        per_item.append({"id": item_id, "correct": is_correct})

    report = {
        "benchmark_id": "ledger_canonical_reconciliation_v1",
        "total": total,
        "correct": correct,
        "accuracy": (correct / total) if total else 0.0,
        "missing_predictions": sorted([i for i in gold.keys() if i not in preds]),
        "extra_predictions": sorted([i for i in preds.keys() if i not in gold]),
        "per_item": per_item,
    }
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

