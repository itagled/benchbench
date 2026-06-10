#!/usr/bin/env python3
"""Generator for Rosetta Fieldwork v1.

Each item is an independent, procedurally generated constructed mini-language.
The solver receives a small parallel corpus (conlang sentence <-> English
translation) plus one novel English query sentence, and must produce the
conlang translation of the query. Grading is deterministic exact match after
light normalization.

The generator enforces machine-checked identifiability: every wordform needed
for the gold answer is either attested verbatim in the corpus, or is forced by
an attested analogy (same affix chain on a stem of the same harmony class and
the same boundary-relevant final/initial segment type), and every morpheme is
attested several times across distinct stems. This makes the gold answer
derivable in principle by an external solver from the public bundle alone.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

BENCHMARK_ID = "rosetta_fieldwork_v1"

# ----------------------------------------------------------------------------
# English-side lexicon (chosen so every surface form is number/tense
# unambiguous: no zero plurals, no past forms identical to the base form).
# ----------------------------------------------------------------------------

NOUN_PLURALS = {
    "dog": "dogs", "bird": "birds", "stone": "stones", "river": "rivers",
    "tree": "trees", "house": "houses", "star": "stars", "horse": "horses",
    "friend": "friends", "basket": "baskets", "moon": "moons", "road": "roads",
    "song": "songs", "cloud": "clouds", "island": "islands",
    "garden": "gardens", "child": "children", "woman": "women", "man": "men",
    "wolf": "wolves", "knife": "knives", "leaf": "leaves",
}

TRANS_VERBS = {
    "see": ("sees", "saw"), "eat": ("eats", "ate"), "hold": ("holds", "held"),
    "follow": ("follows", "followed"), "find": ("finds", "found"),
    "carry": ("carries", "carried"), "bite": ("bites", "bit"),
    "take": ("takes", "took"), "love": ("loves", "loved"),
    "watch": ("watches", "watched"), "chase": ("chases", "chased"),
    "push": ("pushes", "pushed"), "call": ("calls", "called"),
    "help": ("helps", "helped"),
}

INTRANS_VERBS = {
    "sleep": ("sleeps", "slept"), "fall": ("falls", "fell"),
    "run": ("runs", "ran"), "swim": ("swims", "swam"),
    "sing": ("sings", "sang"), "dance": ("dances", "danced"),
    "jump": ("jumps", "jumped"), "cry": ("cries", "cried"),
    "wait": ("waits", "waited"), "laugh": ("laughs", "laughed"),
}

ALL_VERBS = {**TRANS_VERBS, **INTRANS_VERBS}

ADJECTIVES = (
    "big", "small", "old", "new", "red", "black", "white", "good",
    "cold", "young",
)

# ----------------------------------------------------------------------------
# Conlang phonology
# ----------------------------------------------------------------------------

VOWELS_BACK = ("a", "o", "u")
VOWELS_FRONT = ("e", "i")
ALL_VOWELS = set(VOWELS_BACK) | set(VOWELS_FRONT)
CONSONANT_POOL = tuple("ptkbdgmnslrvhwjf")


def is_vowel(ch: str) -> bool:
    return ch in ALL_VOWELS


def harmony_class_of(base: str) -> str:
    for ch in base:
        if ch in VOWELS_BACK:
            return "back"
        if ch in VOWELS_FRONT:
            return "front"
    return "back"


def final_cat(base: str) -> str:
    ch = base[-1]
    if is_vowel(ch):
        return "V"
    if ch == "n":
        return "n"
    return "C"


def init_cat(base: str) -> str:
    return "pb" if base[0] in ("p", "b") else "x"


def realize_morph(form: str, cls: str) -> str:
    """Resolve harmony archiphonemes A (a/e) and U (u/i)."""
    if cls == "front":
        return form.replace("A", "e").replace("U", "i")
    return form.replace("A", "a").replace("U", "u")


def apply_nasal(word: str) -> str:
    return re.sub(r"n([pb])", r"m\1", word)


def synth_surface(lang: dict, base: str, suffixes: list, prefix) -> str:
    word = base
    for sfx in suffixes:
        if lang["rules"]["hiatus"] and is_vowel(word[-1]) and is_vowel(sfx[0]):
            word = word[:-1]
        word += sfx
    if prefix:
        word = prefix + word
    if lang["rules"]["nasal"]:
        word = apply_nasal(word)
    return word


# ----------------------------------------------------------------------------
# Stem and affix generation
# ----------------------------------------------------------------------------

class BuildError(Exception):
    pass


def gen_stem(rng, lang, used, cls=None, fin=None, ini=None) -> str:
    cons = lang["cons"]
    harmony = lang["rules"]["harmony"]
    for _ in range(800):
        stem_cls = cls or (rng.choice(("back", "front")) if harmony else None)
        if harmony:
            vset = VOWELS_BACK if stem_cls == "back" else VOWELS_FRONT
        else:
            vset = lang["vowel_inv"]

        def syll(coda_p):
            s = rng.choice(cons) + rng.choice(vset)
            if rng.random() < coda_p:
                s += rng.choice(cons)
            return s

        stem = syll(0.25) + syll(0.35)
        if fin == "V":
            while not is_vowel(stem[-1]):
                stem = stem[:-1]
            if len(stem) < 3:
                continue
        elif fin == "n":
            if is_vowel(stem[-1]):
                stem += "n"
            else:
                stem = stem[:-1] + "n"
        elif fin == "C":
            non_n = [c for c in cons if c != "n"]
            if is_vowel(stem[-1]):
                stem += rng.choice(non_n)
            elif stem[-1] == "n":
                stem = stem[:-1] + rng.choice(non_n)
        if ini == "pb":
            pb = [c for c in ("p", "b") if c in cons]
            if not pb:
                raise BuildError("no p/b consonant available for ini=pb")
            stem = rng.choice(pb) + stem[1:]
        elif ini == "x":
            if stem[0] in ("p", "b"):
                others = [c for c in cons if c not in ("p", "b")]
                stem = rng.choice(others) + stem[1:]
        if lang["rules"]["nasal"]:
            stem = apply_nasal(stem)
        # nasal normalization may have changed nothing relevant to fin/ini
        if fin == "V" and not is_vowel(stem[-1]):
            continue
        if fin == "n" and stem[-1] != "n":
            continue
        if fin == "C" and (is_vowel(stem[-1]) or stem[-1] == "n"):
            continue
        if not (3 <= len(stem) <= 7):
            continue
        if stem in used:
            continue
        used.add(stem)
        return stem
    raise BuildError("could not generate stem under constraints")


def gen_affix(rng, lang, used_forms, shapes=("CV", "VC", "CVC"),
              force_final_n=False) -> str:
    cons = lang["cons"]
    harmony = lang["rules"]["harmony"]
    for _ in range(400):
        shape = rng.choice(shapes)
        out = []
        for ch in shape:
            if ch == "C":
                out.append(rng.choice(cons))
            else:
                if harmony:
                    out.append(rng.choice(("A", "U")))
                else:
                    out.append(rng.choice(lang["vowel_inv"]))
        form = "".join(out)
        if force_final_n and not form[-1] in ("A", "U") and not is_vowel(form[-1]):
            form = form[:-1] + "n"
        if lang["rules"]["nasal"]:
            # avoid internal n+p/b in the underlying form for stability
            form = apply_nasal(form)
        realizations = {realize_morph(form, "back"), realize_morph(form, "front")}
        if any(len(r) < 1 for r in realizations):
            continue
        if any(r in used_forms for r in realizations):
            continue
        used_forms.update(realizations)
        return form
    raise BuildError("could not generate affix")


# ----------------------------------------------------------------------------
# Tier configuration
# ----------------------------------------------------------------------------

TIER_CONFIG = {
    "easy": dict(
        corpus=16, p_trans=0.75, p_adj=0.35, p_pl=0.45, p_neg=0.0,
        harmony=0.0, hiatus=0.0, nasal=0.0, agr=0.0, neg_morph=0.0,
        p_acc=0.6, p_pres_zero=0.35, need_rule=False,
        nouns=5, vtrans=3, vintr=2, adjs=3,
        exact_all=True, p_irreg=0.0, p_irreg_verb=0.0, decoy_irreg=False,
    ),
    "medium": dict(
        corpus=24, p_trans=0.85, p_adj=0.5, p_pl=0.55, p_neg=0.35,
        harmony=0.75, hiatus=0.5, nasal=0.0, agr=0.0, neg_morph=1.0,
        p_acc=0.9, p_pres_zero=0.25, need_rule=True,
        nouns=7, vtrans=4, vintr=3, adjs=4,
        exact_all=False, p_irreg=0.35, p_irreg_verb=0.0, decoy_irreg=False,
    ),
    "hard": dict(
        corpus=32, p_trans=1.0, p_adj=0.8, p_pl=0.65, p_neg=0.5,
        harmony=1.0, hiatus=1.0, nasal=1.0, agr=0.75, neg_morph=1.0,
        p_acc=1.0, p_pres_zero=0.25, need_rule=True,
        nouns=9, vtrans=5, vintr=3, adjs=5,
        exact_all=False, p_irreg=0.6, p_irreg_verb=0.3, decoy_irreg=True,
    ),
}

TIER_PROPORTIONS = (("easy", 6), ("medium", 10), ("hard", 14))


# ----------------------------------------------------------------------------
# Language construction
# ----------------------------------------------------------------------------

def make_language(rng, cfg) -> dict:
    rules = {
        "harmony": rng.random() < cfg["harmony"],
        "hiatus": rng.random() < cfg["hiatus"],
        "nasal": rng.random() < cfg["nasal"],
    }
    if cfg["need_rule"] and not (rules["harmony"] or rules["hiatus"]):
        rules["hiatus"] = True
    cons = set(rng.sample(CONSONANT_POOL, 9))
    cons.add("n")
    if rules["nasal"]:
        cons.add("p")
    cons = sorted(cons)
    vowel_inv = None if rules["harmony"] else sorted(rng.sample(sorted(ALL_VOWELS), 4))

    lang = {
        "rules": rules,
        "cons": cons,
        "vowel_inv": vowel_inv,
        "word_order": rng.choice(("SOV", "SVO", "VSO")),
        "adj_order": rng.choice(("before", "after")),
        "_used_stems": set(),
        "_used_affixes": set(),
    }

    morphs = {}
    morphs["pl"] = gen_affix(rng, lang, lang["_used_affixes"])
    morphs["acc"] = (gen_affix(rng, lang, lang["_used_affixes"])
                     if rng.random() < cfg["p_acc"] else None)
    morphs["pres"] = ("" if rng.random() < cfg["p_pres_zero"]
                      else gen_affix(rng, lang, lang["_used_affixes"]))
    morphs["past"] = gen_affix(rng, lang, lang["_used_affixes"])
    morphs["agr"] = (gen_affix(rng, lang, lang["_used_affixes"])
                     if rng.random() < cfg["agr"] else None)
    if rng.random() < cfg["neg_morph"]:
        pos = rng.choice(("pre", "suf"))
        force_n = rules["nasal"] and pos == "pre" and rng.random() < 0.6
        morphs["neg"] = {
            "form": gen_affix(rng, lang, lang["_used_affixes"],
                              shapes=("CV", "CVC", "VC"),
                              force_final_n=force_n),
            "pos": pos,
        }
    else:
        morphs["neg"] = None
    lang["morphs"] = morphs

    lex = {"noun": {}, "vtrans": {}, "vintr": {}, "adj": {}}
    for gloss in rng.sample(sorted(NOUN_PLURALS), cfg["nouns"]):
        lex["noun"][gloss] = gen_stem(rng, lang, lang["_used_stems"])
    for gloss in rng.sample(sorted(TRANS_VERBS), cfg["vtrans"]):
        lex["vtrans"][gloss] = gen_stem(rng, lang, lang["_used_stems"])
    for gloss in rng.sample(sorted(INTRANS_VERBS), cfg["vintr"]):
        lex["vintr"][gloss] = gen_stem(rng, lang, lang["_used_stems"])
    for gloss in rng.sample(sorted(ADJECTIVES), cfg["adjs"]):
        lex["adj"][gloss] = gen_stem(rng, lang, lang["_used_stems"])
    lang["lex"] = lex
    lang["irreg_pl"] = {}
    lang["irreg_past"] = {}
    return lang


# ----------------------------------------------------------------------------
# Word and sentence realization
# ----------------------------------------------------------------------------

def morph_form(lang, mid: str):
    if mid == "neg":
        return lang["morphs"]["neg"]["form"]
    return lang["morphs"][mid]


def verb_stem(lang, gloss: str) -> str:
    if gloss in lang["lex"]["vtrans"]:
        return lang["lex"]["vtrans"][gloss]
    return lang["lex"]["vintr"][gloss]


def make_word(lang, pos, gloss, *, plural=False, accus=False, tense=None,
              subj_pl=False, neg=False) -> dict:
    if pos == "noun":
        irreg = lang["irreg_pl"].get(gloss)
        if plural and irreg is not None:
            base, chain, used_irreg = irreg, [], True
        elif plural:
            base, chain, used_irreg = lang["lex"]["noun"][gloss], ["pl"], False
        else:
            base, chain, used_irreg = lang["lex"]["noun"][gloss], [], False
        if accus and lang["morphs"]["acc"]:
            chain = chain + ["acc"]
        prefix_mid = None
    elif pos == "verb":
        irreg = lang["irreg_past"].get(gloss)
        if tense == "past" and irreg is not None:
            base, chain, used_irreg = irreg, [], True
        else:
            base, chain, used_irreg = verb_stem(lang, gloss), [tense], False
        if lang["morphs"]["agr"] and subj_pl:
            chain = chain + ["agr"]
        prefix_mid = None
        if neg:
            if lang["morphs"]["neg"] is None:
                raise BuildError("negated frame in language without neg morph")
            if lang["morphs"]["neg"]["pos"] == "pre":
                prefix_mid = "neg"
            else:
                chain = chain + ["neg"]
    else:
        raise ValueError(pos)

    cls = harmony_class_of(base)
    sfx = []
    nonzero = []
    for mid in chain:
        form = morph_form(lang, mid)
        if form:
            nonzero.append(mid)
            sfx.append(realize_morph(form, cls))
    pre = realize_morph(morph_form(lang, "neg"), cls) if prefix_mid else None
    surface = synth_surface(lang, base, sfx, pre)
    base_truncated = bool(
        lang["rules"]["hiatus"] and sfx and is_vowel(base[-1]) and is_vowel(sfx[0])
    )
    sig = (
        pos,
        tuple(nonzero),
        prefix_mid is not None,
        harmony_class_of(base) if lang["rules"]["harmony"] else None,
        final_cat(base) if nonzero else None,
        init_cat(base) if prefix_mid else None,
        used_irreg,
    )
    return {
        "pos": pos, "gloss": gloss, "base": base, "chain": list(chain),
        "prefix": prefix_mid, "surface": surface, "sig": sig,
        "irreg": used_irreg, "base_truncated": base_truncated,
    }


def frame_words(lang, frame) -> list:
    words = [make_word(lang, "noun", frame["subj"]["noun"],
                       plural=frame["subj"]["plural"], accus=False)]
    if frame["type"] == "trans":
        words.append(make_word(lang, "noun", frame["obj"]["noun"],
                               plural=frame["obj"]["plural"], accus=True))
    words.append(make_word(lang, "verb", frame["verb"], tense=frame["tense"],
                           subj_pl=frame["subj"]["plural"], neg=frame["neg"]))
    return words


def np_tokens(lang, np, accus) -> list:
    noun_w = make_word(lang, "noun", np["noun"], plural=np["plural"],
                       accus=accus)["surface"]
    if np["adj"]:
        adj_w = lang["lex"]["adj"][np["adj"]]
        if lang["adj_order"] == "before":
            return [adj_w, noun_w]
        return [noun_w, adj_w]
    return [noun_w]


def conlang_sentence(lang, frame) -> str:
    s = np_tokens(lang, frame["subj"], accus=False)
    v = [make_word(lang, "verb", frame["verb"], tense=frame["tense"],
                   subj_pl=frame["subj"]["plural"], neg=frame["neg"])["surface"]]
    if frame["type"] == "trans":
        o = np_tokens(lang, frame["obj"], accus=True)
    else:
        o = []
    order = lang["word_order"]
    if order == "SOV":
        toks = s + o + v
    elif order == "SVO":
        toks = s + v + o
    else:  # VSO
        toks = v + s + o
    return " ".join(toks)


def english_np(np) -> list:
    words = ["the"]
    if np["adj"]:
        words.append(np["adj"])
    words.append(NOUN_PLURALS[np["noun"]] if np["plural"] else np["noun"])
    return words


def english_sentence(frame) -> str:
    subj = english_np(frame["subj"])
    gloss = frame["verb"]
    third, past = ALL_VERBS[gloss]
    pl = frame["subj"]["plural"]
    if frame["neg"]:
        aux = "did" if frame["tense"] == "past" else ("do" if pl else "does")
        vp = [aux, "not", gloss]
    else:
        if frame["tense"] == "past":
            vp = [past]
        else:
            vp = [gloss] if pl else [third]
    words = subj + vp
    if frame["type"] == "trans":
        words += english_np(frame["obj"])
    return " ".join(words)


# ----------------------------------------------------------------------------
# Frame sampling
# ----------------------------------------------------------------------------

def sample_np(rng, lang, p_adj, p_pl, exclude=()) -> dict:
    nouns = [g for g in sorted(lang["lex"]["noun"]) if g not in exclude]
    noun = rng.choice(nouns)
    adj = None
    if lang["lex"]["adj"] and rng.random() < p_adj:
        adj = rng.choice(sorted(lang["lex"]["adj"]))
    return {"noun": noun, "adj": adj, "plural": rng.random() < p_pl}


def sample_query(rng, lang, cfg) -> dict:
    trans = rng.random() < cfg["p_trans"]
    if trans:
        verb = rng.choice(sorted(lang["lex"]["vtrans"]))
    else:
        verb = rng.choice(sorted(lang["lex"]["vintr"]))
    subj = sample_np(rng, lang, cfg["p_adj"], cfg["p_pl"])
    obj = None
    if trans:
        obj = sample_np(rng, lang, cfg["p_adj"], cfg["p_pl"],
                        exclude=(subj["noun"],))
    neg = bool(lang["morphs"]["neg"]) and rng.random() < cfg["p_neg"]
    return {
        "type": "trans" if trans else "intrans",
        "subj": subj, "obj": obj, "verb": verb,
        "tense": rng.choice(("pres", "past")), "neg": neg,
    }


def random_frame(rng, lang, p_adj=0.3, p_pl=0.4, p_neg=0.15,
                 force_type=None) -> dict:
    if force_type == "trans" or (force_type is None and rng.random() < 0.6):
        ftype = "trans"
        verb = rng.choice(sorted(lang["lex"]["vtrans"]))
    else:
        ftype = "intrans"
        verb = rng.choice(sorted(lang["lex"]["vintr"]))
    subj = sample_np(rng, lang, p_adj, p_pl)
    obj = None
    if ftype == "trans":
        obj = sample_np(rng, lang, p_adj, p_pl, exclude=(subj["noun"],))
    neg = bool(lang["morphs"]["neg"]) and rng.random() < p_neg
    return {"type": ftype, "subj": subj, "obj": obj, "verb": verb,
            "tense": rng.choice(("pres", "past")), "neg": neg}


def frame_with_subject(rng, lang, np, tense=None, neg=False) -> dict:
    verb = rng.choice(sorted(lang["lex"]["vintr"]))
    return {"type": "intrans", "subj": dict(np), "obj": None, "verb": verb,
            "tense": tense or rng.choice(("pres", "past")), "neg": neg}


def frame_with_object(rng, lang, np, tense=None, neg=False) -> dict:
    subj = sample_np(rng, lang, 0.0, 0.3, exclude=(np["noun"],))
    verb = rng.choice(sorted(lang["lex"]["vtrans"]))
    return {"type": "trans", "subj": subj, "obj": dict(np), "verb": verb,
            "tense": tense or rng.choice(("pres", "past")), "neg": neg}


def frame_with_verb(rng, lang, verb, tense, subj_pl, neg) -> dict:
    trans = verb in lang["lex"]["vtrans"]
    subj = sample_np(rng, lang, 0.0, 1.0 if subj_pl else 0.0)
    obj = None
    if trans:
        obj = sample_np(rng, lang, 0.0, 0.4, exclude=(subj["noun"],))
    return {"type": "trans" if trans else "intrans", "subj": subj, "obj": obj,
            "verb": verb, "tense": tense, "neg": neg}


# ----------------------------------------------------------------------------
# Query word specs, irregulars, analog partners
# ----------------------------------------------------------------------------

def query_word_specs(lang, query) -> dict:
    """Map role key -> word dict for the query's nouns and verb."""
    specs = {"subj": make_word(lang, "noun", query["subj"]["noun"],
                               plural=query["subj"]["plural"], accus=False)}
    if query["type"] == "trans":
        specs["obj"] = make_word(lang, "noun", query["obj"]["noun"],
                                 plural=query["obj"]["plural"], accus=True)
    specs["verb"] = make_word(
        lang, "verb", query["verb"], tense=query["tense"],
        subj_pl=query["subj"]["plural"], neg=query["neg"])
    return specs


