#!/usr/bin/env python
"""Scorer: compare predictions to gold, output score_report.json.

Each prediction row has {"id", "answer"}. Score is exact-match on the
integer `answer` field (minimum number of rule applications).
Missing predictions count as wrong.
"""
import argparse
import json


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gold", required=True)
    p.add_argument("--predictions", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    gold = {g["id"]: g["answer"] for g in load_jsonl(args.gold)}
    try:
        preds = {p_["id"]: p_["answer"] for p_ in load_jsonl(args.predictions)}
    except FileNotFoundError:
        preds = {}

    correct = 0
    per_item = []
    for iid, gans in gold.items():
        pans = preds.get(iid)
        ok = (pans == gans)
        if ok:
            correct += 1
        per_item.append({"id": iid, "gold": gans, "pred": pans, "correct": ok})

    total = len(gold)
    report = {
        "score": correct,
        "total": total,
        "accuracy": correct / total if total else 0.0,
        "per_item": per_item,
    }
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Score: {correct}/{total}")


if __name__ == "__main__":
    main()
