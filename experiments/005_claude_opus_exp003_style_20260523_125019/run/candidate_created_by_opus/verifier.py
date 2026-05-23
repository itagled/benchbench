#!/usr/bin/env python
"""Verifier for String Rewriting Distance benchmark.

Checks:
 - items file is well-formed JSONL with required fields
 - gold file is well-formed JSONL with `id` and `answer`
 - ids match 1-1 between items and gold
 - every rule has a length-2 pattern and length-1-or-2 replacement
 - alphabet of all strings is a subset of {A,B,C,D}
 - answers are integers in [0, 25]
 - recomputes BFS distance for each item and confirms it matches gold

Exits with status 0 on success, nonzero on failure.
"""
import argparse
import json
import sys

from generator import bfs_distance, ALPHABET

ALPHA_SET = set(ALPHABET)


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def check_string(s, label, item_id):
    if not isinstance(s, str) or not s:
        raise ValueError(f"{item_id}: {label} not a non-empty string")
    if any(c not in ALPHA_SET for c in s):
        raise ValueError(f"{item_id}: {label}={s!r} has chars outside alphabet")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--items", required=True)
    p.add_argument("--gold", required=True)
    args = p.parse_args()

    items = load_jsonl(args.items)
    gold = load_jsonl(args.gold)

    item_ids = {it["id"] for it in items}
    gold_ids = {g["id"] for g in gold}
    if item_ids != gold_ids:
        print(f"FAIL: id sets differ. items-gold={item_ids - gold_ids}, gold-items={gold_ids - item_ids}")
        sys.exit(1)

    gold_by_id = {g["id"]: g["answer"] for g in gold}

    errors = []
    for it in items:
        iid = it["id"]
        try:
            check_string(it["initial"], "initial", iid)
            check_string(it["target"], "target", iid)
            if not isinstance(it["rules"], list) or not it["rules"]:
                raise ValueError(f"{iid}: rules missing or empty")
            for ri, rule in enumerate(it["rules"]):
                if len(rule) != 2:
                    raise ValueError(f"{iid}: rule {ri} is not a 2-element list")
                pat, rep = rule
                check_string(pat, f"rule[{ri}].pat", iid)
                check_string(rep, f"rule[{ri}].rep", iid)
                if len(pat) != 2:
                    raise ValueError(f"{iid}: rule {ri} pattern length != 2")
                if len(rep) not in (1, 2):
                    raise ValueError(f"{iid}: rule {ri} replacement length not in {{1,2}}")
            ans = gold_by_id[iid]
            if not isinstance(ans, int) or ans < 0 or ans > 25:
                raise ValueError(f"{iid}: gold answer out of range: {ans}")
            recomputed = bfs_distance(it["initial"], it["target"], it["rules"])
            if recomputed != ans:
                raise ValueError(f"{iid}: BFS recomputed {recomputed} but gold is {ans}")
        except Exception as e:
            errors.append(str(e))

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(f"OK: {len(items)} items verified, all BFS distances match gold.")


if __name__ == "__main__":
    main()
