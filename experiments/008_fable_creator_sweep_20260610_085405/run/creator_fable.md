I'll build this benchmark step by step. Let me start by checking the target directory and planning.Now the verifier and scorer.Now the baseline solvers, then I'll run the generation pipeline.Both shortcut baselines score 0/30. Now the determinism check.Now let me inspect items by hand to audit quality — one per tier.Demo item is clean and even shows the vowel-deletion rule. Now the solver packet and manifest.Now the leakage inspection of the bundle.Bundle is clean. Let me hand-audit one medium and one hard item from the final data for the validation report.Both items check out by hand — every gold wordform is forced by attested analogies. Now the documentation files.Final end-to-end re-run of the strict CLI contract, plus a quick check on the demo-language overlap claim.The package is complete. Summary of what was built:

## Rosetta Fieldwork v1 — procedural field-linguistics decipherment

**Task.** Each of 30 items is an independent, procedurally generated constructed mini-language. The solver gets a 16–32 pair parallel corpus (conlang ↔ English) and must translate one novel English sentence *into* the conlang. Exact-match scoring, 1 point/item.

**Why this design beats the failure modes in the feedback:**
- **Not a forensics re-skin** — measures morphophonological induction and compositional generalization, an axis absent from the existing local benchmark set.
- **Tool-resistant but not tool-proof** — no retrievable artifact (fresh languages), no obvious script: the shipped statistical-alignment baseline reaches token-F1 0.44 yet scores **0/30**, because harmony, vowel deletion, nasal assimilation, agreement, irregulars, and word order must all be exactly right.
- **Floor above zero, ceiling below 30** — 6 easy items (lexicon + word order only), 10 medium, 14 hard (3 interacting boundary rules, decoy irregulars, fully novel inflected forms). Audited: outside the easy tier, no inflected query wordform is ever attested verbatim.
- **Externally solvable by construction, not by hope** — the generator enforces and `verifier.py` independently re-checks a per-item identifiability contract (every gold wordform attested verbatim or forced by a signature-matched analogy; affixes attested ≥3× across ≥2 stems; stem-segment visibility; irregulars shown verbatim). The solver packet discloses the closed phenomenon inventory and a worked demo, so a Linguistics-Olympiad-capable human can derive every answer.

**Validation performed:**
- Generation deterministic (byte-identical rerun) under the strict CLI contract
- `verifier.py`: 30/30 items PASS (regeneration, identifiability, leakage)
- Gold self-score: 30/30; two shortcut baselines: 0/30 each
- Hand-solved audits of one medium and one hard item (documented in `validation_report.md`)
- Programmatic bundle leakage scan: only `{id, corpus, query_english}` exposed; no gold strings, tiers, seeds, or grammar parameters anywhere in `solver_bundle/`

Closest existing benchmarks (LINGOLY/IOLBENCH/modeLing) and the non-duplication argument — procedural freshness, deterministic generation-direction grading, machine-checked identifiability — are stated in `README.md` and `benchmark_spec.json`.