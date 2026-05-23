# SMRM VM Solver Packet: Mutative Assembly Inversion (MAI)

Welcome to the **Mutative Assembly Inversion (MAI)** benchmark. This packet contains all necessary information to solve the evaluation puzzles in `items_private_sample.jsonl`.

## Task Overview

Each item in `items_private_sample.jsonl` contains a single logical puzzle. You are given:
- **`id`**: Unique identifier for the puzzle.
- **`initial_memory`**: An array of $N=8$ 16-bit instruction words (integers from $0$ to $65535$).
- **`disassembly`**: An array of 8 strings representing the disassembled initial instructions for your reference.
- **`initial_registers`**: The initial values of `R2` and `R3`. Registers `R0` and `R1` are unknown 8-bit inputs.
- **`target_registers`**: The exact final values that `R0`, `R1`, `R2`, and `R3` must have after program termination.
- **`max_steps`**: The maximum instruction execution limit (50).

Your goal is to find the **unique** pair of 8-bit inputs `(R0, R1)` (each in the range $[0, 255]$) that will cause the SMRM VM to execute, terminate, and finish with the exact register values specified in `target_registers`.

There is guaranteed to be **exactly one** unique solution for each puzzle.

## SMRM VM Specifications

The Self-Modifying Register Machine (SMRM) operates under these deterministic rules:

### 1. State representation
- **Registers**: `R0`, `R1`, `R2`, `R3`. All are 8-bit unsigned integers (values $0$ to $255$). Arithmetic overflow/underflow wraps modulo 256.
- **Memory**: 8 instruction words, each is a 16-bit unsigned integer (values $0$ to $65535$).
- **Program Counter (PC)**: Points to the index ($0$ to $7$) of the instruction being fetched. Starts at $0$.

### 2. Instruction Decoding
A 16-bit instruction word is split into four 4-bit nibbles:
- `OP` = `(word >> 12) & 0xF` (Instruction opcode)
- `A` = `(word >> 8) & 0xF`  (First operand nibble)
- `B` = `(word >> 4) & 0xF`  (Second operand nibble)
- `C` = `word & 0xF`         (Third operand nibble)

### 3. Execution Cycle
At each clock step:
1. Fetch the instruction word `W = memory[PC]`.
2. Increment `PC = (PC + 1) % 8`.
3. Decode `W` into `OP`, `A`, `B`, `C`.
4. Execute `OP` as detailed below.
5. If `HALT` is executed or the step count reaches `max_steps`, execution halts.

### 4. Instruction Set Architecture (ISA)

| OP | Name | Operands | Action |
|---|---|---|---|
| **`0x0`** | `ADD` | `dst, src1, src2` | Let `dst = A % 4`, `src1 = B % 4`, `src2 = C % 4`. <br>`R[dst] = (R[src1] + R[src2]) % 256` |
| **`0x1`** | `SUB` | `dst, src1, src2` | Let `dst = A % 4`, `src1 = B % 4`, `src2 = C % 4`. <br>`R[dst] = (R[src1] - R[src2]) % 256` |
| **`0x2`** | `MUL` | `dst, src1, src2` | Let `dst = A % 4`, `src1 = B % 4`, `src2 = C % 4`. <br>`R[dst] = (R[src1] * R[src2]) % 256` |
| **`0x3`** | `XOR` | `dst, src1, src2` | Let `dst = A % 4`, `src1 = B % 4`, `src2 = C % 4`. <br>`R[dst] = R[src1] ^ R[src2]` |
| **`0x4`** | `AND` | `dst, src1, src2` | Let `dst = A % 4`, `src1 = B % 4`, `src2 = C % 4`. <br>`R[dst] = R[src1] & R[src2]` |
| **`0x5`** | `OR`  | `dst, src1, src2` | Let `dst = A % 4`, `src1 = B % 4`, `src2 = C % 4`. <br>`R[dst] = R[src1] \| R[src2]` |
| **`0x6`** | `SHL` | `dst, src, shift`  | Let `dst = A % 4`, `src = B % 4`, `shift = C % 8`. <br>`R[dst] = (R[src] << shift) % 256` |
| **`0x7`** | `SHR` | `dst, src, shift`  | Let `dst = A % 4`, `src = B % 4`, `shift = C % 8`. <br>`R[dst] = (R[src] >> shift) % 256` |
| **`0x8`** | `SET` | `dst, val`        | Let `dst = A % 4`, `val = (B << 4) \| C`. <br>`R[dst] = val` |
| **`0x9`** | `JNZ` | `reg, offset`     | Let `reg = A % 4`, `val = (B << 4) \| C`. Let `offset` be `val` interpreted as a signed 8-bit integer (two's complement, range -128 to 127). <br>If `R[reg] != 0`:<br>&nbsp;&nbsp;&nbsp;&nbsp;`PC = (PC - 1 + offset) % 8` <br>*(Note: PC was already incremented to PC+1 after fetch. PC-1 points to the current JNZ address).* |
| **`0xA`** | `MUT` | `target, reg`     | Let `target = A % 8`, `reg = B % 4`. <br>Form the 16-bit mutation word by replicating the 8-bit value of `R[reg]` in both bytes:<br>&nbsp;&nbsp;&nbsp;&nbsp;`mutation = (R[reg] << 8) \| R[reg]` <br>Mutate memory: `memory[target] = (memory[target] ^ mutation) & 0xFFFF` |
| **`0xB`** | `HALT`| | Stop execution immediately. |

*   **Opcode > `0xB` (or unknown opcodes)** are executed as **`NOP`** (no operation; advances `PC`). Memory mutations can produce opcodes $> 11$. They run safely as NOPs.

## Output Submission Format

For each puzzle ID, output a single line in your predictions file formatted exactly as:
`R0=X,R1=Y`
where `X` and `Y` are the decimal values in $[0, 255]$.
Example:
`{"id": "mai_0", "answer": "R0=42,R1=137"}`
