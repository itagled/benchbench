#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Iterable, Mapping


RULES_TEXT = """# LCR v1 Rules (solver-visible)

You are given a per-item folder containing:
- `ledger.csv`
- `fx_rates.csv`

Your job: compute final per-account balances in **USD cents** and output a **canonical JSON object string**:
- Keys: every `account_id` that appears anywhere in `ledger.csv`, even if final balance is 0.
- Values: signed integer USD cents.
- Canonical JSON: keys sorted lexicographically (Unicode codepoint order), no extra whitespace.

## Files

### `ledger.csv`
Columns:
- `txn_id` (string): transaction identifier. May repeat (duplicates).
- `posted_at` (string): ISO-8601 UTC timestamp, format `YYYY-MM-DDTHH:MM:SSZ`.
- `account_id` (string): account identifier (ASCII uppercase A-Z plus digits).
- `currency` (string): one of the currencies listed in `fx_rates.csv`.
- `amount_minor` (integer): signed amount in minor units of `currency` (e.g., cents).
- `type` (string): `PAYMENT`, `CHARGE`, `REFUND`, `ADJUSTMENT`, or `REVERSAL`.
- `ref_txn_id` (string): empty unless `type == REVERSAL`, in which case it references a `txn_id`.
- `status` (string): `POSTED` or `VOID`.

### `fx_rates.csv`
Columns:
- `date` (string): `YYYY-MM-DD` in UTC calendar date.
- `currency` (string)
- `usd_per_unit` (decimal string): USD per 1.0 unit of the currency. Example: `1.0735`

Rates are provided for multiple dates per currency.

## Computation

### Step 0: parse rows
Ignore ledger rows with `status == VOID`.

### Step 1: de-duplicate `txn_id`
If multiple POSTED rows share the same `txn_id`, keep **only** the row with the earliest `posted_at` timestamp (strictly earliest). Discard all later rows with that `txn_id` entirely.

### Step 2: apply reversal semantics
After de-duplication:
- A row with `type == REVERSAL` cancels (removes) the referenced transaction identified by `ref_txn_id`.
- Cancellation means: the referenced transaction contributes **0** to the final balances.
- The reversal row itself also contributes **0** to final balances.
- If multiple reversal rows reference the same `ref_txn_id`, the first one in increasing `posted_at` order is effective; later ones do nothing extra.
- If a reversal references a `ref_txn_id` that does not exist after de-duplication, it has no effect (still contributes 0).

### Step 3: FX conversion
For each non-canceled, non-REVERSAL transaction row, convert `amount_minor` to USD cents:
1. Let `d` be the UTC calendar date of `posted_at` (the `YYYY-MM-DD` portion).
2. Select the FX rate for (currency, date) using:
   - Choose the rate whose `date` is the **latest date <= d**.
   - It is guaranteed such a rate exists for every row.
3. Convert:
   - amount_units = amount_minor / minor_per_unit
   - usd = amount_units * usd_per_unit
   - usd_cents = round_to_nearest_int(usd * 100) with ties **away from zero**

Minor units per currency are:
- USD, EUR, GBP: 100
- JPY: 1

### Step 4: account aggregation
Sum USD cents per `account_id`.

## Output
Return the canonical JSON object string described at top.
"""


MINOR_PER_UNIT: dict[str, int] = {"USD": 100, "EUR": 100, "GBP": 100, "JPY": 1}


def _round_ties_away_from_zero(x: float) -> int:
    if x >= 0:
        return int(x + 0.5)
    return int(x - 0.5)


@dataclass(frozen=True)
class LedgerRow:
    txn_id: str
    posted_at: datetime
    account_id: str
    currency: str
    amount_minor: int
    type: str
    ref_txn_id: str
    status: str


def _parse_ts(ts: str) -> datetime:
    # Format: 2026-01-02T03:04:05Z
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")


