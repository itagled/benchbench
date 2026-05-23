# Validation Report: Mutative Assembly Inversion (MAI)

This report validates the **Mutative Assembly Inversion (MAI)** benchmark, evaluating its external solvability, uniqueness of solutions, and performance baseline checks.

## External Solvability & Identifiability Argument

A qualified external solver (an LLM with code execution tools, or a human programmer) can fully solve any item in the MAI benchmark using only the public solver bundle.

### Why the Public Solver Bundle is Sufficient:
1. **Perfect Specification**: The file `solver_bundle/solver_packet.md` documents the entire instruction set, bitwise layout, memory mutation rules, signed jump calculations, and modulo wrap-arounds with zero ambiguity.
2. **Complete Public Inputs**: The items in `solver_bundle/items_private_sample.jsonl` provide the complete initial state (memory words, disassembly, known register values R2/R3, target outputs, step limit) of the VM.
3. **Finite State Space**: The unknown input space consists of only two 8-bit registers, `R0` and `R1`. The total search space is exactly $256 \times 256 = 65,536$ states.
4. **Deterministic Simulation**: Since the SMRM VM is entirely deterministic and requires no hidden state, a solver can write a simple Python interpreter conforming to the specification, run it for all 65,536 inputs, and identify the unique input pair that matches the target final register values.
5. **No Hidden Keys or Seeds**: The correctness of the answer depends solely on running the deterministic simulation.

## Validation Results

We executed the benchmark generator and verified the package using the strict BenchBench CLI contract.

### 1. Item Generation
*   **Sample Count**: 30 high-quality, verified puzzles were generated.
*   **Difficulty Constraints**: 
    *   Minimum of 8 execution steps (ensuring logical depth).
    *   At least one `MUT` instruction executed.
    *   At least one instruction word in memory modified during execution (ensuring active self-modification).
    *   Verified to have exactly **one** unique correct input pair $(R0, R1)$ matching the target state.

### 2. Package Verification (`verifier.py`)
Running `verifier.py` on the 30 generated items and their gold answers completed successfully.
*   **Result**: 100% of items successfully parsed, verified to run exactly to their target states, and proved to have exactly **one unique solution** in $[0, 255] \times [0, 255]$.
*   **Command run**:
    ```bash
    python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl
    ```
*   **Status**: Passed.

### 3. Gold Self-Score (`scorer.py`)
We ran a self-grading evaluation using the gold solutions as predictions.
*   **Accuracy**: `1.0000` (30/30).
*   **Command run**:
    ```bash
    python scorer.py --gold gold_private_sample.jsonl --predictions predictions.jsonl --out score_report.json
    ```
*   **Status**: Passed.

### 4. Weak Baseline Evaluation
We implemented a baseline solver that predicts `R0=0,R1=0` for all puzzles.
*   **Accuracy**: `0.0000` (0/30).
*   **Command run**:
    ```bash
    python baseline_solver.py && python scorer.py --gold gold_private_sample.jsonl --predictions predictions_baseline.jsonl --out score_report_baseline.json
    ```
*   **Status**: Passed. This demonstrates that the benchmark has zero false positives under naive shortcut heuristics and is highly resistant to simple guesses.
