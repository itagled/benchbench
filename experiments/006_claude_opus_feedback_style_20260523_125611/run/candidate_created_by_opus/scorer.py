#!/usr/bin/env python3
"""Exact-match scorer over normalized tokens."""
import argparse, json, sys, re
from pathlib import Path

def load_jsonl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]

def normalize(s):
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    s = re.sub(r"[\.,!\?;:\"\(\)\[\]]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    gold = {g["id"]: g["answer"] for g in load_jsonl(args.gold)}
    preds = {p["id"]: p.get("answer","") for p in load_jsonl(args.predictions)}

    correct = 0
    per_item = []
    for gid, gans in gold.items():
        pans = preds.get(gid, "")
        ok = normalize(pans) == normalize(gans)
        if ok:
            correct += 1
        per_item.append({"id": gid, "correct": ok, "gold": gans, "pred": pans})

    report = {
        "total": len(gold),
        "correct": correct,
        "score": f"{correct}/{len(gold)}",
        "per_item": per_item,
    }
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Score: {correct}/{len(gold)}")

if __name__ == "__main__":
    main()
