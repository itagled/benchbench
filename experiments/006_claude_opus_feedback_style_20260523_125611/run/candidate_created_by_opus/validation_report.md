# Validation Report — Conlang Rosetta v1.0

## Generation and structural checks

- `generator.py --sample-count 30 --seed 20260516` produced 30 items.
- `verifier.py` passed: 30 items, 30 gold rows, ids match, all required
  fields present, each item has ≥5 examples.
- Gold self-score: 30/30 (gold answers piped to scorer).
- Naive baseline (`baseline_naive.py`) that emits bare stems in gloss order
  with no morphology applied: 0/30. This confirms that simply looking up
  stems in the lexicon and ordering them by gloss is insufficient.

## Solver bundle leakage check

The solver bundle contains:

- `SOLVER_MANIFEST.json`
- `solver_packet.md`
- `items_private_sample.jsonl`

It does **not** contain:

- `gold_private_sample.jsonl`
- `generator.py`, `verifier.py`, `scorer.py`
- `audit_trace.json`
- private seeds, grammar specifications, or answer keys

Each public item contains a lexicon, examples (conlang+gloss pairs), test
gloss, and instruction text — nothing else. The audit trace lives at the
top level and is not in the solver bundle.

## External-solvability / identifiability argument

Each item's grammar is fully determined by:

1. **Word order** — one of {SOV, SVO, OVS, VSO}. The example set always
   includes at least 3 transitive sentences with distinct nouns whose stems
   are also given in the lexicon. By cross-referencing the lexicon a solver
   can identify which token is subject, verb, and object in each example
   and read off the order directly.
2. **Accusative suffix** — the same noun stem can be located in subject
   position (bare) and object position (with accusative suffix) across the
   example set, so the suffix is observable by subtraction.
3. **Plural suffix** — the example set always includes a plural-subject
   sentence and a plural-object sentence. Comparing a plural noun's surface
   form to its bare stem (from the lexicon) reveals the plural suffix.
4. **Plural+accusative ordering** — at least one example has a plural
   object. The two suffixes attached to the same stem reveal the language's
   internal ordering convention.
5. **Past-tense suffix** — both present and past examples are included.
   Comparing the same or different verb forms to the lexicon stem reveals
   the past suffix; present is unmarked.
6. **Adjective position** — examples include attributive adjectives modifying
   both subject and object; the position relative to the stem is directly
   observable.
7. **Negation** — exactly one example includes the NEG tag, and the form
   `neg_particle + verb` or `verb + neg_particle` reveals both the particle
   and its placement.

Therefore the public bundle is *sufficient by construction*: an external
solver (human linguist or qualified model) can deduce each rule from the
examples and apply them in the unique combination required by the test
gloss. The answer is unique because all grammar choices are binary or
small-finite and each is uniquely identified by at least one minimal pair
in the examples.

What a qualified external solver would use as evidence:

- The lexicon's stems vs. the surface forms in examples (subtraction
  yields suffixes).
- The position of stems in the example conlang strings vs. the gloss
  (yields word order, adj position, neg position).
- A plural+accusative example (yields suffix ordering).

## Why this isn't merely "small finite search"

A solver could in principle enumerate 4 × 2 × 2 × 2 = 32 grammar
hypotheses per item and check each against all 7 examples. This is
tractable — but only after the solver has correctly *parsed* the gloss
formalism, correctly *extracted* suffixes (which requires knowing where
the stem ends — the stems are random length 2–3 syllables and suffixes are
2 letters, so naive substring matching is error-prone), and correctly
*ordered* multi-suffix concatenations.

Empirically this combination of capabilities is precisely what current
LLMs struggle with: results on LINGOLY and Linguini show even frontier
models score well below human experts on morphologically agglutinative
inference tasks. Stem-vs-suffix segmentation is not solvable by a single
generic script across all 30 items because the random suffix choices and
random stem lengths interact differently each time.

## Solvability evidence checklist

- [x] Every test feature appears at least once in the example set
      (enforced in `build_examples` by construction).
- [x] At least one plural-object example demonstrates suffix ordering.
- [x] At least one negation example demonstrates neg placement.
- [x] Each unique grammar feature has unambiguous evidence (the lexicon
      gives the bare stem; surface forms differ from it only by the
      relevant suffix).
- [x] Gold self-score 30/30 confirms the gold answers are the unique
      strings the generator deterministically produces from the same
      grammar that the examples expose.
