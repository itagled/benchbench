#!/usr/bin/env python3
"""Structural verifier and leakage check for the benchmark package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PRIVATE_TOKENS = ["gold_private", "private_audit", "private_audit_traces", '"correct"', '"gold"']


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    args = parser.parse_args()

    items = read_jsonl(args.items)
    gold = read_jsonl(args.gold)
    item_ids = []
    solver_dir = args.items.parent
    for row in items:
        if set(row) != {"id", "dossier_path"}:
            raise SystemExit(f"item row must contain exactly id and dossier_path: {row}")
        item_ids.append(row["id"])
        dossier = solver_dir / row["dossier_path"]
        if not dossier.is_file():
            raise SystemExit(f"missing dossier: {row['dossier_path']}")
        text = dossier.read_text(encoding="utf-8")
        if row["id"] not in text:
            raise SystemExit(f"dossier does not contain its item id: {row['id']}")
    gold_ids = []
    for row in gold:
        if set(row) != {"id", "answer"}:
            raise SystemExit(f"gold row must contain exactly id and answer: {row}")
        gold_ids.append(row["id"])
        if not isinstance(row["answer"], str):
            raise SystemExit(f"gold answer must be a JSON string for {row['id']}")
        json.loads(row["answer"])
    if item_ids != gold_ids:
        raise SystemExit("items and gold ids differ or are not in identical order")

    manifest = solver_dir / "SOLVER_MANIFEST.json"
    if not manifest.is_file():
        raise SystemExit("missing solver bundle manifest")
    forbidden_names = {"gold_private_sample.jsonl", "generator.py", "verifier.py", "scorer.py", "private_audit_traces.jsonl"}
    for path in solver_dir.rglob("*"):
        if path.is_file() and path.name in forbidden_names:
            raise SystemExit(f"forbidden private file leaked into solver bundle: {path}")
    for path in solver_dir.rglob("*"):
        if path.is_file() and path.suffix in {".json", ".jsonl", ".md", ".txt"}:
            text = path.read_text(encoding="utf-8")
            if path.name == "solver_packet.md":
                continue
            if path.name == "SOLVER_MANIFEST.json":
                continue
            for token in PRIVATE_TOKENS:
                if token in text and path.name != "items_private_sample.jsonl":
                    raise SystemExit(f"possible answer leakage token {token!r} in {path}")
    print(f"verified {len(items)} items")


if __name__ == "__main__":
    main()
