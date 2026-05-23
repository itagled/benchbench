#!/usr/bin/env python3
"""Conlang Rosetta benchmark generator.

Each item presents a fictional language via ~7 interlinear-glossed example
sentences. The solver must infer the morphology and word order, then produce
a single exact-string conlang translation for a test sentence given as an
interlinear gloss.
"""
import argparse, json, os, random
from pathlib import Path

ENG_NOUNS = ["man","woman","dog","cat","child","fish","bird","tree","house","water","stone","book"]
ENG_VERBS = ["see","eat","give","find","hit","love","want","hear","carry"]
ENG_ADJS  = ["big","small","old","good","red"]

SYLLABLES = ["ka","ne","li","po","ra","tu","si","vo","dra","men","ki","lu","sha","to","ru",
             "bi","za","fa","mo","pe","xi","wa","je","no","gu","tha","sel","muk","har","tin",
             "yo","ber","kal","nim","pol","sur","weh","fey","dor","mez"]

CASE_MARKERS = ["ka","tu","mi","ro","li","sa","na"]
PLURAL_MARKERS = ["shu","vi","ne","ta","wo"]
PAST_MARKERS = ["ki","mo","nu","pe","be"]
NEG_PARTICLES = ["mai","zi","nok","kep","oru"]


def make_language(rng):
    used = set()
    def stem():
        while True:
            s = "".join(rng.choice(SYLLABLES) for _ in range(rng.randint(2,3)))
            if s in used or len(s) > 8:
                continue
            used.add(s)
            return s

    noun = {w: stem() for w in ENG_NOUNS}
    verb = {w: stem() for w in ENG_VERBS}
    adj  = {w: stem() for w in ENG_ADJS}

    # Pick non-overlapping suffix markers
    pool = list(CASE_MARKERS); rng.shuffle(pool)
    acc_suf = pool.pop()
    pool = list(PLURAL_MARKERS); rng.shuffle(pool)
    pl_suf = pool.pop()
    pool = list(PAST_MARKERS); rng.shuffle(pool)
    past_suf = pool.pop()
    neg = rng.choice(NEG_PARTICLES)

    # Ensure no suffix is a substring conflict with another (keep them distinct enough)
    while acc_suf == pl_suf or acc_suf == past_suf or pl_suf == past_suf:
        acc_suf = rng.choice(CASE_MARKERS)
        pl_suf = rng.choice(PLURAL_MARKERS)
        past_suf = rng.choice(PAST_MARKERS)

    grammar = {
        "word_order": rng.choice(["SOV","SVO","OVS","VSO"]),
        "adj_position": rng.choice(["pre","post"]),
        "neg_placement": rng.choice(["before_verb","after_verb"]),
        # Suffix ordering on nouns: e.g. stem-PL-ACC vs stem-ACC-PL
        "noun_suffix_order": rng.choice(["plural_then_case","case_then_plural"]),
        "acc_suf": acc_suf,
        "pl_suf": pl_suf,
        "past_suf": past_suf,
        "neg": neg,
        "noun": noun,
        "verb": verb,
        "adj": adj,
    }
    return grammar


def render_noun(grammar, eng, plural=False, accusative=False, adj_eng=None):
    s = grammar["noun"][eng]
    suffixes = []
    if grammar["noun_suffix_order"] == "plural_then_case":
        if plural: suffixes.append(grammar["pl_suf"])
        if accusative: suffixes.append(grammar["acc_suf"])
    else:
        if accusative: suffixes.append(grammar["acc_suf"])
        if plural: suffixes.append(grammar["pl_suf"])
    word = s + "".join(suffixes)
    if adj_eng is not None:
        a = grammar["adj"][adj_eng]
        if grammar["adj_position"] == "pre":
            return f"{a} {word}"
        else:
            return f"{word} {a}"
    return word


def render_verb(grammar, eng, past=False, negated=False):
    v = grammar["verb"][eng]
    if past:
        v = v + grammar["past_suf"]
    if negated:
        if grammar["neg_placement"] == "before_verb":
            return grammar["neg"] + " " + v
        else:
            return v + " " + grammar["neg"]
    return v


def render_sentence(grammar, subj):
    """subj is a dict: {subj_eng, subj_pl, subj_adj, verb_eng, verb_past, verb_neg, obj_eng, obj_pl, obj_adj}."""
    s_np = render_noun(grammar, subj["subj_eng"], subj.get("subj_pl",False), False, subj.get("subj_adj"))
    o_np = render_noun(grammar, subj["obj_eng"], subj.get("obj_pl",False), True, subj.get("obj_adj"))
    v = render_verb(grammar, subj["verb_eng"], subj.get("verb_past",False), subj.get("verb_neg",False))
    wo = grammar["word_order"]
    if wo == "SOV":
        return f"{s_np} {o_np} {v}"
    if wo == "SVO":
        return f"{s_np} {v} {o_np}"
    if wo == "OVS":
        return f"{o_np} {v} {s_np}"
    if wo == "VSO":
        return f"{v} {s_np} {o_np}"


