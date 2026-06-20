# Rosetta Fieldwork v1

A procedurally generated **field-linguistics decipherment** benchmark. Each of
the 30 items is an independent constructed mini-language. The solver receives
a small parallel corpus (conlang sentence ↔ English translation) plus one
novel English sentence, and must produce the conlang translation of that
sentence. Grading is deterministic exact match after light normalization.

## Capability claim

The benchmark measures **few-shot induction of a novel morphophonological
system and compositional generalization from a small parallel corpus**:
segmenting words into morphemes, identifying affix functions (plural, object
case, tense, subject agreement, negation), recognizing boundary sound rules
(vowel harmony, vowel deletion, nasal assimilation), spotting irregular
forms, inferring word order, and then composing all of it correctly under an
exact-match contract. This axis is largely orthogonal to the
ledger/policy-reconciliation axis of the incumbent (Reimbursement Forensics)
and to code/math benchmarks.

## Why it is hard for strong tool-enabled models

- There is no public artifact to retrieve: every language is freshly
  generated, so search and memorized linguistics data give zero items.
- There is no obvious program to write: brute-force enumeration of grammars
  is open-ended, and statistical word alignment (we ship that baseline)
  scores 0/30 because morphology, boundary phonology, and word order must
  all be exactly right.
- The exact-match contract punishes near-misses: a single wrong suffix vowel
  (harmony), an undeleted vowel (hiatus), a missed irregular plural, or a
  misplaced adjective fails the item.
- A difficulty gradient (6 easy / 10 medium / 14 hard, identities hidden)
  is designed so every competent solver scores above zero while the hard
  tier resists even careful solvers: hard items use 2–3 interacting
  phonological rules, agreement, negation, irregular and decoy-irregular
  forms, and never attest any inflected query wordform verbatim.

## Why it is fair (external solvability)

The generator machine-enforces an identifiability contract, re-checked by
`verifier.py` on the shipped data:

- every wordform in the gold answer is attested verbatim, or forced by
  analogy (same affix chain attested on another stem of the same harmony
  class and the same boundary-relevant final/initial segment shape);
- every affix used by the answer is attested at least 3 times across at
  least 2 distinct stems; every needed stem appears in at least 2 sentences;
  word order and negation patterns are attested at least 3 and 2 times;
- irregular forms needed for the answer are always shown verbatim;
- if a stem-final vowel matters for the answer, some corpus form exposes it.

So a qualified human (e.g. a Linguistics Olympiad solver) or model can, in
principle, derive every answer from the public bundle alone. The solver
packet states all of this, including the closed inventory of possible
phenomena. See `validation_report.md` for the full argument and a hand-solved
audit of one medium and one hard item.

## Relation to existing benchmarks (and non-duplication)

Closest relatives: **LINGOLY / IOLBENCH / modeLing** (Linguistics-Olympiad
style problems) and low-resource MT probes. Differences: those use a fixed
pool of human-written, partially leaked Olympiad puzzles with heterogeneous
free-text grading; this package is **procedurally generated** (unbounded
fresh items, zero leakage), graded by **deterministic exact match** in the
generation direction (English → conlang, which a consistent grammar fully
determines), and ships a **machine-checked identifiability proof** per item —
none of which the Olympiad-derived sets provide. It is not a re-skin of the
incumbent Reimbursement Forensics axis (document reconciliation + policy
arithmetic): no policies, ledgers, or amounts are involved.

## Files

- `generator.py` — seeded generator (`--demo` prints a solved demo item).
- `verifier.py` — package verifier: regeneration, identifiability, leakage.
- `scorer.py` — deterministic exact-match scorer (+ token-F1 diagnostic).
- `baselines.py` — shortcut baselines (copy-nearest, gloss-lookup).
- `gold_private_sample.jsonl` — gold answers (`id`, `answer`). PRIVATE.
- `private_meta.json` — full grammar/frame metadata for audit. PRIVATE.
- `solver_bundle/` — everything the solver may see (items, packet, manifest).
- `validation_report.md`, `failure_modes.md` — audit documents.

## CLI contract

```bash
python generator.py --sample-count 30 --seed 20260516 --out-dir .
python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl
python scorer.py --gold gold_private_sample.jsonl --predictions predictions.jsonl --out score_report.json
```

Generation is fully deterministic in the seed (byte-identical reruns).
