#!/usr/bin/env python3
"""Verify structural validity of items + gold."""
import argparse, json, sys
from pathlib import Path

def load_jsonl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--gold", required=True)
    args = ap.parse_args()

    items = load_jsonl(args.items)
    gold = load_jsonl(args.gold)
    errors = []

    if len(items) != len(gold):
        errors.append(f"item count {len(items)} != gold count {len(gold)}")
    item_ids = {it["id"] for it in items}
    gold_ids = {g["id"] for g in gold}
    if item_ids != gold_ids:
        errors.append("ids mismatch between items and gold")

    for it in items:
        for k in ("id","lexicon","examples","test_gloss","instructions"):
            if k not in it:
                errors.append(f"item {it.get('id')} missing field {k}")
        if "lexicon" in it:
            for k in ("nouns","verbs","adjectives"):
                if k not in it["lexicon"]:
                    errors.append(f"item {it['id']} lexicon missing {k}")
        if "examples" in it:
            if len(it["examples"]) < 5:
                errors.append(f"item {it['id']} has <5 examples")
            for ex in it["examples"]:
                if "conlang" not in ex or "gloss" not in ex:
                    errors.append(f"item {it['id']} example malformed")

    for g in gold:
        if set(g.keys()) != {"id","answer"}:
            errors.append(f"gold {g.get('id')} has wrong fields {set(g.keys())}")
        if not isinstance(g.get("answer"), str) or not g["answer"]:
            errors.append(f"gold {g.get('id')} empty answer")

    if errors:
        print("VERIFICATION FAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(f"OK: {len(items)} items, {len(gold)} gold answers.")

if __name__ == "__main__":
    main()