def gloss(subj):
    """Produce interlinear gloss of an English-derived specification."""
    def np_gloss(eng, plural, adj):
        n = eng + (".PL" if plural else ".SG")
        if adj is not None:
            return adj + " " + n
        return n
    sg = np_gloss(subj["subj_eng"], subj.get("subj_pl",False), subj.get("subj_adj"))
    og = np_gloss(subj["obj_eng"], subj.get("obj_pl",False), subj.get("obj_adj")) + ".ACC"
    vg = subj["verb_eng"] + (".PAST" if subj.get("verb_past",False) else ".PRES")
    if subj.get("verb_neg",False):
        vg = "NEG " + vg
    return f"[SUBJ: {sg}]  [VERB: {vg}]  [OBJ: {og}]"


def pick_sentence_spec(rng, force=None):
    spec = {
        "subj_eng": rng.choice(ENG_NOUNS),
        "subj_pl": rng.random() < 0.3,
        "subj_adj": rng.choice(ENG_ADJS) if rng.random() < 0.25 else None,
        "verb_eng": rng.choice(ENG_VERBS),
        "verb_past": rng.random() < 0.5,
        "verb_neg": rng.random() < 0.25,
        "obj_eng": rng.choice(ENG_NOUNS),
        "obj_pl": rng.random() < 0.3,
        "obj_adj": rng.choice(ENG_ADJS) if rng.random() < 0.25 else None,
    }
    if spec["subj_eng"] == spec["obj_eng"]:
        # avoid identical subj/obj
        others = [n for n in ENG_NOUNS if n != spec["subj_eng"]]
        spec["obj_eng"] = rng.choice(others)
    if force:
        spec.update(force)
    return spec


def build_examples(grammar, rng):
    """Construct 7 example sentences that demonstrate each rule in the grammar.

    Coverage required:
      - word order: at least 3 distinct examples with different nouns to disambiguate.
      - case marking: a noun appears as both subject and object somewhere.
      - plural suffix: at least 2 examples with a plural noun.
      - past tense: at least 2 examples in past, 2 in present.
      - adjective: at least 2 examples with adjective, both subject- and object-modifying ideally.
      - negation: exactly 1 example with negation, in clear position.
      - suffix order: at least 1 example combining plural + accusative on the same noun.
    """
    examples = []

    # Example 1: simple SVO present, no plural, no adj, no neg.
    examples.append(pick_sentence_spec(rng, force={"subj_pl":False,"obj_pl":False,"subj_adj":None,"obj_adj":None,"verb_past":False,"verb_neg":False}))
    # Example 2: simple present, different nouns to disambiguate word order
    examples.append(pick_sentence_spec(rng, force={"subj_pl":False,"obj_pl":False,"subj_adj":None,"obj_adj":None,"verb_past":False,"verb_neg":False}))
    # Example 3: past tense
    examples.append(pick_sentence_spec(rng, force={"subj_pl":False,"obj_pl":False,"subj_adj":None,"obj_adj":None,"verb_past":True,"verb_neg":False}))
    # Example 4: plural subject, past
    examples.append(pick_sentence_spec(rng, force={"subj_pl":True,"obj_pl":False,"subj_adj":None,"obj_adj":None,"verb_past":True,"verb_neg":False}))
    # Example 5: plural object (demonstrates suffix ordering plural+acc)
    examples.append(pick_sentence_spec(rng, force={"subj_pl":False,"obj_pl":True,"subj_adj":None,"obj_adj":None,"verb_past":False,"verb_neg":False}))
    # Example 6: adjective on subject and adjective on object
    adj1 = rng.choice(ENG_ADJS); adj2 = rng.choice(ENG_ADJS)
    examples.append(pick_sentence_spec(rng, force={"subj_pl":False,"obj_pl":False,"subj_adj":adj1,"obj_adj":adj2,"verb_past":False,"verb_neg":False}))
    # Example 7: negation
    examples.append(pick_sentence_spec(rng, force={"subj_pl":False,"obj_pl":False,"subj_adj":None,"obj_adj":None,"verb_past":False,"verb_neg":True}))

    return examples


