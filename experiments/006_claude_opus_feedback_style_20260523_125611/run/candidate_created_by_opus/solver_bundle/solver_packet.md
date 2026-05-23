# Conlang Rosetta — Solver Packet

You are solving 30 linguistics-style puzzles. Each item is a self-contained
fictional language. You are given:

- A lexicon mapping every English content word in this benchmark to its conlang
  *bare stem*. Suffixes and word order are NOT in the lexicon — you must infer
  them.
- Seven example sentences. Each has the conlang form and an interlinear gloss
  using these tags:
    .SG  singular noun
    .PL  plural noun
    .ACC direct-object (accusative) marker on the object NP
    .PRES present tense
    .PAST past tense
    NEG  sentence negation (applies to the verb)
  Adjectives appear as bare English words in the gloss; they modify the noun
  they precede in the gloss.
- A test gloss in the same format. Your job is to output the exact conlang
  sentence for the test gloss.

The conlang has consistent rules for:

1. Constituent word order (one of SOV / SVO / OVS / VSO).
2. Adjective position (before or after the noun it modifies).
3. Noun morphology: plural suffix and accusative suffix. The order in which
   these suffixes attach to the stem is fixed within a language. Singular
   subjects take no overt suffix.
4. Verb morphology: a past-tense suffix attaches directly to the verb stem.
   Present tense is unmarked.
5. Negation: a fixed negation particle appears in a fixed position relative to
   the verb (either immediately before or immediately after).

The examples collectively show every rule needed to translate the test
sentence. There is exactly one correct conlang string per item.

## Output

Write `predictions.jsonl` with one line per item:

    {"id": "item_000", "answer": "kanu vidra meka-ka"}

Use lowercase, single spaces between tokens, no leading/trailing whitespace,
no punctuation. Token strings should match the morphology you derive (suffixes
concatenated directly to the stem with no separator).