def _canonical_json(obj: Mapping[str, int]) -> str:
    # json.dumps with sort_keys uses Python's key ordering; ensure keys are strings.
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _load_fx_rates(path: Path) -> dict[str, list[tuple[date, float]]]:
    rates: dict[str, list[tuple[date, float]]] = {}
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = datetime.strptime(row["date"], "%Y-%m-%d").date()
            ccy = row["currency"]
            usd_per_unit = float(row["usd_per_unit"])
            rates.setdefault(ccy, []).append((d, usd_per_unit))
    for ccy in rates:
        rates[ccy].sort(key=lambda t: t[0])
    return rates


def _fx_for_date(rates: dict[str, list[tuple[date, float]]], ccy: str, d: date) -> float:
    series = rates[ccy]
    # latest <= d; guaranteed exists.
    lo = 0
    hi = len(series) - 1
    best = series[0][1]
    while lo <= hi:
        mid = (lo + hi) // 2
        md, mv = series[mid]
        if md <= d:
            best = mv
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def compute_answer(ledger_rows: list[LedgerRow], fx_rates_path: Path) -> str:
    # Step 0: ignore VOID
    posted = [r for r in ledger_rows if r.status == "POSTED"]

    # Step 1: dedupe by txn_id, keep earliest posted_at
    by_id: dict[str, LedgerRow] = {}
    for r in posted:
        prev = by_id.get(r.txn_id)
        if prev is None or r.posted_at < prev.posted_at:
            by_id[r.txn_id] = r
    deduped = list(by_id.values())

    # Step 2: reversals
    deduped.sort(key=lambda r: r.posted_at)
    canceled: set[str] = set()
    reversed_once: set[str] = set()
    for r in deduped:
        if r.type != "REVERSAL":
            continue
        target = r.ref_txn_id
        if not target or target in reversed_once:
            continue
        reversed_once.add(target)
        if target in by_id:
            canceled.add(target)

    # Step 3+4: fx + aggregate
    rates = _load_fx_rates(fx_rates_path)
    accounts: set[str] = set(r.account_id for r in ledger_rows)  # includes VOID too, per rules
    balances: dict[str, int] = {a: 0 for a in accounts}
    for r in deduped:
        if r.txn_id in canceled:
            continue
        if r.type == "REVERSAL":
            continue
        minor_per_unit = MINOR_PER_UNIT[r.currency]
        d = r.posted_at.date()
        fx = _fx_for_date(rates, r.currency, d)
        usd = (r.amount_minor / minor_per_unit) * fx
        usd_cents = _round_ties_away_from_zero(usd * 100.0)
        balances[r.account_id] += usd_cents

    return _canonical_json(balances)