def apply_irregulars(rng, lang, query, cfg) -> None:
    plural_nps = [np for np in (query["subj"], query.get("obj"))
                  if np and np["plural"]]
    if plural_nps and rng.random() < cfg["p_irreg"]:
        np = rng.choice(plural_nps)
        gloss = np["noun"]
        cls = (harmony_class_of(lang["lex"]["noun"][gloss])
               if lang["rules"]["harmony"] else None)
        lang["irreg_pl"][gloss] = gen_stem(rng, lang, lang["_used_stems"],
                                           cls=cls)
    if (query["tense"] == "past" and rng.random() < cfg["p_irreg_verb"]):
        gloss = query["verb"]
        cls = (harmony_class_of(verb_stem(lang, gloss))
               if lang["rules"]["harmony"] else None)
        lang["irreg_past"][gloss] = gen_stem(rng, lang, lang["_used_stems"],
                                             cls=cls)
    if cfg["decoy_irreg"]:
        query_nouns = {query["subj"]["noun"]}
        if query.get("obj"):
            query_nouns.add(query["obj"]["noun"])
        candidates = [g for g in sorted(lang["lex"]["noun"])
                      if g not in query_nouns and g not in lang["irreg_pl"]]
        if candidates:
            gloss = rng.choice(candidates)
            cls = (harmony_class_of(lang["lex"]["noun"][gloss])
                   if lang["rules"]["harmony"] else None)
            lang["irreg_pl"][gloss] = gen_stem(rng, lang, lang["_used_stems"],
                                               cls=cls)
            lang["_decoy_irreg"] = gloss


