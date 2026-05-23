#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

DECISIONS = {"approve", "reject", "escalate"}
RULES = {"R1", "R2", "R3", "R4", "R5", "R6", "R7", "A1"}


def load_jsonl(path: Path):
    rows = []
    with path.open() as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}")
    return rows


def validate_canonical_answer(answer: str) -> None:
    if not isinstance(answer, str):
        raise SystemExit("answer must be a JSON string")
    try:
        obj = json.loads(answer)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"answer is not valid JSON: {exc}")
    if sorted(obj.keys()) != ["decision", "governing_rule", "responsible_actor"]:
        raise SystemExit("answer must contain exactly decision, governing_rule, and responsible_actor")
    if obj["decision"] not in DECISIONS:
        raise SystemExit(f"invalid decision value: {obj['decision']}")
    if obj["governing_rule"] not in RULES:
        raise SystemExit(f"invalid governing_rule value: {obj['governing_rule']}")
    actor = obj["responsible_actor"]
    if not isinstance(actor, str) or len(actor) != 3 or not actor.isupper():
        raise SystemExit("responsible_actor must be a three-letter uppercase code")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", required=True)
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    gold_rows = load_jsonl(Path(args.gold))
    gold = {}
    for row in gold_rows:
        if sorted(row.keys()) != ["answer", "id"]:
            raise SystemExit("gold rows must include exactly id and answer")
        validate_canonical_answer(row["answer"])
        if row["id"] in gold:
            raise SystemExit(f"duplicate gold id: {row['id']}")
        gold[row["id"]] = row["answer"]

    preds = load_jsonl(Path(args.predictions))

    results = []
    correct = 0
    seen = set()
    for row in preds:
        if sorted(row.keys()) != ["answer", "id"]:
            raise SystemExit("prediction rows must include exactly id and answer")
        validate_canonical_answer(row["answer"])
        if row["id"] in seen:
            raise SystemExit(f"duplicate prediction id: {row['id']}")
        if row["id"] not in gold:
            raise SystemExit(f"unknown prediction id: {row['id']}")
        seen.add(row["id"])
        is_correct = gold.get(row["id"]) == row["answer"]
        correct += int(is_correct)
        results.append({"id": row["id"], "correct": is_correct})

    missing = sorted(set(gold) - seen)
    report = {
        "total_gold": len(gold),
        "predictions_received": len(preds),
        "missing_ids": missing,
        "exact_match": correct,
        "accuracy": correct / len(gold) if gold else 0.0,
        "results": results,
    }
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
