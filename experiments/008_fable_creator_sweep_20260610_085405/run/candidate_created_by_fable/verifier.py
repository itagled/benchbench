#!/usr/bin/env python3
"""Verifier for Rosetta Fieldwork v1.

Checks the full package for internal consistency, identifiability, and
solver-bundle leakage:

1. Item / gold id alignment and uniqueness.
2. Every public corpus pair regenerates byte-identically from the private
   grammar + frame metadata (the corpus really is produced by one consistent
   grammar).
3. Every gold answer regenerates from the private grammar applied to the
   query frame (the gold is the deterministic output of the grammar).
4. Identifiability: the attestation conditions in generator.check_item hold
   (exact or analog attestation of every query wordform, lexeme exposure,
   morpheme generality, clause-order and negation evidence, base-segment
   visibility, no duplicate or leaked sentences).
5. Leakage: public item rows contain only {id, corpus, query_english}; the
   gold sentence never appears among corpus conlang sentences; the query
   English never appears among corpus English sentences.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import generator as G


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
    ap.add_argument("--items", required=True)
    ap.add_argument("--gold", required=True)
    ap.add_argument("--meta", default="private_meta.json")
    args = ap.parse_args()

    items = load_jsonl(args.items)
    golds = load_jsonl(args.gold)
    meta = json.loads(Path(args.meta).read_text())
    metas = {m["id"]: m for m in meta["items"]}

    errors = []
    item_ids = [it["id"] for it in items]
    gold_ids = [g["id"] for g in golds]
    if len(set(item_ids)) != len(item_ids):
        errors.append("duplicate item ids")
    if item_ids != gold_ids:
        errors.append("item/gold id mismatch or ordering mismatch")
    if set(item_ids) != set(metas):
        errors.append("meta ids do not match item ids")

    gold_by_id = {g["id"]: g for g in golds}
    n_checked = 0
    for it in items:
        iid = it["id"]
        m = metas.get(iid)
        if m is None:
            continue
        lang, frames, query = m["lang"], m["corpus_frames"], m["query_frame"]
        gold_row = gold_by_id[iid]

        if set(gold_row) != {"id", "answer"}:
            errors.append(f"{iid}: gold row has extra fields {set(gold_row)}")
        if set(it) != {"id", "corpus", "query_english"}:
            errors.append(f"{iid}: item row has unexpected fields {set(it)}")
        for pair in it["corpus"]:
            if set(pair) != {"conlang", "english"}:
                errors.append(f"{iid}: corpus pair has unexpected fields")
                break

        # regeneration checks
        if len(frames) != len(it["corpus"]):
            errors.append(f"{iid}: corpus length mismatch")
            continue
        for k, (f, pair) in enumerate(zip(frames, it["corpus"])):
            if G.conlang_sentence(lang, f) != pair["conlang"]:
                errors.append(f"{iid}: corpus[{k}] conlang does not regenerate")
            if G.english_sentence(f) != pair["english"]:
                errors.append(f"{iid}: corpus[{k}] english does not regenerate")
        if G.english_sentence(query) != it["query_english"]:
            errors.append(f"{iid}: query english does not regenerate")
        regen_gold = G.conlang_sentence(lang, query)
        if regen_gold != gold_row["answer"]:
            errors.append(f"{iid}: gold answer does not regenerate")
        if not re.fullmatch(r"[a-z]+( [a-z]+)*", gold_row["answer"]):
            errors.append(f"{iid}: gold answer charset violation")

        # identifiability + leak conditions
        problems = G.check_item(lang, frames, query, m["tier"])
        for code, key in problems:
            errors.append(f"{iid}: identifiability check failed: {code}:{key}")

        # direct leakage re-checks against the public file itself
        corpus_conlang = {p["conlang"] for p in it["corpus"]}
        corpus_english = {p["english"] for p in it["corpus"]}
        if gold_row["answer"] in corpus_conlang:
            errors.append(f"{iid}: gold sentence leaked into corpus")
        if it["query_english"] in corpus_english:
            errors.append(f"{iid}: query english leaked into corpus")
        n_checked += 1

    report = {
        "benchmark": G.BENCHMARK_ID,
        "items_checked": n_checked,
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    print(json.dumps(report, indent=2))
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
