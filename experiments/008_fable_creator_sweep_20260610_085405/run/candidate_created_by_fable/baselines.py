#!/usr/bin/env python3
"""Shortcut baselines for Rosetta Fieldwork v1 (private-side audit tool).

Two obvious non-linguistic shortcuts a lazy solver might try:

- copy_nearest: return the corpus conlang sentence whose English translation
  shares the most content words with the query. Tests whether answers leak
  via near-duplicate sentences.
- gloss_lookup: build a word-level co-occurrence table between English
  content words and conlang tokens, then emit the best-matching conlang token
  for each English content word in English word order. Tests whether naive
  statistical alignment without morphology or word-order analysis suffices.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict

STOP = {"the", "do", "does", "did", "not"}


def load_jsonl(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def content_words(english: str):
    return [w for w in english.split() if w not in STOP]


def copy_nearest(item) -> str:
    q = set(content_words(item["query_english"]))
    best, best_score = "", -1
    for pair in item["corpus"]:
        score = len(q & set(content_words(pair["english"])))
        if score > best_score:
            best, best_score = pair["conlang"], score
    return best


def gloss_lookup(item) -> str:
    cooc = defaultdict(Counter)
    for pair in item["corpus"]:
        etoks = content_words(pair["english"])
        ctoks = pair["conlang"].split()
        for e in etoks:
            for c in ctoks:
                cooc[e][c] += 1
    out = []
    for e in content_words(item["query_english"]):
        if cooc[e]:
            out.append(cooc[e].most_common(1)[0][0])
    return " ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="solver_bundle/items_private_sample.jsonl")
    ap.add_argument("--mode", choices=("copy_nearest", "gloss_lookup"),
                    required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    items = load_jsonl(args.items)
    fn = copy_nearest if args.mode == "copy_nearest" else gloss_lookup
    with open(args.out, "w") as fh:
        for it in items:
            fh.write(json.dumps({"id": it["id"], "answer": fn(it)}) + "\n")
    print(f"wrote {len(items)} predictions to {args.out}")


if __name__ == "__main__":
    main()
