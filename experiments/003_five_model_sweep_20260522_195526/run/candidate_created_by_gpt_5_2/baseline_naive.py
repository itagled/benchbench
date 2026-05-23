#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path


MINOR_PER_UNIT = {"USD": 100, "EUR": 100, "GBP": 100, "JPY": 1}


def _load_fx_exact(path: Path) -> dict[tuple[str, str], float]:
    # Naive: only uses exact same-day rates; if missing, falls back to 1.0.
    out: dict[tuple[str, str], float] = {}
    with path.open("r", newline="") as f:
        for row in csv.DictReader(f):
            out[(row["currency"], row["date"])] = float(row["usd_per_unit"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True, type=str)
    ap.add_argument("--out", required=True, type=str)
    args = ap.parse_args()

    items_path = Path(args.items)
    out_path = Path(args.out)

    preds: list[dict[str, str]] = []
    with items_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            item_id = item["id"]
            base = items_path.parent
            ledger_path = base / item["ledger_csv"]
            fx_path = base / item["fx_rates_csv"]
            fx = _load_fx_exact(fx_path)

            balances: dict[str, int] = {}
            with ledger_path.open("r", newline="") as lf:
                for row in csv.DictReader(lf):
                    # Naive mistakes:
                    # - ignores VOID
                    # - does not dedupe txn_id
                    # - ignores REVERSAL semantics (treats as normal row)
                    ccy = row["currency"]
                    minor = int(row["amount_minor"])
                    d = datetime.strptime(row["posted_at"], "%Y-%m-%dT%H:%M:%SZ").date().isoformat()
                    rate = fx.get((ccy, d), 1.0)
                    usd = (minor / MINOR_PER_UNIT[ccy]) * rate
                    usd_cents = int(usd * 100)  # truncation, wrong rounding
                    acct = row["account_id"]
                    balances[acct] = balances.get(acct, 0) + usd_cents

            ans = json.dumps(balances, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            preds.append({"id": item_id, "answer": ans})

    with out_path.open("w", encoding="utf-8") as f:
        for r in preds:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
