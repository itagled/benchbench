# MFN-Cascade: Solver Failure Modes

This document details the observed and anticipated failure modes of solver models attempting the **MFN-Cascade** benchmark. Because the benchmark requires high-fidelity legal text parsing and multi-round stateful graph propagation, standard shortcuts fail dramatically.

---

## 🚫 1. Shortcut Lookup (Static Base Rate Lookup)
* **Description:** The solver identifies the target importer, exporter, and good, and immediately looks up the base tariff in the corresponding bilateral treaty, ignoring any event updates, amendments, or MFN cascades.
* **Impact:** This was directly tested with our `baseline_base_lookup.py` script. It achieved an accuracy of only **13.3%** (4/30).
* **Why it fails:** 86.7% of the items have their rates altered by the unilateral concession event cascading through MFN clauses or overridden by active historical amendments.

---

## 📅 2. Temporal Misalignment (Date Ignorance)
* **Description:** The solver fails to restrict the active treaties and amendments to the exact historical date of the query. For example, if a query takes place on `2023-05-12`, the solver incorrectly applies an amendment effective on `2024-09-01`.
* **Why it fails:** Applying future amendments modifies base tariffs or MFN parameters prematurely, corrupting the starting tariff schedule and resulting in incorrect propagation fixed points.

---

## 🔄 3. Propagation Depth Suffocation (Single-Round Execution)
* **Description:** Solvers often assume that cascades only propagate one step (i.e., Importer A reduces rate to X, which triggers B's MFN, and B updates, and then it stops).
* **Why it fails:** Interconnected MFN clauses cause multi-hop chain reactions (e.g., $A \to B \to C \to A$). Stopping after one or two rounds leads to outdated intermediate rates. The simulator must be run iteratively until convergence or round 20 limit.

---

## 🌳 4. Hierarchical Category Decoupling
* **Description:** The solver tracks parent category (e.g. `Electronics`) changes but fails to propagate those rate decreases down to child categories (e.g. `ConsumerElectronics`), or vice-versa (mistakenly assuming child rate updates propagate upwards).
* **Why it fails:** Child categories must inherit lower parent rates automatically as codified in the Common Framework. Failing to enforce this hierarchical flow cuts off the cascade to child categories.

---

## 🔒 5. Stalemate Locking & Formatting Failure
* **Description:** In cyclic dependencies, the rates can decrease continuously or oscillate. If a solver does not implement the exact round-20 stalemate lock, it will either loop infinitely or predict an incorrect value. Even if they compute the value, they might forget to prefix the answer with `STALEMATE_`.
* **Why it fails:** The exact contract requires `STALEMATE_X.Y%` for non-convergent systems. Naive solvers will output the raw percentage or fail to round to 1 decimal place at round 20, causing an exact match mismatch.