def _write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _make_item(rng: random.Random, item_id: str, out_solver_dir: Path) -> tuple[list[LedgerRow], Path, dict[str, str]]:
    currencies = ["USD", "EUR", "GBP", "JPY"]
    account_count = rng.randint(5, 12)
    accounts = [f"A{rng.randint(10,99)}{chr(ord('A')+i)}" for i in range(account_count)]

    # FX rates over a short window
    base_day = date(2026, 1, 1) + timedelta(days=rng.randint(0, 80))
    fx_rows: list[dict[str, str]] = []
    fx_by_ccy: dict[str, list[tuple[date, float]]] = {}
    for ccy in currencies:
        days = sorted({base_day + timedelta(days=rng.randint(0, 25)) for _ in range(rng.randint(6, 10))})
        for d in days:
            if ccy == "USD":
                rate = 1.0
            elif ccy == "EUR":
                rate = rng.uniform(0.95, 1.15)
            elif ccy == "GBP":
                rate = rng.uniform(1.15, 1.40)
            else:  # JPY
                rate = rng.uniform(0.0060, 0.0105)
            rate = round(rate, 6)
            fx_rows.append({"date": d.isoformat(), "currency": ccy, "usd_per_unit": f"{rate:.6f}"})
            fx_by_ccy.setdefault(ccy, []).append((d, rate))
    fx_rows.sort(key=lambda r: (r["currency"], r["date"]))

    item_dir = out_solver_dir / "items" / item_id
    fx_path = item_dir / "fx_rates.csv"
    _write_csv(fx_path, ["date", "currency", "usd_per_unit"], fx_rows)

    # Ledger: generate with duplicates, voids, reversals, out-of-order times
    start_ts = datetime.combine(base_day, datetime.min.time())
    ledger_rows: list[LedgerRow] = []
    ledger_csv_rows: list[dict[str, str]] = []

    txn_ids: list[str] = []
    txn_count = rng.randint(26, 44)
    for i in range(txn_count):
        txn_id = f"T{rng.randint(10000, 99999)}_{i}"
        txn_ids.append(txn_id)
        posted_at = start_ts + timedelta(hours=rng.randint(0, 24 * 25), minutes=rng.randint(0, 59), seconds=rng.randint(0, 59))
        account_id = rng.choice(accounts)
        ccy = rng.choice(currencies)
        minor_per_unit = MINOR_PER_UNIT[ccy]
        # amounts: keep modest; include negatives
        units = rng.randint(-2500, 2500) / 10.0  # -250.0..250.0
        if ccy == "JPY":
            units = rng.randint(-25000, 25000)  # integer
        amount_minor = int(round(units * minor_per_unit))
        if amount_minor == 0:
            amount_minor = minor_per_unit
        typ = rng.choices(["PAYMENT", "CHARGE", "REFUND", "ADJUSTMENT"], weights=[3, 3, 2, 2])[0]
        status = "VOID" if rng.random() < 0.10 else "POSTED"
        ref = ""
        row = LedgerRow(
            txn_id=txn_id,
            posted_at=posted_at,
            account_id=account_id,
            currency=ccy,
            amount_minor=amount_minor,
            type=typ,
            ref_txn_id=ref,
            status=status,
        )
        ledger_rows.append(row)

    # Add some duplicates with later timestamps (conflicting amounts), some earlier too.
    dup_count = rng.randint(5, 10)
    for _ in range(dup_count):
        base = rng.choice(ledger_rows)
        # sometimes earlier, sometimes later; earliest should win
        delta_hours = rng.choice([-48, -24, -3, 2, 12, 36])
        posted_at = base.posted_at + timedelta(hours=delta_hours, minutes=rng.randint(0, 30))
        new_amount = base.amount_minor + rng.randint(-5000, 5000)
        if new_amount == 0:
            new_amount = base.amount_minor
        status = base.status if rng.random() < 0.8 else ("VOID" if base.status == "POSTED" else "POSTED")
        ledger_rows.append(
            LedgerRow(
                txn_id=base.txn_id,
                posted_at=posted_at,
                account_id=base.account_id,
                currency=base.currency,
                amount_minor=new_amount,
                type=base.type,
                ref_txn_id="",
                status=status,
            )
        )

    # Add reversals: reference some txn_ids; include duplicate reversals; include non-existent references
    reversal_targets = rng.sample(txn_ids, k=rng.randint(6, 10))
    for t in reversal_targets:
        posted_at = start_ts + timedelta(hours=rng.randint(0, 24 * 25), minutes=rng.randint(0, 59), seconds=rng.randint(0, 59))
        ledger_rows.append(
            LedgerRow(
                txn_id=f"R{rng.randint(10000,99999)}_{t}",
                posted_at=posted_at,
                account_id=rng.choice(accounts),
                currency=rng.choice(currencies),
                amount_minor=rng.randint(-5000, 5000),
                type="REVERSAL",
                ref_txn_id=t,
                status="POSTED",
            )
        )
        if rng.random() < 0.35:
            # duplicate reversal later
            ledger_rows.append(
                LedgerRow(
                    txn_id=f"R{rng.randint(10000,99999)}_{t}_DUP",
                    posted_at=posted_at + timedelta(hours=rng.randint(1, 40)),
                    account_id=rng.choice(accounts),
                    currency=rng.choice(currencies),
                    amount_minor=rng.randint(-5000, 5000),
                    type="REVERSAL",
                    ref_txn_id=t,
                    status="POSTED",
                )
            )
    # some reversals to missing ids
    for _ in range(rng.randint(1, 3)):
        posted_at = start_ts + timedelta(hours=rng.randint(0, 24 * 25))
        ledger_rows.append(
            LedgerRow(
                txn_id=f"R{rng.randint(10000,99999)}_MISSING",
                posted_at=posted_at,
                account_id=rng.choice(accounts),
                currency=rng.choice(currencies),
                amount_minor=rng.randint(-5000, 5000),
                type="REVERSAL",
                ref_txn_id=f"T_MISSING_{rng.randint(1,999)}",
                status="POSTED",
            )
        )

    # Serialize ledger.csv in shuffled order (out-of-order timestamps)
    rng.shuffle(ledger_rows)
    for r in ledger_rows:
        ledger_csv_rows.append(
            {
                "txn_id": r.txn_id,
                "posted_at": r.posted_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "account_id": r.account_id,
                "currency": r.currency,
                "amount_minor": str(r.amount_minor),
                "type": r.type,
                "ref_txn_id": r.ref_txn_id,
                "status": r.status,
            }
        )
    ledger_path = item_dir / "ledger.csv"
    _write_csv(
        ledger_path,
        ["txn_id", "posted_at", "account_id", "currency", "amount_minor", "type", "ref_txn_id", "status"],
        ledger_csv_rows,
    )

    rules_path = item_dir / "rules.md"
    rules_path.write_text(RULES_TEXT, encoding="utf-8")

    manifest = {
        "id": item_id,
        "ledger_csv": str(Path("items") / item_id / "ledger.csv"),
        "fx_rates_csv": str(Path("items") / item_id / "fx_rates.csv"),
        "rules_md": str(Path("items") / item_id / "rules.md"),
        "sha256": {
            "ledger.csv": _sha256_file(ledger_path),
            "fx_rates.csv": _sha256_file(fx_path),
            "rules.md": _sha256_file(rules_path),
        },
    }
    return ledger_rows, fx_path, manifest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-count", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out-dir", type=str, required=True)
    args = ap.parse_args()

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)

    solver_dir = out_dir / "solver_bundle"
    solver_dir.mkdir(parents=True, exist_ok=True)
    (solver_dir / "items").mkdir(parents=True, exist_ok=True)

    # Shared solver-bundle docs
    (solver_dir / "README.md").write_text(
        "# LCR v1 Solver Bundle\n\n"
        "This bundle contains the only files a solver is allowed to read.\n\n"
        "Inputs:\n"
        "- `items_private_sample.jsonl`: the list of items and relative asset paths\n"
        "- `items/<id>/ledger.csv`\n"
        "- `items/<id>/fx_rates.csv`\n"
        "- `items/<id>/rules.md`\n\n"
        "Task: for each item, compute the canonical JSON answer string described in `rules.md`.\n",
        encoding="utf-8",
    )

    items_path = solver_dir / "items_private_sample.jsonl"
    gold_path = out_dir / "gold_private_sample.jsonl"
    solver_manifest_path = solver_dir / "SOLVER_MANIFEST.json"

    solver_items: list[dict[str, object]] = []
    gold_rows: list[dict[str, str]] = []

    for i in range(args.sample_count):
        item_id = f"lcr_{args.seed}_{i:02d}"
        ledger_rows, fx_path, item_manifest = _make_item(rng, item_id, solver_dir)
        answer = compute_answer(ledger_rows, fx_path)
        solver_items.append(item_manifest)
        gold_rows.append({"id": item_id, "answer": answer})

    # Write solver items jsonl
    with items_path.open("w", encoding="utf-8") as f:
        for row in solver_items:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Write gold jsonl
    with gold_path.open("w", encoding="utf-8") as f:
        for row in gold_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    solver_manifest = {
        "benchmark_id": "ledger_canonical_reconciliation_v1",
        "bundle_version": "1.0.0",
        "contains": [
            "items_private_sample.jsonl",
            "items/<id>/ledger.csv",
            "items/<id>/fx_rates.csv",
            "items/<id>/rules.md"
        ],
        "explicitly_not_included": [
            "gold answers",
            "generator/verifier/scorer code",
            "validation reports",
            "any hidden labels"
        ]
    }
    solver_manifest_path.write_text(json.dumps(solver_manifest, indent=2) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