def stem_matches(lang, stem, word) -> bool:
    """Does this stem satisfy the analog constraints for the query word?"""
    if lang["rules"]["harmony"]:
        if harmony_class_of(stem) != harmony_class_of(word["base"]):
            return False
    nonzero = word["sig"][1]
    if nonzero and final_cat(stem) != final_cat(word["base"]):
        return False
    if word["prefix"] and init_cat(stem) != init_cat(word["base"]):
        return False
    return True


def ensure_partners(rng, lang, query, cfg, specs) -> dict:
    """For each non-irregular query word that needs an analog, find or create
    a partner lexeme whose stem has the same signature-relevant properties."""
    partners = {}
    if cfg["exact_all"]:
        return partners
    for role, word in specs.items():
        if word["irreg"]:
            continue
        if word["pos"] == "noun":
            pool_key, master = "noun", NOUN_PLURALS
        else:
            trans = word["gloss"] in lang["lex"]["vtrans"]
            pool_key = "vtrans" if trans else "vintr"
            master = TRANS_VERBS if trans else INTRANS_VERBS
        candidates = []
        for g, stem in sorted(lang["lex"][pool_key].items()):
            if g == word["gloss"]:
                continue
            # partner must be regular for the relevant slot
            if word["pos"] == "noun" and g in lang["irreg_pl"]:
                continue
            if word["pos"] == "verb" and g in lang["irreg_past"]:
                continue
            if stem_matches(lang, stem, word):
                candidates.append(g)
        if candidates:
            partners[role] = rng.choice(candidates)
            continue
        unused = [g for g in sorted(master) if g not in lang["lex"][pool_key]]
        if not unused:
            raise BuildError("gloss pool exhausted for partners")
        gloss = rng.choice(unused)
        cls = (harmony_class_of(word["base"])
               if lang["rules"]["harmony"] else None)
        nonzero = word["sig"][1]
        fin = final_cat(word["base"]) if nonzero else None
        ini = init_cat(word["base"]) if word["prefix"] else None
        if ini == "x":
            ini = "x"
        lang["lex"][pool_key][gloss] = gen_stem(
            rng, lang, lang["_used_stems"], cls=cls, fin=fin, ini=ini)
        partners[role] = gloss
    return partners


