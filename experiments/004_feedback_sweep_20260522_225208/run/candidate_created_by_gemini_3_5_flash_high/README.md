# MFN-Cascade: Recursive Treaty Tariff Adjudication (RTTCA)

MFN-Cascade is a high-difficulty benchmark testing **multi-stage, legally-grounded recursive reasoning** in frontier AI agents. In this benchmark, the solver must parse semi-structured, legally-phrased trade agreements, resolve complex rule priorities and exceptions, and follow a cascading chain of recursive tariff updates to calculate the final, stable tariff rates between target nations.

---

## 🌟 Capability Claim & Key Novelty
Most existing benchmarks test models either on simple factual recall (e.g., MMLU), code generation (e.g., HumanEval), or simple single-step rule adherence (e.g., IFEval). Strong models excel at these because they can easily generate code or recall common patterns.

**MFN-Cascade** introduces a new challenge:
1. **Dense Legal Logic:** All rules (base rates, Most Favored Nation (MFN) updates, offsets, exceptions, and amendments) are expressed in legally-phrased bilateral treaty documents. The solver must correctly read and interpret these texts to extract the underlying rules.
2. **Recursive Cascades:** A single initial trade event (unilateral tariff reduction) triggers a cascading chain of updates across multiple nations due to interconnected MFN clauses.
3. **Hierarchical Category Propagation:** Tariff rates on parent categories (e.g., Electronics) automatically propagate to sub-categories (e.g., Consumer Electronics) under specific conditions.
4. **Stalemate Protocol:** Some cascades can form cyclic loops. The benchmark features a deterministic "Stalemate Locking Rule" codified in the common framework to resolve cycles after exactly 20 rounds of updates.
5. **Brittle-Script Resistance:** A model cannot easily solve this using basic regexes or standard parsing scripts because of the semi-structured legal text and date-based multilateral amendments that override prior articles.

---

## 📁 Package Directory Structure

```
candidate_created_by_gemini_3_5_flash_high/
├── README.md                  # This file
├── benchmark_spec.json        # Formal metadata about the benchmark
├── generator.py               # Procedural generator for treaties, queries, and gold answers
├── verifier.py                # Verifier validating integrity of the items/gold files
├── scorer.py                  # Scorer computing exact-match accuracy
├── gold_private_sample.jsonl  # Private gold answers (id and answer)
├── validation_report.md       # Analysis of solvability and baseline scores
├── failure_modes.md           # Documentation of failure modes observed
└── solver_bundle/
    ├── SOLVER_MANIFEST.json   # Listing of all files in the solver bundle
    ├── items_private_sample.jsonl # Item inputs for the solver
    ├── README.md              # Instructions for the solver
    └── treaties/              # Folder containing public treaty documents
        ├── common_framework.txt
        ├── treaty_alpha_beta.txt
        ├── treaty_beta_gamma.txt
        └── ...
```

---

## 🛠️ CLI Contracts

Every script must be executed from this directory.

### 1. Generation
To generate the 30 private sample items and create the public solver bundle:
```bash
/Users/rohit/.pyenv/versions/global_env/bin/python generator.py --sample-count 30 --seed 20260516 --out-dir .
```

### 2. Verification
To verify the integrity and schema of the generated files:
```bash
/Users/rohit/.pyenv/versions/global_env/bin/python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl
```

### 3. Scoring
To score a solver's predictions against the gold answers:
```bash
/Users/rohit/.pyenv/versions/global_env/bin/python scorer.py --gold gold_private_sample.jsonl --predictions predictions.jsonl --out score_report.json
```

---

## ⚖️ Rules of the MFN-Cascade System

1. **Hierarchy:** Parent categories (e.g. `Electronics`) automatically propagate their tariff rate to child categories (e.g. `ConsumerElectronics`) if the parent tariff is lower.
2. **MFN Trigger:** If Importer $D$ applies a lower rate on category $C$ to a third-party nation than it does to Exporter $S$, the MFN clause is triggered.
3. **MFN Formula:** The new tariff to $S$ is adjusted to $\min(\text{Current Tariff}, \max(\text{Floor}, \text{Formula}(\text{Third-Party Rate})))$.
4. **Discrete Rounds:** Updates propagate in distinct, discrete rounds. Each round applies MFN updates and then parent-to-child category overrides.
5. **Locking Rule:** If the system has not stabilized (changes $< 0.01\%$) after 20 rounds, it enters a `STALEMATE`. All rates lock to their round 20 values, rounded to 1 decimal place, and the final answer format is `STALEMATE_X.Y%`. Otherwise, the format is `X.Y%`.
