#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ITEM_KEYS = {"id", "shared_rules", "charter", "amendments", "case_file"}
GOLD_KEYS = {"id", "answer"}
ANSWER_PREFIXES = (
    "verdict=ALLOW;lane=",
    "verdict=REVIEW;lane=",
    "verdict=DENY;lane=",
)
LANE_MARKERS = (";lane=GREEN;fee=", ";lane=AMBER;fee=", ";lane=RED;fee=")


def load_jsonl(path: Path):
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
            rows.append((line_no, row))
    return rows


def is_valid_answer(answer: str) -> bool:
    if not isinstance(answer, str):
        return False
    if not answer.startswith(ANSWER_PREFIXES):
        return False
    lane_marker = next((marker for marker in LANE_MARKERS if marker in answer), None)
    if lane_marker is None:
        return False
    fee_text = answer.split(lane_marker, 1)[1]
    return fee_text.isdigit()


def resolve_bundle_path(bundle_root: Path, rel_path: str, line_no: int, key: str) -> Path:
    if not isinstance(rel_path, str) or not rel_path:
        raise SystemExit(f"items line {line_no}: {key} must be a non-empty relative path string")
    candidate = Path(rel_path)
    if candidate.is_absolute():
        raise SystemExit(f"items line {line_no}: {key} must be relative, got absolute path {rel_path}")
    if ".." in candidate.parts:
        raise SystemExit(f"items line {line_no}: {key} must not escape the solver bundle: {rel_path}")
    resolved = (bundle_root / candidate).resolve()
    try:
        resolved.relative_to(bundle_root.resolve())
    except ValueError as exc:
        raise SystemExit(f"items line {line_no}: {key} escapes the solver bundle: {rel_path}") from exc
    return resolved


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    args = parser.parse_args()

    item_rows = load_jsonl(args.items)
    gold_rows = load_jsonl(args.gold)
    bundle_root = args.items.parent.resolve()

    item_ids = []
    shared_rules_refs = set()
    for line_no, row in item_rows:
        if set(row.keys()) != ITEM_KEYS:
            raise SystemExit(f"items line {line_no}: expected keys {sorted(ITEM_KEYS)}, got {sorted(row.keys())}")
        item_id = row["id"]
        if not isinstance(item_id, str) or not item_id:
            raise SystemExit(f"items line {line_no}: id must be a non-empty string")
        item_ids.append(item_id)
        for key in ["shared_rules", "charter", "amendments", "case_file"]:
            resolved = resolve_bundle_path(bundle_root, row[key], line_no, key)
            if not resolved.is_file():
                raise SystemExit(f"items line {line_no}: missing file {row[key]}")
        shared_rules_refs.add(row["shared_rules"])

    if not item_rows:
        raise SystemExit("items file must contain at least one item")
    if len(shared_rules_refs) != 1:
        raise SystemExit("items file must reference exactly one shared_rules path across all items")

    gold_ids = []
    for line_no, row in gold_rows:
        if set(row.keys()) != GOLD_KEYS:
            raise SystemExit(f"gold line {line_no}: expected keys {sorted(GOLD_KEYS)}, got {sorted(row.keys())}")
        item_id = row["id"]
        if not isinstance(item_id, str) or not item_id:
            raise SystemExit(f"gold line {line_no}: id must be a non-empty string")
        if not is_valid_answer(row["answer"]):
            raise SystemExit(f"gold line {line_no}: answer must match verdict/lane/fee canonical format")
        gold_ids.append(item_id)

    if len(set(item_ids)) != len(item_ids):
        raise SystemExit("items file contains duplicate ids")
    if len(set(gold_ids)) != len(gold_ids):
        raise SystemExit("gold file contains duplicate ids")
    if item_ids != gold_ids:
        raise SystemExit("item ids and gold ids do not match in order")

    print(json.dumps({"ok": True, "item_count": len(item_ids)}, sort_keys=True))


if __name__ == "__main__":
    main()