# ----------------------------------------------------------------------------
# Identifiability checker (also used by verifier.py)
# ----------------------------------------------------------------------------

def check_item(lang, frames, query, tier) -> list:
    cfg = TIER_CONFIG[tier]
    problems = []

    specs = query_word_specs(lang, query)
    query_english = english_sentence(query)
    gold = conlang_sentence(lang, query)

    corpus_words = []
    frame_glosses = []
    englishes = []
    conlangs = []
    for f in frames:
        ws = frame_words(lang, f)
        corpus_words.extend(ws)
        glosses = {w["gloss"] for w in ws}
        for np in (f["subj"], f.get("obj")):
            if np and np["adj"]:
                glosses.add(np["adj"])
        frame_glosses.append(glosses)
        englishes.append(english_sentence(f))
        conlangs.append(conlang_sentence(lang, f))

    # structural leak checks
    if len(set(englishes)) != len(englishes):
        problems.append(("english_dup", None))
    if query_english in englishes:
        problems.append(("query_leak", None))
    if gold in conlangs:
        problems.append(("gold_leak", None))
    if not re.fullmatch(r"[a-z]+( [a-z]+)*", gold):
        problems.append(("answer_charset", gold))

    # word-level attestation
    for role, w in specs.items():
        need_exact = cfg["exact_all"] or w["irreg"]
        if need_exact:
            ok = any(cw["gloss"] == w["gloss"] and cw["surface"] == w["surface"]
                     for cw in corpus_words)
            if not ok:
                problems.append(("exact_attest", role))
        else:
            ok = any(cw["sig"] == w["sig"] for cw in corpus_words)
            if not ok:
                problems.append(("analog_attest", role))
        # base-final-segment visibility: if the query keeps the base intact
        # and hiatus deletion exists, some attestation of the same base must
        # also keep it intact (else the stem-final vowel is unrecoverable).
        if (lang["rules"]["hiatus"] and is_vowel(w["base"][-1])
                and not w["base_truncated"]):
            ok = any(cw["gloss"] == w["gloss"] and cw["base"] == w["base"]
                     and not cw["base_truncated"] for cw in corpus_words)
            if not ok:
                problems.append(("base_visible", role))

    # lexeme exposure: every query content gloss in >= 2 frames
    query_glosses = {w["gloss"] for w in specs.values()}
    for np in (query["subj"], query.get("obj")):
        if np and np["adj"]:
            query_glosses.add(np["adj"])
    for g in sorted(query_glosses):
        n = sum(1 for fg in frame_glosses if g in fg)
        if n < 2:
            problems.append(("lexeme_exposure", g))

    # adjective order evidence
    query_adjs = [np["adj"] for np in (query["subj"], query.get("obj"))
                  if np and np["adj"]]
    if query_adjs:
        n_any = sum(
            1 for f in frames
            if any(np and np["adj"] for np in (f["subj"], f.get("obj"))))
        if n_any < 2:
            problems.append(("adj_any", None))

    # morpheme generality: every overt morph used by the query appears in
    # >= 3 corpus words across >= 2 distinct bases
    query_morphs = set()
    for w in specs.values():
        query_morphs.update(w["sig"][1])
        if w["prefix"]:
            query_morphs.add("neg")
    for mid in sorted(query_morphs):
        hosts = set()
        count = 0
        for cw in corpus_words:
            if mid in cw["sig"][1] or (mid == "neg" and cw["prefix"]):
                count += 1
                hosts.add(cw["base"])
        if count < 3 or len(hosts) < 2:
            problems.append(("morph_general", mid))

    # clause-type order evidence
    n_type = sum(1 for f in frames if f["type"] == query["type"])
    if n_type < 3:
        problems.append(("clause_order", query["type"]))

    # negation evidence
    if query["neg"]:
        n_neg = sum(1 for f in frames if f["neg"])
        if n_neg < 2:
            problems.append(("neg_evidence", None))

    return problems


