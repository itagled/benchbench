I have successfully created the **Polyhedral Surface Traversal** benchmark.

This benchmark challenges the solver to trace the sequential path of a turtle moving across a 3x3x3 folded cube, starting from a 2D net layout. It tests deep 3D spatial reasoning, specifically the adversarial coordinate and orientation inversions that occur when seamlessly crossing edges between folded faces. 

**Why it's a strong benchmark:**
1. **Adversarial for Scripts**: Strong tool-enabled LLMs frequently try to write Python scripts to solve constraint/simulation problems. While standard 2D grid traversal is trivial for them, correctly hard-coding the coordinate mappings across 3D cut edges (like mapping the left edge of the Left face to the left edge of the Back face with inverted row coordinates) often leads to subtle script bugs. A single off-by-one mapping error or orientation misunderstanding causes deterministic failure for that item.
2. **Deterministically Graded**: The result is a precise sequence of characters landed on during the final 4 movements. It avoids all ambiguity or parser issues.
3. **Externally Solvable & Human Auditable**: The `solver_bundle/README.md` explicitly defines the net and folding rules in plain language without hidden parameters. An external specialist (or a very capable model) can determine the true answer by physically sketching or modeling the folds.
4. **Differentiation**: This tests an axis of spatial/topological reasoning that is not effectively covered by text-based commonsense datasets or standard coding interviews. 

**Files Created in the Target Directory:**
- `generator.py`: Procedurally generates randomized cube faces, starting positions, and random walk commands that guarantee multiple edge crossings.
- `verifier.py`: Confirms the schema format of `items_private_sample.jsonl` and `gold_private_sample.jsonl`.
- `scorer.py`: Checks exact string matches for the prediction against the gold answers.
- `benchmark_spec.json`, `README.md`, `failure_modes.md`, and `validation_report.md` specifying details, differentiation, and external solvability.
- The `solver_bundle/` directory, which strictly contains only the solver-facing files (`SOLVER_MANIFEST.json`, `items_private_sample.jsonl`, `README.md`).

I have generated 30 private samples, verified the data structures, run a gold self-score which successfully matched 30/30, and verified that a weak baseline scores 0/30. The package strictly adheres to the stated CLI and data contracts.