def build_test(grammar, rng, examples):
    """Build a test sentence that uses features all shown in examples.
    Make it combine multiple features so the solver must chain rules."""
    # Pick a test that combines: plural object + accusative + adjective + past tense + maybe negation.
    flags = {
        "verb_past": rng.choice([True, False]),
        "verb_neg": rng.random() < 0.3,
        "obj_pl": rng.random() < 0.5,
        "subj_pl": rng.random() < 0.5,
        "subj_adj": rng.choice(ENG_ADJS) if rng.random() < 0.5 else None,
        "obj_adj": rng.choice(ENG_ADJS) if rng.random() < 0.5 else None,
    }
    spec = pick_sentence_spec(rng, force=flags)
    # Ensure at least one non-trivial feature
    if not (flags["verb_past"] or flags["verb_neg"] or flags["obj_pl"] or flags["subj_pl"] or flags["subj_adj"] or flags["obj_adj"]):
        spec["verb_past"] = True
    return spec


def normalize(s):
    return " ".join(s.strip().split())


def make_item(item_idx, master_seed):
    rng = random.Random(master_seed * 100003 + item_idx)
    grammar = make_language(rng)
    examples = build_examples(grammar, rng)
    test_spec = build_test(grammar, rng, examples)

    # Render
    rendered_examples = []
    for ex in examples:
        rendered_examples.append({
            "conlang": render_sentence(grammar, ex),
            "gloss": gloss(ex),
        })
    answer = normalize(render_sentence(grammar, test_spec))
    test_gloss = gloss(test_spec)

    # Build public item content: lexicon + examples + test gloss
    lexicon = {
        "nouns": {k: grammar["noun"][k] for k in ENG_NOUNS},
        "verbs": {k: grammar["verb"][k] for k in ENG_VERBS},
        "adjectives": {k: grammar["adj"][k] for k in ENG_ADJS},
    }

    item_id = f"item_{item_idx:03d}"

    public_item = {
        "id": item_id,
        "lexicon": lexicon,
        "examples": rendered_examples,
        "test_gloss": test_gloss,
        "instructions": (
            "You are given a fictional language. The lexicon lists the bare stem "
            "for each English word. The examples are sentence pairs: each shows "
            "the conlang sentence and its interlinear gloss using these tags: "
            ".SG (singular), .PL (plural), .PRES (present tense), .PAST (past tense), "
            ".ACC (direct object / accusative case), and NEG (negation). "
            "The conlang has consistent rules for word order, suffix ordering on nouns, "
            "adjective placement, tense marking on verbs, and negation placement. "
            "Infer the rules from the examples, then produce the conlang sentence "
            "for the test gloss. Output ONLY the conlang sentence as a single line "
            "of lowercase space-separated tokens. No punctuation, no commentary."
        ),
    }

    private_gold = {"id": item_id, "answer": answer}

    audit = {
        "id": item_id,
        "grammar": {k: v for k, v in grammar.items() if k not in ("noun","verb","adj")},
        "test_spec": test_spec,
    }
    return public_item, private_gold, audit


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sample-count", type=int, default=30)
    p.add_argument("--seed", type=int, default=20260516)
    p.add_argument("--out-dir", default=".")
    args = p.parse_args()

    out = Path(args.out_dir)
    bundle = out / "solver_bundle"
    bundle.mkdir(parents=True, exist_ok=True)

    public_items = []
    gold = []
    audit = []
    for i in range(args.sample_count):
        pub, g, a = make_item(i, args.seed)
        public_items.append(pub)
        gold.append(g)
        audit.append(a)

    with open(bundle / "items_private_sample.jsonl", "w") as f:
        for it in public_items:
            f.write(json.dumps(it) + "\n")

    with open(out / "gold_private_sample.jsonl", "w") as f:
        for g in gold:
            f.write(json.dumps(g) + "\n")

    with open(out / "audit_trace.json", "w") as f:
        json.dump(audit, f, indent=2)

    # Solver bundle README
    manifest = {
        "benchmark": "Conlang Rosetta",
        "version": "1.0",
        "items_file": "items_private_sample.jsonl",
        "output_format": "predictions.jsonl with one JSON object per line: {\"id\": str, \"answer\": str}",
        "answer_format": "exact lowercase space-separated conlang sentence; no punctuation; tokens normalized to single spaces"
    }
    with open(bundle / "SOLVER_MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=2)

    solver_readme = """# Conlang Rosetta — Solver Packet

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
"""
    with open(bundle / "solver_packet.md", "w") as f:
        f.write(solver_readme)

    print(f"Generated {len(public_items)} items.")


if __name__ == "__main__":
    main()
