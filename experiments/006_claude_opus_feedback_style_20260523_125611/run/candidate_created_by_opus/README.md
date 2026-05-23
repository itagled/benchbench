# Conlang Rosetta

A linguistics-Olympiad-style benchmark. Each of 30 items presents a freshly
generated fictional language via a small lexicon and ~7 interlinear-glossed
example sentences. The solver must infer the grammar and produce a single
exact-string translation of a held-out gloss.

## Files

- `generator.py` — produces items, gold, audit trace, solver bundle.
- `verifier.py` — structural validation.
- `scorer.py` — exact-match scorer.
- `gold_private_sample.jsonl` — private gold answers ({id, answer}).
- `solver_bundle/` — what the solver sees.
- `validation_report.md`, `failure_modes.md` — supporting docs.

## CLI

```
python generator.py --sample-count 30 --seed 20260516 --out-dir .
python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl
python scorer.py --gold gold_private_sample.jsonl --predictions predictions.jsonl --out score_report.json
```

## Closest existing benchmarks and why this isn't a duplicate

Closest: Linguistics-Olympiad style problems (UKLO/NACLO/IOL) and recent
LLM-targeted benchmarks like LINGOLY and Linguini. Those benchmarks use a
fixed, finite set of real or hand-authored language puzzles, which means
answers can leak into training corpora over time and the puzzles cannot be
regenerated freshly.

Conlang Rosetta is procedural: every seed produces 30 entirely fictional
languages with random stems and random combinations of grammar features
(word order, suffix ordering, adjective position, tense, negation
placement). There is no real-world referent for any of the languages so
training-data contamination is structurally impossible. The grammar space
is large enough (4 word orders × 2 adj positions × 2 suffix orders ×
2 neg positions × random stems and suffix choices) that no two seeds
produce the same language.

It is also distinct from the existing eval families in the landscape pack:
it is not coding, math, factuality, document QA, agent/tool, multimodal,
or knowledge-exam. It is structured-inference + morphology.
