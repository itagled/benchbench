# Mutative Assembly Inversion (MAI)

Welcome to the **Mutative Assembly Inversion (MAI)** benchmark. This benchmark evaluates a solver's ability to emulate, reverse engineer, and solve constraints on a custom self-modifying computer architecture.

## Overview of the Task

You are given:
1. **Initial Program Memory**: An array of $N=8$ 16-bit instruction words (both as raw decimal integers and as disassembly).
2. **Initial Register State**: Registers `R0`, `R1`, `R2`, `R3`. `R2` and `R3` are pre-initialized to specific known constant 8-bit integers. Registers `R0` and `R1` are the secret inputs (wildcards) that you must determine.
3. **Target Final Register State**: The register values that all 4 registers must have when the program terminates.
4. **Step Limit**: The maximum number of instructions the VM can execute (e.g., 50 steps). If the program executes more than this limit without halting, it is terminated, and the final register values at that point are evaluated.

Your task is to find the **unique** pair of 8-bit values for `R0` and `R1` (each in the range $[0, 255]$) that will cause the program to terminate with the exact target register state. There is guaranteed to be **exactly one** unique solution.

## The Self-Modifying Register Machine (SMRM) Specification

The SMRM is an 8-bit register machine with a small program memory and self-modifying features.

### Machine State
*   **Registers**: Four 8-bit registers, `R0`, `R1`, `R2`, `R3`. All register values are unsigned 8-bit integers (range $0$ to $255$). Register operations are performed modulo 256.
*   **Memory**: A fixed-size array of $N=8$ 16-bit words (integers from $0$ to $65535$), indexed $0$ to $7$.
*   **Program Counter (PC)**: An integer pointing to the current instruction in memory (range $0$ to $7$). PC starts at $0$.

### Instruction Encoding
Each 16-bit instruction word is split into four 4-bit nibbles, denoted in hexadecimal as `OP`, `A`, `B`, and `C`:
```
   15   12 11    8 7     4 3     0
  +-------+-------+-------+-------+
  |  OP   |   A   |   B   |   C   |
  +-------+-------+-------+-------+
```
*   `OP` = `(word >> 12) & 0xF`
*   `A`  = `(word >> 8) & 0xF`
*   `B`  = `(word >> 4) & 0xF`
*   `C`  = `word & 0xF`

### Execution Loop
At each step of execution:
1. Fetch the 16-bit instruction word `W = memory[PC]`.
2. Increment the program counter: `PC = (PC + 1) % N`.
3. Decode `W` into `OP`, `A`, `B`, `C`.
4. Execute the instruction according to `OP`.
5. If a `HALT` opcode is executed, or if the number of executed steps reaches `MAX_STEPS`, execution stops.

### Instruction Set Reference

| Opcode (OP) | Name | Syntax | Semantic Description |
| :--- | :--- | :--- | :--- |
| **`0x0`** | `ADD` | `ADD dst, src1, src2` | `dst = A % 4`, `src1 = B % 4`, `src2 = C % 4`<br>`R[dst] = (R[src1] + R[src2]) % 256` |
| **`0x1`** | `SUB` | `SUB dst, src1, src2` | `dst = A % 4`, `src1 = B % 4`, `src2 = C % 4`<br>`R[dst] = (R[src1] - R[src2]) % 256` |
| **`0x2`** | `MUL` | `MUL dst, src1, src2` | `dst = A % 4`, `src1 = B % 4`, `src2 = C % 4`<br>`R[dst] = (R[src1] * R[src2]) % 256` |
| **`0x3`** | `XOR` | `XOR dst, src1, src2` | `dst = A % 4`, `src1 = B % 4`, `src2 = C % 4`<br>`R[dst] = R[src1] ^ R[src2]` |
| **`0x4`** | `AND` | `AND dst, src1, src2` | `dst = A % 4`, `src1 = B % 4`, `src2 = C % 4`<br>`R[dst] = R[src1] & R[src2]` |
| **`0x5`** | `OR`  | `OR dst, src1, src2`  | `dst = A % 4`, `src1 = B % 4`, `src2 = C % 4`<br>`R[dst] = R[src1] \| R[src2]` |
| **`0x6`** | `SHL` | `SHL dst, src, shift`  | `dst = A % 4`, `src = B % 4`, `shift = C % 8`<br>`R[dst] = (R[src] << shift) % 256` |
| **`0x7`** | `SHR` | `SHR dst, src, shift`  | `dst = A % 4`, `src = B % 4`, `shift = C % 8`<br>`R[dst] = (R[src] >> shift) % 256` |
| **`0x8`** | `SET` | `SET dst, val`        | `dst = A % 4`, `val = (B << 4) \| C`<br>`R[dst] = val` |
| **`0x9`** | `JNZ` | `JNZ reg, offset`     | `reg = A % 4`, `offset_val = (B << 4) \| C`<br>Let `offset` be `offset_val` interpreted as a signed 8-bit integer (range -128 to 127; two's complement).<br>If `R[reg] != 0`:<br>&nbsp;&nbsp;&nbsp;&nbsp;`PC = (PC - 1 + offset) % N` |
| **`0xA`** | `MUT` | `MUT target, reg`     | `target = A % N`, `reg = B % 4`<br>The 16-bit instruction at address `target` is XORed with a 16-bit word formed by duplicating the 8-bit value of `R[reg]` into both high and low bytes:<br>`mutation = (R[reg] << 8) \| R[reg]`<br>`memory[target] = (memory[target] ^ mutation) & 0xFFFF` |
| **`0xB`** | `HALT`| `HALT`                | Terminate program execution. |

*   *Note 1*: Opcode values of `0xC` to `0xF` (and any other unmapped opcodes) are executed as **`NOP`** (no operation; simply advances PC). This is highly relevant because instructions can mutate during execution and their opcodes might change to values $> 11$.
*   *Note 2 (JNZ Offset)*: The `JNZ` instruction jumps relative to the address of the `JNZ` instruction itself. Because `PC` is already incremented by 1 during step 2 of the fetch-decode loop, the jump formula subtracted 1 (`PC - 1 + offset`) to align it relative to the original `JNZ` address.
*   *Note 3 (MUT Target)*: A program can mutate its own instructions, including the instruction currently being executed or instructions that will be executed in future steps.

## Answer Format

The output must be formatted exactly as `R0=X,R1=Y`, where `X` and `Y` are the decimal integer values of `R0` and `R1` (e.g. `R0=42,R1=137`).
