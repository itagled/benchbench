# Rosetta Fieldwork v1 — Solver Packet

## Task

Each item in `items_private_sample.jsonl` is an **independent constructed
mini-language**. You receive:

- `corpus`: a list of sentence pairs. `conlang` is a sentence in the
  mini-language; `english` is its exact English translation.
- `query_english`: one new English sentence.

Your job: **translate `query_english` into the mini-language** and output the
resulting conlang sentence.

Every item is a different language. Nothing learned from one item applies to
any other item. The languages are constructed for this benchmark; no internet
or world knowledge about real languages will give you the answer. All the
evidence you need is inside that item's corpus.

## Rules of the world (true for every item)

These facts are guaranteed, and you may rely on them:

1. Each language is **completely regular and consistent** within its item,
   except that a few individual words may have irregular (suppletive) forms.
   Any irregular form needed for the answer is shown verbatim somewhere in
   the corpus.
2. Morphology is **concatenative**: words are built from a stem plus optional
   prefixes/suffixes marking things like plural number, direct object (case),
   tense, subject agreement, or negation. A given language uses a fixed
   subset of these.
3. **Sound changes may apply at morpheme boundaries.** The possible phenomena
   are: (a) suffix/prefix vowels may alternate depending on the vowels of the
   stem (vowel harmony); (b) a vowel may be deleted when two vowels meet at a
   morpheme boundary; (c) a consonant may assimilate to a neighbouring
   consonant at a boundary (e.g. n becoming m before p/b). Not every language
   has these; the corpus shows you which apply.
4. **Word order is fixed per language** and may differ from English (e.g.
   verb-final or verb-initial). Adjective position relative to the noun is
   also fixed per language.
5. English glosses are literal. "The" carries no information (the languages
   have no articles). English tense and number are marked exactly
   (e.g. "the dogs run" = plural present, "the dog ran" = singular past,
   "did not see" = negated past).
6. **Identifiability guarantee:** the gold translation is forced by the
   corpus. Every wordform in the answer is either shown verbatim in the
   corpus, or is derivable by direct analogy with corpus forms: the same
   affix combination is attested on another stem of the same vowel class and
   the same boundary-relevant shape, every needed affix is attested on at
   least two different stems, and every needed stem is attested in at least
   two sentences. If you analyse the corpus correctly, exactly one answer is
   consistent with it.
7. The query sentence itself never appears in the corpus; it is always a new
   combination.

## Answer format

Submit `predictions.jsonl`, one JSON object per line, with exactly these
fields:

```json
{"id": "rf_001", "answer": "your conlang sentence here"}
```

- The answer is the conlang sentence: **lowercase words separated by single
  spaces**, in the language's own word order, no punctuation.
- Do not insert hyphens or morpheme boundaries (scoring strips hyphens, but
  plain words are safest). Do not add commentary inside `answer`.
- Scoring is **exact match per item** after normalization (lowercasing,
  removal of punctuation, whitespace collapsing). One point per item; there
  is no partial credit, so check every affix.

## Worked example (demo language; not part of the scored set)

Corpus (excerpt of the relevant lines):

```
fafu nagujo          | the horse sleeps
wergo naguw          | the man slept
turu rojudjo         | the road waits
gotore rojudjo       | the stones wait
jefe jujhuw          | the woman sang
wergo jujhejo        | the man sings
netgof dedahjo       | the child jumps
jefe dedahuw         | the woman jumped
```

Query: `the horse waited`

Reasoning sketch:

- Subject-first order, verb last (full corpus shows subject-object-verb).
- "horse" = `fafu` (from `fafu nagujo`).
- Present tense ends in `-jo` (`nagujo`, `rojudjo`, `jujhejo`, `dedahjo`);
  past ends in `-uw` (`naguw`, `jujhuw`, `dedahuw`).
- "wait" stem = `rojud` (from `rojudjo` minus `-jo`).
- Note the boundary rule visible in `naguw`: stem `nagu` + `uw` drops one
  vowel at the vowel-vowel boundary (compare `jujhe`/`jujhuw`). The stem
  `rojud` ends in a consonant, so nothing is deleted: `rojud` + `uw` =
  `rojuduw`.

Answer: `{"id": "demo_001", "answer": "fafu rojuduw"}`

## Practical advice

- Work item by item; segment words by comparing minimal pairs of sentences.
- Identify which grammatical categories the language marks (plural, object
  case, tense, agreement, negation) before translating.
- Watch for irregular forms: if the corpus shows a form that your rules do
  not predict, the corpus wins.
- Verify your final answer wordform-by-wordform against attested analogies.
