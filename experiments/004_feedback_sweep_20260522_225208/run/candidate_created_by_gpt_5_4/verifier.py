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
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}")
    return rows


def parse_canonical_answer(answer: str) -> dict:
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
    return obj


def validate_item_row(row: dict, bundle_dir: Path) -> None:
    if sorted(row.keys()) != ["id", "packet_dir", "policy_path", "question"]:
        raise SystemExit("item rows must include exactly id, packet_dir, policy_path, and question")
    item_id = row["id"]
    if not isinstance(item_id, str) or not item_id:
        raise SystemExit("item id must be a non-empty string")
    if not isinstance(row["question"], str) or not row["question"].strip():
        raise SystemExit(f"question for {item_id} must be a non-empty string")
    policy_path = Path(row["policy_path"])
    packet_dir = Path(row["packet_dir"])
    if policy_path.is_absolute() or packet_dir.is_absolute():
        raise SystemExit(f"item {item_id} uses absolute solver-bundle paths")
    policy_file = (bundle_dir / policy_path).resolve()
    packet_path = (bundle_dir / packet_dir).resolve()
    bundle_root = bundle_dir.resolve()
    if bundle_root not in policy_file.parents or bundle_root not in packet_path.parents:
        raise SystemExit(f"item {item_id} points outside the solver bundle")
    if not policy_file.is_file():
        raise SystemExit(f"policy file for {item_id} does not exist: {row['policy_path']}")
    if not packet_path.is_dir():
        raise SystemExit(f"packet dir for {item_id} does not exist: {row['packet_dir']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", required=True)
    parser.add_argument("--gold", required=True)
    args = parser.parse_args()

    items = load_jsonl(Path(args.items))
    gold = load_jsonl(Path(args.gold))
    bundle_dir = Path(args.items).resolve().parent

    item_ids = [row.get("id") for row in items]
    gold_ids = [row.get("id") for row in gold]

    if len(item_ids) != len(set(item_ids)):
        raise SystemExit("duplicate item ids in items file")
    if len(gold_ids) != len(set(gold_ids)):
        raise SystemExit("duplicate item ids in gold file")
    if set(item_ids) != set(gold_ids):
        raise SystemExit("items and gold ids do not match")

    for row in items:
        validate_item_row(row, bundle_dir)

    for row in gold:
        if sorted(row.keys()) != ["answer", "id"]:
            raise SystemExit("gold rows must include exactly id and answer")
        parse_canonical_answer(row["answer"])

    print(json.dumps({"status": "ok", "item_count": len(items)}, indent=2))


if __name__ == "__main__":
    main()