# ----------------------------------------------------------------------------
# Evidence construction
# ----------------------------------------------------------------------------

def realizes_query_word(lang, frame, specs) -> bool:
    qs = {(w["gloss"], w["surface"]) for w in specs.values()}
    return any((cw["gloss"], cw["surface"]) in qs
               for cw in frame_words(lang, frame))


def exact_frame_for(rng, lang, query, role) -> dict:
    """A frame attesting the exact query wordform for the given role."""
    if role == "subj":
        np = {"noun": query["subj"]["noun"], "adj": None,
              "plural": query["subj"]["plural"]}
        return frame_with_subject(rng, lang, np)
    if role == "obj":
        np = {"noun": query["obj"]["noun"], "adj": None,
              "plural": query["obj"]["plural"]}
        return frame_with_object(rng, lang, np)
    return frame_with_verb(rng, lang, query["verb"], query["tense"],
                           query["subj"]["plural"], query["neg"])


def evidence_factories(rng, lang, query, cfg, specs, partners) -> list:
    """List of (factory, allow_exact) pairs producing evidence frames."""
    factories = []
    query_glosses = {w["gloss"] for w in specs.values()}

    def noun_factories(role):
        w = specs[role]
        gloss = w["gloss"]
        # exposure A: bare singular subject (shows stem + harmony class)
        factories.append((lambda r=rng, g=gloss: frame_with_subject(
            r, lang, {"noun": g, "adj": None, "plural": False}), True))
        # exposure B: flipped configuration
        if role == "subj":
            factories.append((lambda r=rng, g=gloss, p=not w_pl(w): (
                frame_with_object(r, lang, {"noun": g, "adj": None,
                                            "plural": p})), True))
        else:
            factories.append((lambda r=rng, g=gloss, p=not w_pl(w): (
                frame_with_subject(r, lang, {"noun": g, "adj": None,
                                             "plural": p})), True))
        # pattern frame: exact (easy / irregular) or analog partner
        if cfg["exact_all"] or w["irreg"]:
            factories.append((lambda r=rng, ro=role: exact_frame_for(
                r, lang, query, ro), True))
        else:
            pg = partners[role]
            np = {"noun": pg, "adj": None, "plural": w_pl(w)}
            if role == "subj":
                factories.append((lambda r=rng, n=np: frame_with_subject(
                    r, lang, n), True))
            else:
                factories.append((lambda r=rng, n=np: frame_with_object(
                    r, lang, n), True))

    def w_pl(w):
        return ("pl" in w["chain"]) or w["irreg"]

    noun_factories("subj")
    if query["type"] == "trans":
        noun_factories("obj")

    # verb evidence
    vw = specs["verb"]
    other_tense = "past" if query["tense"] == "pres" else "pres"
    factories.append((lambda r=rng: frame_with_verb(
        r, lang, query["verb"], other_tense, False, False), True))
    factories.append((lambda r=rng: frame_with_verb(
        r, lang, query["verb"], other_tense, True, False), True))
    if cfg["exact_all"] or vw["irreg"]:
        factories.append((lambda r=rng: exact_frame_for(
            r, lang, query, "verb"), True))
    else:
        pg = partners["verb"]
        factories.append((lambda r=rng, g=pg: frame_with_verb(
            r, lang, g, query["tense"], query["subj"]["plural"],
            query["neg"]), True))

    # adjective evidence: each query adjective with two different nouns
    for np in (query["subj"], query.get("obj")):
        if np and np["adj"]:
            adj = np["adj"]
            for _ in range(2):
                def adj_fac(r=rng, a=adj):
                    host = sample_np(r, lang, 0.0, 0.3)
                    host["adj"] = a
                    if r.random() < 0.5:
                        return frame_with_subject(r, lang, host)
                    return frame_with_object(r, lang, host)
                factories.append((adj_fac, False))

    # morpheme generality frames (hosts exclude query glosses)
    query_morphs = set()
    for w in specs.values():
        query_morphs.update(w["sig"][1])
        if w["prefix"]:
            query_morphs.add("neg")

    def host_noun(r):
        pool = [g for g in sorted(lang["lex"]["noun"])
                if g not in query_glosses and g not in lang["irreg_pl"]]
        if not pool:
            pool = [g for g in sorted(lang["lex"]["noun"])
                    if g not in lang["irreg_pl"]]
        return r.choice(pool)

    def host_verb(r):
        pool = [g for g in sorted(list(lang["lex"]["vtrans"])
                                  + list(lang["lex"]["vintr"]))
                if g not in query_glosses and g not in lang["irreg_past"]]
        if not pool:
            pool = sorted(list(lang["lex"]["vtrans"])
                          + list(lang["lex"]["vintr"]))
        return r.choice(pool)

    for mid in sorted(query_morphs):
        for _ in range(2):
            if mid == "pl":
                def fac(r=rng):
                    return frame_with_subject(
                        r, lang, {"noun": host_noun(r), "adj": None,
                                  "plural": True})
            elif mid == "acc":
                def fac(r=rng):
                    return frame_with_object(
                        r, lang, {"noun": host_noun(r), "adj": None,
                                  "plural": False})
            elif mid in ("pres", "past"):
                def fac(r=rng, t=mid):
                    return frame_with_verb(r, lang, host_verb(r), t,
                                           False, False)
            elif mid == "agr":
                def fac(r=rng):
                    return frame_with_verb(
                        r, lang, host_verb(r),
                        r.choice(("pres", "past")), True, False)
            else:  # neg
                def fac(r=rng):
                    return frame_with_verb(
                        r, lang, host_verb(r),
                        r.choice(("pres", "past")), False, True)
            factories.append((fac, False))

    # decoy irregular exposure (hard tier)
    decoy = lang.get("_decoy_irreg")
    if decoy:
        factories.append((lambda r=rng, g=decoy: frame_with_subject(
            r, lang, {"noun": g, "adj": None, "plural": True}), False))
        factories.append((lambda r=rng, g=decoy: frame_with_subject(
            r, lang, {"noun": g, "adj": None, "plural": False}), False))

    return factories


