# MFN-Cascade: Validation Report

## 1. External Solvability & Identifiability Argument

A crucial requirement for any benchmark is that it must be **solvable in principle by a qualified external solver** (human specialist or another advanced model) using **only** the public solver bundle and the stated rules.

### Why MFN-Cascade is Fully Solvable from the Solver Bundle:
1. **Complete Specification:** The public solver bundle contains:
   - `treaties/common_framework.txt`: Specifies the exact math formulas for MFN triggers, margins, multipliers, hierarchy rules, round-by-round simulation steps, and stalemate protocols.
   - Bilateral treaties (e.g. `treaty_alpha_beta.txt`): Codes all initial base tariffs and the precise text of MFN clauses for those nations.
   - Amendments (e.g. `amendment_2022_04_15.txt`): Outlines date-based tariff modifications and MFN parameter adjustments.
2. **Deterministic Mechanics:** There are no hidden variables, random variables, or private seeds involved in resolving a query. Given a starting date and a trade concession event, the initial tariff schedule is fully determined, and the multi-round propagation is a deterministic mathematical process.
3. **Traceability/Auditability:** A human expert or advanced LLM can trace the propagation step-by-step:
   - Identify active treaties and amendments up to the query date.
   - Setup the initial 5x5x15 tariff matrix.
   - Apply the starting concession event.
   - Run discrete update rounds. In each round:
     - Check each of the active MFN clauses for trigger conditions.
     - Reduce rates accordingly.
     - Propagate parent category changes to child categories.
   - Verify if rates stabilize (changes < 0.01%) or hit round 20 to declare a stalemate.
   - Round the final rate to 1 decimal place.

### Evidence an External Solver Uses:
- The exact articles in the bilateral treaties for base tariff lookup.
- The amendment dates to determine whether to apply overrides.
- The hierarchy definition in the common framework to propagate parent rates to child rates.
- The discrete-round formula specified in the common framework to run the simulation.

---

## 2. Baseline Performance Analysis

To prove the benchmark is challenging and resistant to naive scripting or lazy shortcuts, we implemented and ran a **Static Base Rate Lookup Baseline** (`baseline_base_lookup.py`):

| Metric | Value |
|---|---:|
| Total Evaluation Items | 30 |
| Baseline Correct Predictions | 4 |
| **Baseline Accuracy** | **13.3%** |
| **Gold Self-Score Accuracy** | **100.0%** |

### Breakdown of Baseline Failures:
- **Trivial Items (4/30):** The baseline only succeeds on a small minority of items where the cascade does not reach the target category/nations at all, leaving the tariff rate at its original base level.
- **Dynamic Cascade Failure (26/30):** 86.7% of the items require tracking multiple rounds of updates, resolving amendments that active base rate lookups missed, or propagating parent-child overrides. This confirms that solvers *must* perform deep procedural reasoning to score highly.

---

## 3. Leakage & Isolation Audit

We performed a strict audit of the `solver_bundle` directory:
- **No Answers:** The `solver_bundle/items_private_sample.jsonl` contains only `id`, `date`, and `prompt` fields. It contains no `answer` fields.
- **No Code Leakage:** The solver bundle contains zero Python scripts, generator details, or verifier/scorer code. The generator and verifier are located in the candidate root directory, which is completely isolated from the solver bundle.
- **Self-Contained Public Assets:** All public files (`common_framework.txt`, treaties, amendments, README) are stored in the isolated `solver_bundle/` path and referenced using relative paths.
- **Verification Success:** Running the verifier confirmed that no answer text or gold labels are present anywhere in the prompts or public assets.

---

## 4. Item Diversity & Distribution

The generated 30 items exhibit rich diversity across multiple dimensions:
- **Nations involved:** Covers all bilateral import/export pairs among `Alpha`, `Beta`, `Gamma`, `Delta`, and `Epsilon`.
- **Goods Categories:** Spans across all 5 parent categories and 10 child categories in the hierarchy.
- **Cascade Complexity:** Includes both convergent cascades (settling to a unique decimal rate like `4.2%`) and stalemate cycles (producing `STALEMATE_X.Y%` outcomes), testing both sides of the simulation logic.
- **Temporal Variance:** Spread across multiple distinct years (2021, 2023, 2026), testing accurate active-amendment selection based on query dates.
