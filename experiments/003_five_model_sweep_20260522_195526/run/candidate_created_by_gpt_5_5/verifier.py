#!/usr/bin/env python3
"""Package verifier for Amendment Ledger Reconciliation."""

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
            if not line.strip():
                continue
            row = json.loads(line)
            rows.append(row)
            if path.name.startswith("gold") and set(row) != {"id", "answer"}:
                raise AssertionError(f"{path}:{line_no} gold rows must contain exactly id and answer")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", required=True)
    parser.add_argument("--gold", required=True)
    args = parser.parse_args()

    items_path = Path(args.items)
    gold_path = Path(args.gold)
    items = read_jsonl(items_path)
    gold = read_jsonl(gold_path)
    gold_by_id = {row["id"]: row["answer"] for row in gold}

    assert len(items) == len(gold), "item/gold count mismatch"
    assert len(gold_by_id) == len(gold), "duplicate gold id"

    item_ids = set()
    for row in items:
        assert "id" in row, "item missing id"
        assert row["id"] not in item_ids, f"duplicate item id {row['id']}"
        item_ids.add(row["id"])
        required = {"id", "answer_format", "task", "decision_rules", "base_code", "amendments", "case_file"}
        assert required.issubset(row), f"{row['id']} missing required item fields"
        assert row["id"] in gold_by_id, f"{row['id']} missing gold"
        assert "answer" not in row, f"{row['id']} leaks answer field"
        assert len(row["amendments"]) >= 7, f"{row['id']} has too few amendments"
        assert ANSWER_RE.match(str(gold_by_id[row["id"]])), f"{row['id']} malformed gold answer"

    bundle_dir = items_path.parent
    forbidden_names = {
        "gold_private_sample.jsonl",
        "private_audit_traces.jsonl",
        "generator.py",
        "verifier.py",
        "scorer.py",
        "validation_report.md",
        "failure_modes.md",
    }
    leaks = [p.name for p in bundle_dir.iterdir() if p.name in forbidden_names]
    assert not leaks, f"solver bundle contains forbidden files: {leaks}"

    joined = "\n".join(json.dumps(row, sort_keys=True) for row in items)
    for answer in gold_by_id.values():
        assert str(answer) not in joined, "a gold answer appears verbatim in solver items"
    assert "solution" not in joined.lower(), "solver items contain solution-label wording"

    print(f"verified {len(items)} items")


if __name__ == "__main__":
    main()
