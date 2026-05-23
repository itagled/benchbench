# Failure Modes: Mutative Assembly Inversion (MAI)

This document describes the anticipated failure modes for solvers (both humans and LLMs) attempting the MAI benchmark. Due to the highly dynamic and self-modifying nature of the Self-Modifying Register Machine (SMRM), standard reasoning patterns often fail.

## 1. Emulation Bugs (Implementation Errors)

To solve these puzzles, a tool-enabled LLM or human must implement their own emulator. Subtle implementation details will cause emulation bugs:

*   **Mutation Operator Errors**: The `MUT target, reg` instruction replicates the 8-bit register value into a 16-bit word (`(reg_val << 8) | reg_val`) before XORing it with the 16-bit instruction at `target`. Solvers often incorrectly XOR using only the 8-bit value or shift by a different amount, leading to wrong program states.
*   **Off-by-One PC & JNZ Jump Logic**: During instruction execution, `PC` is incremented *before* the opcode is executed. Jumps are computed relative to the original `JNZ` instruction address (using `PC - 1 + offset`). Solvers frequently apply offsets relative to the incremented `PC` or forget the modulo-8 wrap-around, executing incorrect instructions.
*   **Modulo Wrap-around**: Registers are 8-bit ($0 \le R < 256$) and wrap modulo 256. Memory cells are 16-bit ($0 \le W < 65536$) and wrap modulo 65536. Neglecting wrap-around in addition, subtraction, or multiplication leads to incorrect emulator results.
*   **NOP Opcode Handling**: When an instruction is mutated, its opcode (high 4 bits) can become $> 11$ (e.g., $12$ to $15$). The VM executes these mutated words as a `NOP` (advancing PC+1 safely). An incorrect emulator implementation might throw an exception or crash on unknown opcodes instead of running them as NOPs.

## 2. Ineffective Search Strategy (Search Failure)

The SMRM is a highly chaotic, discontinuous dynamical system. Small changes in the initial registers $R0, R1$ completely alter the control flow, instruction mutations, and final register states.

*   **Manual Trace Guessing**: Models trying to trace the execution step-by-step in natural language will inevitably fail after $2$ or $3$ steps. The cognitive load of tracking both mutating instruction memory and 4 registers is too high.
*   **Local/Greedy Search**: Attempting to use local search (like hill climbing) or gradient heuristics will fail because the register space is highly discontinuous. The output register state does not vary smoothly with inputs.
*   **Symbolic/SMT Failures**: Trying to construct symbolic formulas using Z3 without an exact model of the SMRM VM will lead to logic errors in the symbolic translation. A brute-force search over the $256 \times 256 = 65,536$ search space is extremely fast in Python ($< 0.1\text{s}$), yet models may overcomplicate and write complex, buggy backtracking searches instead of a simple exhaustive grid search.

## 3. Ambiguity and Under-specification Traps

*   **Signed vs Unsigned JNZ**: The JNZ offset is an 8-bit two's complement signed integer (values $128 \dots 255$ represent $-128 \dots -1$). Solvers treating it as unsigned will jump forward past the program boundaries, leading to incorrect state tracking.
