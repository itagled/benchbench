#!/usr/bin/env python3
"""Generate the Cross-Document Obligation Resolution benchmark sample."""

from __future__ import annotations

import argparse
import json
import random
import shutil
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


REGIONS = ["Northbridge", "Eastport", "South Vale", "Westmere", "Central Borough"]
CHANNELS = ["clinic", "web portal", "phone desk", "field kiosk", "partner API"]
EVENTS = ["missed handoff", "late consent", "record mismatch", "duplicate intake", "escalation delay"]
CAUSES = ["vendor outage", "staffing shortfall", "client no-show", "software migration", "weather closure"]
SEVERITIES = ["amber", "red", "critical"]


@dataclass(frozen=True)
class Item:
    item_id: str
    dossier: str
    answer: dict
    audit: dict


def iso(d: date) -> str:
    return d.isoformat()


def biz_add(start: date, days: int) -> date:
    cur = start
    left = days
    while left:
        cur += timedelta(days=1)
        if cur.weekday() < 5:
            left -= 1
    return cur


def make_item(rng: random.Random, idx: int) -> Item:
    item_id = f"cdor-{idx:03d}"
    region = rng.choice(REGIONS)
    channel = rng.choice(CHANNELS)
    event = rng.choice(EVENTS)
    cause = rng.choice(CAUSES)
    severity = rng.choice(SEVERITIES)
    incident = date(2026, rng.choice([1, 2, 3, 4]), rng.randint(3, 24))
    discovery_lag = rng.randint(0, 4)
    discovered = incident + timedelta(days=discovery_lag)
    affected = rng.randint(8, 240)
    vulnerable = rng.choice([True, False])
    cross_region = rng.choice([True, False])
    previous_90 = rng.choice([0, 1, 2])
    consent_gap = event == "late consent" or rng.random() < 0.2
    system_error = cause in {"vendor outage", "software migration"} or rng.random() < 0.25
    duplicate = event == "duplicate intake"

    base_days = {"amber": 10, "red": 5, "critical": 2}[severity]
    notify_days = base_days
    triggers = [f"severity:{severity}"]

    if affected >= 100:
        notify_days = min(notify_days, 3)
        triggers.append("volume>=100")
    if vulnerable:
        notify_days = min(notify_days, 4)
        triggers.append("vulnerable_population")
    if cross_region:
        notify_days = min(notify_days, 2)
        triggers.append("cross_region")
    if previous_90 >= 2:
        notify_days = min(notify_days, 1)
        triggers.append("repeat_incident")
    if system_error and severity == "amber" and affected < 50 and not vulnerable:
        notify_days += 2
        triggers.append("amber_system_grace")

    due = biz_add(discovered, notify_days)

    if severity == "critical" or cross_region or previous_90 >= 2:
        board = "required"
    elif severity == "red" and (affected >= 100 or vulnerable):
        board = "conditional_required"
    else:
        board = "not_required"

    if consent_gap and vulnerable:
        remediation = "individual_notice_and_consent_repair"
    elif duplicate:
        remediation = "merge_and_audit_duplicate_records"
    elif system_error:
        remediation = "system_fix_with_retrospective_sample"
    else:
        remediation = "manager_attestation_only"

    if severity == "critical" and affected >= 100:
        hold = "freeze_new_intake"
    elif previous_90 >= 2 and event != "missed handoff":
        hold = "regional_supervisor_signoff"
    elif cause == "client no-show" and severity == "amber":
        hold = "none"
    else:
        hold = "local_manager_signoff"

    answer = {
        "notify_by": iso(due),
        "board_review": board,
        "remediation": remediation,
        "hold": hold,
        "evidence_codes": sorted(triggers),
    }

    # Solver-visible prose intentionally varies order and includes superseded clauses.
    memo_date = incident - timedelta(days=rng.randint(30, 90))
    amendment_date = incident - timedelta(days=rng.randint(5, 20))
    fragments = [
        f"# Dossier {item_id}: Incident Reconciliation Packet\n",
        "## Intake Note\n",
        f"Region: {region}. Channel: {channel}. Incident type: {event}. Cause logged by intake: {cause}.\n",
        f"The operating date was {iso(incident)}; quality office opened the case on {iso(discovered)}. "
        f"The affected count currently stands at {affected}. Severity entered in the local register: {severity}.\n",
        f"Vulnerable-population flag: {'yes' if vulnerable else 'no'}. Cross-region service touch: {'yes' if cross_region else 'no'}. "
        f"Comparable incidents in the preceding 90 days: {previous_90}. Consent repair flag: {'yes' if consent_gap else 'no'}.\n\n",
        "## Procedure Manual Excerpt, effective before current amendments\n",
        f"Manual date {iso(memo_date)}. Amber matters are normally due in 10 business days after discovery; red matters in 5; critical matters in 2. "
        "A board review was originally required only for critical matters. Local manager signoff was the ordinary hold.\n\n",
        "## Amendment Log\n",
        f"Amendment posted {iso(amendment_date)}. Where affected count is at least 100, notification must be no later than 3 business days. "
        "A vulnerable-population flag shortens the outside limit to 4 business days. Cross-region service touch shortens it to 2 business days. "
        "Two or more comparable incidents in the prior 90 days shortens it to 1 business day. Apply the strictest live deadline, not the most recent sentence.\n",
        "For amber matters caused by vendor outage or software migration, add a 2-business-day grace period only if affected count is below 50 and there is no vulnerable-population flag. "
        "This grace rule never extends red or critical cases.\n\n",
        "## Board and Hold Rules\n",
        "Board review is required for critical matters, cross-region matters, and repeat incidents with at least two comparable incidents in 90 days. "
        "For red matters, board review is conditionally required when either count is at least 100 or a vulnerable group is involved. Otherwise it is not required.\n",
        "Freeze new intake for critical cases with count at least 100. Require regional supervisor signoff for repeat incidents with two or more prior comparables unless the incident type is missed handoff. "
        "For amber client-no-show cases, no hold is imposed. All remaining cases use local manager signoff.\n\n",
        "## Remediation Rules\n",
        "If consent repair is flagged and a vulnerable group is involved, use individual_notice_and_consent_repair. "
        "If the incident is duplicate intake and that first rule does not apply, use merge_and_audit_duplicate_records. "
        "If the cause is vendor outage or software migration and neither earlier remediation applies, use system_fix_with_retrospective_sample. "
        "All other cases use manager_attestation_only.\n\n",
        "## Required Answer Format\n",
        "Return one JSON object with exactly these keys: notify_by, board_review, remediation, hold, evidence_codes. "
        "Dates must be ISO YYYY-MM-DD. evidence_codes must be a sorted list of the public trigger codes that set the notification deadline.\n",
    ]
    audit = {
        "region": region,
        "channel": channel,
        "event": event,
        "cause": cause,
        "severity": severity,
        "incident": iso(incident),
        "discovered": iso(discovered),
        "affected": affected,
        "vulnerable": vulnerable,
        "cross_region": cross_region,
        "previous_90": previous_90,
        "consent_gap": consent_gap,
        "system_error": system_error,
        "notify_days": notify_days,
    }
    return Item(item_id=item_id, dossier="".join(fragments), answer=answer, audit=audit)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def generate(sample_count: int, seed: int, out_dir: Path) -> None:
    rng = random.Random(seed)
    solver_dir = out_dir / "solver_bundle"
    assets_dir = solver_dir / "assets"
    if solver_dir.exists():
        shutil.rmtree(solver_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)

    items = [make_item(rng, i + 1) for i in range(sample_count)]
    public_rows = []
    gold_rows = []
    audit_rows = []
    for item in items:
        asset = f"assets/{item.item_id}.md"
        (solver_dir / asset).write_text(item.dossier, encoding="utf-8")
        public_rows.append({"id": item.item_id, "dossier_path": asset})
        gold_rows.append({"id": item.item_id, "answer": json.dumps(item.answer, sort_keys=True, separators=(",", ":"))})
        audit_rows.append({"id": item.item_id, "audit": item.audit, "answer": item.answer})

    write_jsonl(solver_dir / "items_private_sample.jsonl", public_rows)
    write_jsonl(out_dir / "gold_private_sample.jsonl", gold_rows)
    write_jsonl(out_dir / "private_audit_traces.jsonl", audit_rows)
    manifest = {
        "benchmark": "Cross-Document Obligation Resolution",
        "version": "1.0",
        "sample_count": sample_count,
        "items_file": "items_private_sample.jsonl",
        "asset_root": "assets",
        "prediction_schema": {"id": "string", "answer": "canonical JSON string or object"},
        "forbidden_files": ["gold_private_sample.jsonl", "generator.py", "verifier.py", "scorer.py", "private_audit_traces.jsonl"],
    }
    (solver_dir / "SOLVER_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (solver_dir / "solver_packet.md").write_text(SOLVER_PACKET, encoding="utf-8")


SOLVER_PACKET = """# Cross-Document Obligation Resolution Solver Packet

You receive one markdown dossier per item. Each dossier contains all facts and all live rules needed to answer the item.

For each item, submit one JSONL row with exactly:

```json
{"id":"cdor-001","answer":{"notify_by":"YYYY-MM-DD","board_review":"required","remediation":"...","hold":"...","evidence_codes":["..."]}}
```

The `answer` may also be a JSON-encoded string containing the same object. Use only the public dossier. Do not infer from item order or from any generator.

Business days exclude Saturdays and Sundays. No public holidays are used.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-count", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    generate(args.sample_count, args.seed, args.out_dir)


if __name__ == "__main__":
    main()
