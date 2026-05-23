#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROW_KEYS = {"id", "answer"}
VALID_VERDICTS = {"ALLOW", "REVIEW", "DENY"}
VALID_LANES = {"GREEN", "AMBER", "RED"}


def load_rows(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            raw = line.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path.name} line {line_no}: invalid JSON: {exc.msg}") from exc
            if not isinstance(row, dict):
                raise SystemExit(f"{path.name} line {line_no}: each row must be a JSON object")
            if set(row.keys()) != ROW_KEYS:
                raise SystemExit(f"{path.name} line {line_no}: rows must contain exactly id and answer")
            if not isinstance(row["id"], str) or not row["id"]:
                raise SystemExit(f"{path.name} line {line_no}: id must be a non-empty string")
            if not is_valid_answer(row["answer"]):
                raise SystemExit(
                    f"{path.name} line {line_no}: answer must match "
                    "verdict=<ALLOW|REVIEW|DENY>;lane=<GREEN|AMBER|RED>;fee=<integer>"
                )
            rows.append((line_no, row))
    return rows


def is_valid_answer(answer: str) -> bool:
    if not isinstance(answer, str):
        return False
    parts = answer.split(";")
    if len(parts) != 3:
        return False
    verdict_part, lane_part, fee_part = parts
    if not verdict_part.startswith("verdict=") or verdict_part.split("=", 1)[1] not in VALID_VERDICTS:
        return False
    if not lane_part.startswith("lane=") or lane_part.split("=", 1)[1] not in VALID_LANES:
        return False
    if not fee_part.startswith("fee="):
        return False
    fee_value = fee_part.split("=", 1)[1]
    return fee_value.isdigit()


def ensure_unique_ids(rows, label: str) -> None:
    seen = {}
    for line_no, row in rows:
        if row["id"] in seen:
            first_line = seen[row["id"]]
            raise SystemExit(f"{label} contains duplicate id {row['id']} on lines {first_line} and {line_no}")
        seen[row["id"]] = line_no


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    gold_rows = load_rows(args.gold)
    pred_rows = load_rows(args.predictions)
    ensure_unique_ids(gold_rows, "gold file")
    ensure_unique_ids(pred_rows, "predictions file")

    gold = {row["id"]: row["answer"] for _, row in gold_rows}
    preds = {row["id"]: row["answer"] for _, row in pred_rows}

    missing = sorted(set(gold) - set(preds))
    extra = sorted(set(preds) - set(gold))
    if missing or extra:
        raise SystemExit(f"id mismatch: missing={missing} extra={extra}")

    details = []
    correct = 0
    for _, row in gold_rows:
        item_id = row["id"]
        is_correct = preds[item_id] == row["answer"]
        if is_correct:
            correct += 1
        details.append({"id": item_id, "correct": is_correct, "gold": row["answer"], "pred": preds[item_id]})

    report = {
        "score": correct,
        "total": len(gold_rows),
        "accuracy": correct / len(gold_rows) if gold_rows else 0.0,
        "details": details,
    }
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"score": correct, "total": len(gold_rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
