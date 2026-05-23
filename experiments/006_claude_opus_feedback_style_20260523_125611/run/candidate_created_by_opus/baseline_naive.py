#!/usr/bin/env python3
"""Naive baseline: emit stems in gloss order (no morphology applied).
Demonstrates a weak shortcut should score ~0/30."""
import json, sys, re
from pathlib import Path

ENG_NOUNS = ["man","woman","dog","cat","child","fish","bird","tree","house","water","stone","book"]
ENG_VERBS = ["see","eat","give","find","hit","love","want","hear","carry"]
ENG_ADJS  = ["big","small","old","good","red"]

def parse_gloss(test_gloss):
    # Very crude: just extract content words in order they appear.
    tokens = re.findall(r"[A-Za-z]+", test_gloss)
    # remove tags
    tags = {"SUBJ","VERB","OBJ","SG","PL","ACC","PRES","PAST","NEG"}
    return [t for t in tokens if t not in tags]

def solve(item):
    lex = item["lexicon"]
    all_lex = {**lex["nouns"], **lex["verbs"], **lex["adjectives"]}
    words = parse_gloss(item["test_gloss"])
    out = []
    for w in words:
        if w in all_lex:
            out.append(all_lex[w])
    return " ".join(out)

def main():
    items = [json.loads(l) for l in open("solver_bundle/items_private_sample.jsonl")]
    preds = []
    for it in items:
        preds.append({"id": it["id"], "answer": solve(it)})
    with open("predictions_baseline.jsonl","w") as f:
        for p in preds:
            f.write(json.dumps(p)+"\n")

if __name__ == "__main__":
    main()
