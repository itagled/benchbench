#!/usr/bin/env python3
"""Scorer for Rosetta Fieldwork v1.

Deterministic exact-match scoring after light normalization:
lowercase, hyphens removed (so morpheme-segmented answers like "tomi-lar"
still count), all other non-letters treated as separators, whitespace
collapsed. One point per item, no partial credit within an item. A token-F1
diagnostic is reported per item but does not affect the score.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def normalize(s: str) -> str:
    s = s.lower().replace("-", "")
    out = []
    for ch in s:
        out.append(ch if "a" <= ch <= "z" else " ")
    return " ".join("".join(out).split())


def token_f1(pred: str, gold: str) -> float:
    p, g = pred.split(), gold.split()
    if not p or not g:
        return 0.0
    common = 0
    g_remaining = list(g)
    for tok in p:
        if tok in g_remaining:
            g_remaining.remove(tok)
            common += 1
    if common == 0:
        return 0.0
    prec = common / len(p)
    rec = common / len(g)
    return round(2 * prec * rec / (prec + rec), 4)


def load_jsonl(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    golds = load_jsonl(args.gold)
    preds = {}
    for row in load_jsonl(args.predictions):
        preds[row.get("id")] = str(row.get("answer", ""))

    per_item = []
    n_correct = 0
    for g in golds:
        gid = g["id"]
        gold_norm = normalize(g["answer"])
        pred_norm = normalize(preds.get(gid, ""))
        correct = int(pred_norm == gold_norm)
        n_correct += correct
        per_item.append({
            "id": gid,
            "correct": correct,
            "answered": int(gid in preds),
            "token_f1": token_f1(pred_norm, gold_norm),
        })

    report = {
        "benchmark": "rosetta_fieldwork_v1",
        "n_items": len(golds),
        "n_correct": n_correct,
        "score": f"{n_correct}/{len(golds)}",
        "accuracy": round(n_correct / len(golds), 4) if golds else 0.0,
        "mean_token_f1": round(
            sum(r["token_f1"] for r in per_item) / len(per_item), 4)
        if per_item else 0.0,
        "per_item": per_item,
    }
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("benchmark", "n_items", "n_correct", "score",
                       "accuracy", "mean_token_f1")}, indent=2))


if __name__ == "__main__":
    main()
