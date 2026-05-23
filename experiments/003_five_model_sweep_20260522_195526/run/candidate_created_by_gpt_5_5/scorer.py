#!/usr/bin/env python3
"""Exact-match scorer for Amendment Ledger Reconciliation."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ANSWER_RE = re.compile(
    r"^rule=R\d+\|fee_units=\d+\|deadline_days=\d+\|notice=(yes|no)\|waiver=([A-Za-z0-9_+]+|none)$"
)


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                row = json.loads(line)
                rows.append(row)
                if set(row) != {"id", "answer"}:
                    raise ValueError(f"{path}:{line_no} must contain exactly id and answer")
    return rows


def normalize(answer: object) -> str:
    return str(answer).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", required=True)
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    gold_rows = read_jsonl(Path(args.gold))
    pred_rows = read_jsonl(Path(args.predictions))
    gold = {row["id"]: normalize(row["answer"]) for row in gold_rows}
    predictions = {row["id"]: normalize(row["answer"]) for row in pred_rows}

    details = []
    correct = 0
    for item_id, expected in gold.items():
        got = predictions.get(item_id, "")
        ok = got == expected
        correct += int(ok)
        details.append(
            {
                "id": item_id,
                "correct": ok,
                "expected": expected,
                "prediction": got,
                "prediction_well_formed": bool(ANSWER_RE.match(got)),
            }
        )

    extra_predictions = sorted(set(predictions) - set(gold))
    report = {
        "score": correct,
        "total": len(gold),
        "accuracy": correct / len(gold) if gold else 0.0,
        "missing_predictions": sorted(set(gold) - set(predictions)),
        "extra_predictions": extra_predictions,
        "details": details,
    }
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{correct}/{len(gold)}")


if __name__ == "__main__":
    main()
