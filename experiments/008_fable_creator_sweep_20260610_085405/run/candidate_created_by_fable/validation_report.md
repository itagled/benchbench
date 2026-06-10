# Validation Report — Rosetta Fieldwork v1

Date: 2026-06-10. All commands run from this directory with
`/Users/rohit/.pyenv/versions/global_env/bin/python`.

## 1. Generation

```
python generator.py --sample-count 30 --seed 20260516 --out-dir .
```

Output: 30 items (6 easy / 10 medium / 14 hard, tier identities not exposed
to solvers), corpus sizes 16–32 pairs, written to
`solver_bundle/items_private_sample.jsonl`, `gold_private_sample.jsonl`, and
`private_meta.json`.

**Determinism:** regenerated into a scratch directory and diffed; all three
output files are byte-identical across runs (no unordered-set iteration, all
randomness flows from `random.Random` seeded with the CLI seed).

## 2. Verification

```
python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl
=> {"items_checked": 30, "errors": [], "status": "PASS"}
```

The verifier independently re-derives, for every item:

1. **Consistency** — every public corpus pair and every gold answer
   regenerates byte-identically from the stored grammar + semantic frames,
   so each corpus really is the output of one consistent grammar and each
   gold really is that grammar applied to the query.
2. **Identifiability** — the attestation conditions listed in section 5 hold
   on the shipped corpus (not just by construction).
3. **Leakage** — public rows contain only `{id, corpus, query_english}`;
   the gold sentence never appears among corpus conlang sentences; the query
   English never appears among corpus English sentences; gold answers match
   the declared charset.

## 3. Gold self-score

```
cp gold_private_sample.jsonl predictions.jsonl
python scorer.py --gold gold_private_sample.jsonl --predictions predictions.jsonl --out score_report.json
=> 30/30, accuracy 1.0
```

## 4. Shortcut baselines (both 0/30)

| baseline | what it tries | score | mean token-F1 |
|---|---|---:|---:|
| `copy_nearest` | return the corpus conlang sentence whose English shares the most content words with the query | 0/30 | 0.21 |
| `gloss_lookup` | per-word co-occurrence alignment; emit best conlang token per English content word in English order | 0/30 | 0.44 |

The gloss-lookup baseline's token-F1 of 0.44 shows that *partial* lexical
understanding is easy to obtain, while the exact-match score of 0 shows that
the items are not solvable without actually doing the morphology, boundary
phonology, and word-order analysis. This is the intended shape: progress is
smooth, full credit is not.

## 5. Solvability / identifiability argument

**Claim:** for every item, the public corpus determines the gold answer
uniquely; an external solver needs no generator internals.

The answer is a surface string, so it suffices that the corpus pins down the
surface realization of each answer word plus constituent order:

- **Word order / adjective order:** at least 3 corpus sentences share the
  query's clause type, and adjective-bearing sentences are attested whenever
  the query uses an adjective. Order is constant within a language, so the
  English role labels in the corpus fix the mapping.
- **Lexemes:** every content lexeme of the query appears in ≥2 corpus
  sentences with English glosses, fixing the stem (and its harmony class and
  final-segment shape, which are directly observable from its surface).
- **Inflected wordforms:** each is attested verbatim (easy tier, irregular
  forms), or forced by analogy: the *identical affix chain* is attested on
  another stem with the same harmony class and the same boundary-relevant
  final/initial segment category. Since all phonology is local to morpheme
  boundaries, two stems matching in those properties realize the chain
  identically — the attested analog mechanically determines the query form.
- **Affix identity:** every affix used by the answer appears ≥3 times across
  ≥2 distinct stems, so its function is not confusable with a stem fragment.
- **Hidden-segment safety:** if a stem-final vowel could be erased by hiatus
  deletion in all attestations while the answer needs it, that would be
  unidentifiable — the checker explicitly requires an attestation exposing
  the segment whenever the answer exposes it. (When the answer itself erases
  the segment, all consistent analyses produce the same surface string, so
  residual underlying ambiguity cannot change the graded answer.)
- **Irregulars:** suppletive forms required by the answer are attested
  verbatim, with English glosses fixing their number/tense.

