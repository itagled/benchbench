# Failure Modes — Rosetta Fieldwork v1

Known risks, their likelihood, and mitigations already in place.

## 1. Calibration: benchmark turns out too easy

Frontier models have improving but uneven performance on
Linguistics-Olympiad-style decipherment. If a solver panel scores near the
ceiling, the cause will be the medium tier collapsing.

- Mitigation in place: 14/30 items are hard tier (3 interacting boundary
  rules, agreement, negation, irregulars, fully novel inflected forms,
  exact match over 4–6 words). Audit confirmed no inflected query wordform
  is attested verbatim outside the easy tier.
- Knob if needed: raise hard-tier share, add a third phonological rule
  class, or lengthen queries. One-line changes in `TIER_CONFIG`.

## 2. Calibration: benchmark turns out too hard / 0-band

The prior run showed all-zero rows are treated as design failures.

- Mitigation: 6 easy items require only lexicon lookup + word order; any
  competent solver should clear several. Both shipped baselines score 0 but
  the gloss-lookup baseline reaches token-F1 0.44, showing partial progress
  is smooth rather than cliff-like.

## 3. Scorer unfairly rejects reasonable answers

Exact match is brutal if the contract is unclear (the Service Credit
Forensics lesson).

- Mitigation: the answer space is a closed surface string fully determined
  by the corpus; the packet specifies lowercase/space format explicitly;
  normalization forgives case, punctuation, hyphens, and whitespace; the
  scorer treats missing ids as wrong rather than crashing. Residual risk:
  a solver embedding commentary inside `answer` will fail — the packet
  warns against this explicitly.

## 4. Hidden ambiguity (two grammars, two answers)

The classic decipherment failure: corpus consistent with multiple grammars
that disagree on the query.

- Mitigation: machine-checked identifiability contract (verbatim or
  signature-matched analog attestation per wordform, affix generality,
  stem-segment visibility, irregulars attested verbatim). Where underlying
  analyses can still differ (e.g. an unobservable stem-final vowel deleted
  in every relevant context), all consistent analyses yield the same
  surface answer, so grading is unaffected.
- Residual risk: an unforeseen interaction not covered by the signature
  (chain, harmony class, final/initial segment category). The phonological
  rules were chosen to be local and non-interacting precisely to keep the
  signature sufficient; the hand audits in `validation_report.md` spot-check
  this on real items.

## 5. Tool-based shortcut not anticipated

A solver could attempt automated grammar induction (e.g. program synthesis
over concatenative grammars with boundary rules).

- Assessment: this is legitimate solving, not a leak — the task *is* grammar
  induction. The search space (segmentations × affix inventories × rule
  settings × order) is large enough that naive enumeration on 16–32
  sentences is nontrivial to get exactly right, and our alignment baseline
  demonstrates the cheap end scores 0. If a clean solver script ever
  saturates the benchmark, that itself is a capability result, and rule
  density can be raised.

## 6. Leakage via the generator's English templates

English sentences are templated; a solver could try to fingerprint the
generator rather than the language.

- Assessment: knowing the template grammar (visible from any item) does not
  reveal stems, affixes, rules, or order — those are the answer-bearing
  parameters and are item-local. The solver packet already discloses the
  phenomenon inventory, so there is no hidden-vocabulary advantage.

## 7. Verifier blind spots

The verifier trusts `private_meta.json` produced by the generator.

- Mitigation: it re-realizes every sentence and the gold from the meta and
  compares to the shipped public bytes, so a corrupted or hand-edited meta
  fails loudly; identifiability is recomputed from shipped frames rather
  than trusted from build-time state.

## 8. English-side ambiguity

If an English query were number- or tense-ambiguous, the gold would be
contestable.

- Mitigation: the English lexicon excludes zero-plural nouns and verbs whose
  past equals the base form; negation uses unambiguous do-support; subjects
  are always third person with "the". Every English surface maps to exactly
  one semantic frame.
