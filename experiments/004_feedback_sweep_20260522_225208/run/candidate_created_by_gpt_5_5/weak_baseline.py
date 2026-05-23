#!/usr/bin/env python3
"""Naive baseline: use only severity deadlines and default actions."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, timedelta
from pathlib import Path


def biz_add(start: date, days: int) -> date:
    cur = start
    left = days
    while left:
        cur += timedelta(days=1)
        if cur.weekday() < 5:
            left -= 1
    return cur


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    solver_dir = args.items.parent
    rows = [json.loads(line) for line in args.items.read_text(encoding="utf-8").splitlines() if line.strip()]
    with args.out.open("w", encoding="utf-8") as f:
        for row in rows:
            text = (solver_dir / row["dossier_path"]).read_text(encoding="utf-8")
            discovered = date.fromisoformat(re.search(r"opened the case on (\d{4}-\d{2}-\d{2})", text).group(1))
            severity = re.search(r"local register: (\w+)", text).group(1)
            days = {"amber": 10, "red": 5, "critical": 2}[severity]
            answer = {
                "notify_by": biz_add(discovered, days).isoformat(),
                "board_review": "required" if severity == "critical" else "not_required",
                "remediation": "manager_attestation_only",
                "hold": "local_manager_signoff",
                "evidence_codes": [f"severity:{severity}"],
            }
            f.write(json.dumps({"id": row["id"], "answer": answer}, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