def build_item(rng, tier):
    cfg = TIER_CONFIG[tier]
    lang = make_language(rng, cfg)
    query = sample_query(rng, lang, cfg)
    apply_irregulars(rng, lang, query, cfg)
    specs = query_word_specs(lang, query)
    partners = ensure_partners(rng, lang, query, cfg, specs)
    # specs may change if irregulars were applied after sampling; recompute
    specs = query_word_specs(lang, query)

    query_english = english_sentence(query)
    seen_english = {query_english}
    corpus = []

    def try_add(fac, allow_exact, tries=12):
        """Add one frame produced by `fac`, preferring frames that do not
        accidentally attest an exact query wordform. Factories whose purpose
        is exact attestation (allow_exact=True) fall back to an exact-
        realizing frame if no clean draw exists."""
        fallback = None
        for _ in range(tries):
            f = fac()
            e = english_sentence(f)
            if e in seen_english:
                continue
            if not cfg["exact_all"] and realizes_query_word(lang, f, specs):
                if allow_exact and fallback is None:
                    fallback = f
                continue
            seen_english.add(e)
            corpus.append(f)
            return True
        if fallback is not None:
            seen_english.add(english_sentence(fallback))
            corpus.append(fallback)
            return True
        return False

    for fac, allow_exact in evidence_factories(rng, lang, query, cfg, specs,
                                               partners):
        try_add(fac, allow_exact)

    # fillers up to target corpus size
    guard = 0
    while len(corpus) < cfg["corpus"] and guard < 400:
        guard += 1
        try_add(lambda: random_frame(
            rng, lang, force_type=query["type"] if guard % 3 == 0 else None),
            False, tries=4)

    # check-and-patch loop
    for _ in range(5):
        problems = check_item(lang, corpus, query, tier)
        if not problems:
            break
        fatal = [p for p in problems
                 if p[0] in ("english_dup", "query_leak", "gold_leak",
                             "answer_charset")]
        if fatal:
            raise BuildError(f"fatal item problems: {fatal}")
        for code, key in problems:
            if code in ("exact_attest", "analog_attest", "base_visible"):
                try_add(lambda r=rng, k=key: exact_frame_for(r, lang, query, k),
                        True)
            elif code == "lexeme_exposure":
                if key in lang["lex"]["adj"]:
                    def fac(r=rng, a=key):
                        host = sample_np(r, lang, 0.0, 0.3)
                        host["adj"] = a
                        return frame_with_subject(r, lang, host)
                    try_add(fac, False)
                elif key in lang["lex"]["noun"]:
                    try_add(lambda r=rng, g=key: frame_with_subject(
                        r, lang, {"noun": g, "adj": None,
                                  "plural": r.random() < 0.5}), True)
                else:
                    try_add(lambda r=rng, g=key: frame_with_verb(
                        r, lang, g, r.choice(("pres", "past")), False,
                        False), True)
            elif code == "adj_any":
                def fac(r=rng):
                    host = sample_np(r, lang, 1.0, 0.3)
                    return frame_with_subject(r, lang, host)
                try_add(fac, False)
            elif code == "morph_general":
                if key == "pl":
                    try_add(lambda r=rng: frame_with_subject(
                        r, lang, {"noun": rng.choice(sorted(
                            lang["lex"]["noun"])), "adj": None,
                            "plural": True}), True)
                elif key == "acc":
                    try_add(lambda r=rng: random_frame(
                        r, lang, force_type="trans"), True)
                elif key in ("pres", "past"):
                    try_add(lambda r=rng, t=key: frame_with_verb(
                        r, lang, rng.choice(sorted(
                            list(lang["lex"]["vtrans"])
                            + list(lang["lex"]["vintr"]))), t, False,
                        False), True)
                elif key == "agr":
                    try_add(lambda r=rng: frame_with_verb(
                        r, lang, rng.choice(sorted(
                            list(lang["lex"]["vtrans"])
                            + list(lang["lex"]["vintr"]))),
                        rng.choice(("pres", "past")), True, False), True)
                else:
                    try_add(lambda r=rng: frame_with_verb(
                        r, lang, rng.choice(sorted(
                            list(lang["lex"]["vtrans"])
                            + list(lang["lex"]["vintr"]))),
                        rng.choice(("pres", "past")), False, True), True)
            elif code == "clause_order":
                try_add(lambda r=rng, t=key: random_frame(
                    r, lang, force_type=t), False)
            elif code == "neg_evidence":
                try_add(lambda r=rng: frame_with_verb(
                    r, lang, rng.choice(sorted(
                        list(lang["lex"]["vtrans"])
                        + list(lang["lex"]["vintr"]))),
                    rng.choice(("pres", "past")), False, True), True)
    else:
        raise BuildError(
            f"could not satisfy checker: {check_item(lang, corpus, query, tier)}")

    rng.shuffle(corpus)
    return lang, query, corpus