These conditions are enforced by `generator.check_item` and independently
re-checked by `verifier.py` on the shipped artifacts. The solver packet
discloses the closed inventory of possible phenomena (concatenative affixes,
harmony, boundary vowel deletion, nasal assimilation, irregulars, fixed word
order) and the identifiability guarantee itself, so a solver knows the answer
is derivable and what evidence to look for.

**Evidence an external solver would use:** minimal pairs for segmentation
("the island jumps/jumped" → tense suffixes), cross-stem recurrence of
affixes, vowel-class covariation between stems and suffixes (harmony),
forms whose surface deviates from pure concatenation (boundary rules),
glossed plural/past forms that defy the regular rules (irregulars), and
constituent positions across the corpus (order).

### Hand-solved audit (current shipped data)

- `rf_004` (medium; SOV, adj after noun, harmony + hiatus): query "the
  leaves chased the red islands", gold `fibveme tavwuwmavav linef mabonub`.
  `fibve`+`me` (front-class plural, analog `nimmime` "roads");
  `tavwuw`+`ma`+`vav` (plural object, analog `mobummavav` "houses-OBJ");
  `linef` follows its noun phrase (analog "tile fibvemevev linef nawub");
  `mabon`+`ub` past (analog `bovonub` "pushed"; harmony: back `-ub` vs front
  `-ib` in `wewib`; hiatus visible in `vufub` = `vufu`+`ub`). Every gold
  token verified to be forced by corpus analogies.
- `rf_001` (hard; SVO, adj before, harmony + hiatus + nasal, zero present,
  agreement, neg prefix, decoy irregular `hada` "wolves"): query "the
  gardens did not take the new river", gold
  `sarolu lubhulpuddaran mopum nafofmud`. `saro`+`lu` (analog `lunholu`);
  `lub`+`hulpud`+`da`+`ran` exactly parallels attested
  `lubfusabdaran` ("did not watch", same neg+past+agr chain on a back-class
  consonant-final stem); `mopum` precedes its noun (attested); `nafof`+`mud`
  (analog `bafobmud`). Verified by hand.

## 6. Difficulty design and expected scores

- Easy tier (6): all query wordforms attested verbatim; needs lexicon
  mapping plus word order. Strong solvers should get most of these —
  guaranteeing the nonzero floor that the prior feedback requires.
- Medium tier (10): inflected query wordforms are *never* attested verbatim
  (audited: only bare stems coincide); harmony/hiatus must be applied by
  analogy; some irregular plurals.
- Hard tier (14): three interacting boundary rules, agreement, negation,
  zero present marking, irregulars plus decoy irregulars, 32-pair corpora
  with distractor lexemes, 4–6 word answers where every inflected form is
  novel. Exact match makes single-affix slips fatal.

Predicted band for strong tool-enabled solvers: roughly 8–18/30 (easy floor
plus partial medium/hard), with weak shortcut strategies at 0. This matches
the target shape: nobody at 0, nobody near 30. If a future panel saturates
the benchmark, the tier mix and rule density are single-knob adjustable.

## 7. Leakage inspection of the solver bundle

- Bundle contains exactly `SOLVER_MANIFEST.json`, `solver_packet.md`,
  `items_private_sample.jsonl`.
- Programmatic scan: no gold answer string occurs anywhere in any bundle
  file; item rows contain only `{id, corpus, query_english}`; no tier
  labels, seeds, grammar parameters, or references to private files.
- The worked example in the packet uses a dedicated demo language generated
  from an unrelated fixed seed. A programmatic scan found no shared stems
  with any scored item and only two chance 2-letter string coincidences
  among affixes ("re", "we"), which mark different functions in different
  languages and carry no transferable information (every item's language is
  generated independently and must be analysed from its own corpus).
- Internet access does not help: the languages exist only in this package.

## 8. Known limitations

See `failure_modes.md`. The main calibration risk is the unknown skill of
frontier models at olympiad-style decipherment; the tier structure bounds
both tails (easy floor > 0, hard ceiling < 30) rather than betting on a
point estimate.
