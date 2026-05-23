#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_jsonl(path: Path) -> list[dict]:
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
    ap.add_argument("--items", required=True, type=str)
    ap.add_argument("--gold", required=True, type=str)
    args = ap.parse_args()

    items_path = Path(args.items)
    gold_path = Path(args.gold)

    items_rows = _load_jsonl(items_path)
    gold_rows = _load_jsonl(gold_path)

    gold_ids = []
    for i, row in enumerate(gold_rows, start=1):
        if set(row.keys()) != {"id", "answer"}:
            raise SystemExit(f"{gold_path}: line {i}: keys must be exactly {{'id','answer'}}")
        if not isinstance(row["id"], str) or not isinstance(row["answer"], str):
            raise SystemExit(f"{gold_path}: line {i}: 'id' and 'answer' must be strings")
        gold_ids.append(row["id"])

    item_ids = []
    for i, row in enumerate(items_rows, start=1):
        if "id" not in row:
            raise SystemExit(f"{items_path}: line {i}: missing 'id'")
        if not isinstance(row["id"], str):
            raise SystemExit(f"{items_path}: line {i}: 'id' must be a string")
        item_ids.append(row["id"])
        # Ensure referenced files exist relative to solver_bundle
        base = items_path.parent.resolve()
        for k in ["ledger_csv", "fx_rates_csv", "rules_md"]:
            if k not in row or not isinstance(row[k], str):
                raise SystemExit(f"{items_path}: line {i}: missing or invalid '{k}'")
            p = (base / row[k]).resolve()
            if not p.exists():
                raise SystemExit(f"{items_path}: line {i}: missing asset for {k}: {row[k]}")
            # Must be inside solver_bundle
            if p != base and base not in p.parents:
                raise SystemExit(f"{items_path}: line {i}: asset escapes solver_bundle: {row[k]}")

    if len(set(gold_ids)) != len(gold_ids):
        raise SystemExit("gold_private_sample.jsonl has duplicate ids")
    if len(set(item_ids)) != len(item_ids):
        raise SystemExit("items_private_sample.jsonl has duplicate ids")
    if set(gold_ids) != set(item_ids):
        missing_in_items = sorted(set(gold_ids) - set(item_ids))
        missing_in_gold = sorted(set(item_ids) - set(gold_ids))
        raise SystemExit(
            "ID mismatch between items and gold.\n"
            f"missing_in_items={missing_in_items}\n"
            f"missing_in_gold={missing_in_gold}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