def serialize_lang(lang) -> dict:
    return {k: v for k, v in lang.items() if not k.startswith("_")}


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def tier_plan(count: int) -> list:
    total = sum(n for _, n in TIER_PROPORTIONS)
    plan = []
    for tier, n in TIER_PROPORTIONS:
        plan.extend([tier] * max(1, round(count * n / total)))
    while len(plan) > count:
        plan.pop()
    while len(plan) < count:
        plan.append("hard")
    return plan


def generate_item(seed, index, tier):
    for attempt in range(40):
        rng = random.Random(f"{BENCHMARK_ID}:{seed}:{index}:{attempt}")
        try:
            lang, query, corpus = build_item(rng, tier)
        except BuildError:
            continue
        return lang, query, corpus
    raise RuntimeError(f"item {index} ({tier}) failed after 40 attempts")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-count", type=int, default=30)
    ap.add_argument("--seed", type=int, default=20260516)
    ap.add_argument("--out-dir", type=str, default=".")
    ap.add_argument("--demo", action="store_true",
                    help="print one solved demo item (medium tier) and exit")
    args = ap.parse_args()

    if args.demo:
        lang, query, corpus = generate_item("demo-packet", 0, "medium")
        item = {
            "corpus": [{"conlang": conlang_sentence(lang, f),
                        "english": english_sentence(f)} for f in corpus],
            "query_english": english_sentence(query),
        }
        print(json.dumps({"item": item,
                          "answer": conlang_sentence(lang, query),
                          "lang": serialize_lang(lang),
                          "query_frame": query}, indent=2))
        return

    out_dir = Path(args.out_dir)
    bundle_dir = out_dir / "solver_bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    master = random.Random(f"{BENCHMARK_ID}:{args.seed}:plan")
    plan = tier_plan(args.sample_count)
    master.shuffle(plan)

    items, golds, metas = [], [], []
    for i, tier in enumerate(plan):
        lang, query, corpus = generate_item(args.seed, i, tier)
        item_id = f"rf_{i + 1:03d}"
        items.append({
            "id": item_id,
            "corpus": [{"conlang": conlang_sentence(lang, f),
                        "english": english_sentence(f)} for f in corpus],
            "query_english": english_sentence(query),
        })
        golds.append({"id": item_id, "answer": conlang_sentence(lang, query)})
        metas.append({"id": item_id, "tier": tier,
                      "lang": serialize_lang(lang),
                      "query_frame": query, "corpus_frames": corpus})

    with open(bundle_dir / "items_private_sample.jsonl", "w") as fh:
        for row in items:
            fh.write(json.dumps(row) + "\n")
    with open(out_dir / "gold_private_sample.jsonl", "w") as fh:
        for row in golds:
            fh.write(json.dumps(row) + "\n")
    with open(out_dir / "private_meta.json", "w") as fh:
        json.dump({"benchmark": BENCHMARK_ID, "seed": args.seed,
                   "count": args.sample_count, "items": metas}, fh, indent=1)

    by_tier = {}
    for m in metas:
        by_tier[m["tier"]] = by_tier.get(m["tier"], 0) + 1
    sizes = [len(it["corpus"]) for it in items]
    print(json.dumps({
        "benchmark": BENCHMARK_ID,
        "items": len(items),
        "tiers": by_tier,
        "corpus_size_min": min(sizes),
        "corpus_size_max": max(sizes),
        "out_dir": str(out_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
