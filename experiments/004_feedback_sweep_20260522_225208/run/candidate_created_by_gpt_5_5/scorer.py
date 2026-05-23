#!/usr/bin/env python3
"""Exact scorer for Cross-Document Obligation Resolution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_KEYS = ["notify_by", "board_review", "remediation", "hold", "evidence_codes"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows


def normalize_answer(raw: Any) -> dict[str, Any] | None:
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return None
    if not isinstance(raw, dict):
        return None
    if set(raw) != set(REQUIRED_KEYS):
        return None
    out = dict(raw)
    if not isinstance(out["evidence_codes"], list):
        return None
    out["evidence_codes"] = sorted(str(x) for x in out["evidence_codes"])
    for key in REQUIRED_KEYS[:-1]:
        if not isinstance(out[key], str):
            return None
    return out


def validate_prediction_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out = {}
    for row in rows:
        if set(row) != {"id", "answer"}:
            raise SystemExit(f"prediction row must contain exactly id and answer: {row}")
        if row["id"] in out:
            raise SystemExit(f"duplicate prediction id: {row['id']}")
        out[row["id"]] = row["answer"]
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    gold_rows = load_jsonl(args.gold)
    pred_rows = load_jsonl(args.predictions)
    preds = validate_prediction_rows(pred_rows)

    details = []
    correct = 0
    for row in gold_rows:
        if set(row) != {"id", "answer"}:
            raise SystemExit(f"gold row must contain exactly id and answer: {row}")
        gold = normalize_answer(row["answer"])
        pred = normalize_answer(preds.get(row["id"]))
        is_correct = gold is not None and pred == gold
        correct += int(is_correct)
        details.append({"id": row["id"], "correct": is_correct, "gold": gold, "prediction": pred})

    report = {
        "score": correct,
        "total": len(gold_rows),
        "accuracy": correct / len(gold_rows) if gold_rows else 0.0,
        "missing_ids": sorted(set(row["id"] for row in gold_rows) - set(preds)),
        "extra_ids": sorted(set(preds) - set(row["id"] for row in gold_rows)),
        "details": details,
    }
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{correct}/{len(gold_rows)}")


if __name__ == "__main__":
    main()
