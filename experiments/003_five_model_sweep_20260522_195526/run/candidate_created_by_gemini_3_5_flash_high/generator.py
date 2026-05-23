#!/usr/bin/env python3
import os
import sys
import json
import argparse
import random

# Instruction parser and execution logic
def parse_instruction(w):
    op = (w >> 12) & 0xF
    a = (w >> 8) & 0xF
    b = (w >> 4) & 0xF
    c = w & 0xF
    return op, a, b, c

def disassemble_instruction(w, n=8):
    op, a, b, c = parse_instruction(w)
    dst = a % 4
    src1 = b % 4
    src2 = c % 4
    reg = b % 4
    
    if op == 0:
        return f"ADD R{dst}, R{src1}, R{src2}"
    elif op == 1:
        return f"SUB R{dst}, R{src1}, R{src2}"
    elif op == 2:
        return f"MUL R{dst}, R{src1}, R{src2}"
    elif op == 3:
        return f"XOR R{dst}, R{src1}, R{src2}"
    elif op == 4:
        return f"AND R{dst}, R{src1}, R{src2}"
    elif op == 5:
        return f"OR R{dst}, R{src1}, R{src2}"
    elif op == 6:
        shift = c % 8
        return f"SHL R{dst}, R{reg}, {shift}"
    elif op == 7:
        shift = c % 8
        return f"SHR R{dst}, R{reg}, {shift}"
    elif op == 8:
        val = (b << 4) | c
        return f"SET R{dst}, {val}"
    elif op == 9:
        val = (b << 4) | c
        offset = val - 256 if val >= 128 else val
        return f"JNZ R{a % 4}, {offset}"
    elif op == 0xA:
        target = a % n
        return f"MUT {target}, R{reg}"
    elif op == 0xB:
        return "HALT"
    else:
        return f"NOP (OP={op})"

def run_smrm(memory_init, registers_init, max_steps=50):
    """
    Runs the SMRM VM.
    registers_init is [R0, R1, R2, R3]
    Returns (registers, final_memory, step_count, mut_executed, self_modified)
    """
    memory = list(memory_init)
    registers = list(registers_init)
    pc = 0
    steps = 0
    n = len(memory)
    mut_executed = False
    self_modified = False
    
    while steps < max_steps:
        w = memory[pc]
        orig_pc = pc
        pc = (pc + 1) % n
        steps += 1
        
        op = (w >> 12) & 0xF
        a = (w >> 8) & 0xF
        b = (w >> 4) & 0xF
        c = w & 0xF
        
        if op == 0x0: # ADD
            registers[a % 4] = (registers[b % 4] + registers[c % 4]) & 0xFF
        elif op == 0x1: # SUB
            registers[a % 4] = (registers[b % 4] - registers[c % 4]) & 0xFF
        elif op == 0x2: # MUL
            registers[a % 4] = (registers[b % 4] * registers[c % 4]) & 0xFF
        elif op == 0x3: # XOR
            registers[a % 4] = registers[b % 4] ^ registers[c % 4]
        elif op == 0x4: # AND
            registers[a % 4] = registers[b % 4] & registers[c % 4]
        elif op == 0x5: # OR
            registers[a % 4] = registers[b % 4] | registers[c % 4]
        elif op == 0x6: # SHL
            registers[a % 4] = (registers[b % 4] << (c % 8)) & 0xFF
        elif op == 0x7: # SHR
            registers[a % 4] = (registers[b % 4] >> (c % 8)) & 0xFF
        elif op == 0x8: # SET
            registers[a % 4] = (b << 4) | c
        elif op == 0x9: # JNZ
            val = (b << 4) | c
            offset = val - 256 if val >= 128 else val
            if registers[a % 4] != 0:
                pc = (orig_pc + offset) % n
        elif op == 0xA: # MUT
            target = a % n
            reg_val = registers[b % 4]
            mutation = (reg_val << 8) | reg_val
            old_val = memory[target]
            new_val = (old_val ^ mutation) & 0xFFFF
            if old_val != new_val:
                self_modified = True
            memory[target] = new_val
            mut_executed = True
        elif op == 0xB: # HALT
            break
        else: # NOP
            pass
            
    return registers, memory, steps, mut_executed, self_modified

def find_unique_solution(memory, r2, r3, target_regs, max_steps=50):
    """
    Search over the 65,536 (R0, R1) space to find all solutions matching target_regs.
    Returns the list of matching (r0, r1) pairs.
    """
    solutions = []
    # Fast loop over R0, R1
    for r0 in range(256):
        for r1 in range(256):
            final_regs, _, _, _, _ = run_smrm(memory, [r0, r1, r2, r3], max_steps)
            if final_regs == target_regs:
                solutions.append((r0, r1))
                if len(solutions) > 1:
                    # Early termination if multiple solutions found
                    return solutions
    return solutions

def generate_valid_puzzle(rng, item_id):
    """
    Generates a puzzle that has exactly one unique solution.
    We also enforce that it executes at least 8 steps, executes a MUT instruction,
    and the final registers depend on the inputs (i.e. not trivial).
    """
    # Allowed opcodes: ADD, SUB, MUL, XOR, SHL, SHR, SET, JNZ, MUT, HALT
    opcodes = [0, 1, 2, 3, 6, 7, 8, 9, 10, 11]
    
    attempts = 0
    while True:
        attempts += 1
        # 1. Generate a random program of length 8
        memory = []
        for _ in range(8):
            op = rng.choice(opcodes)
            a = rng.randint(0, 15)
            b = rng.randint(0, 15)
            c = rng.randint(0, 15)
            w = (op << 12) | (a << 8) | (b << 4) | c
            memory.append(w)
            
        # Ensure we have at least one MUT and HALT in the generated base program
        # (This increases the chance of interesting mutative behavior)
        has_mut = any(((w >> 12) & 0xF) == 0xA for w in memory)
        if not has_mut:
            # Inject a MUT instruction randomly
            mut_idx = rng.randint(0, 6)
            a = rng.randint(0, 7) # target memory index (0 to 7)
            b = rng.randint(0, 3) # register index (0 to 3)
            memory[mut_idx] = (0xA << 12) | (a << 8) | (b << 4) | rng.randint(0, 15)
            
        has_halt = any(((w >> 12) & 0xF) == 0xB for w in memory)
        if not has_halt:
            # Inject HALT at the end (index 7)
            memory[7] = (0xB << 12) | rng.randint(0, 4095)
            
        # 2. Select random constants for R2, R3
        r2 = rng.randint(0, 255)
        r3 = rng.randint(0, 255)
        
        # 3. Select a target gold solution (R0_g, R1_g)
        r0_g = rng.randint(0, 255)
        r1_g = rng.randint(0, 255)
        
        # 4. Run the program on the gold solution
        target_regs, final_mem, steps, mut_executed, self_modified = run_smrm(
            memory, [r0_g, r1_g, r2, r3], max_steps=50
        )
        
        # 5. Filter for interestingness
        # - Must execute at least 8 steps to avoid trivial one-step runs
        # - Must execute a MUT instruction during execution
        # - Must have modified memory at least once
        if steps < 8 or not mut_executed or not self_modified:
            continue
            
        # 6. Verify uniqueness of solution
        solutions = find_unique_solution(memory, r2, r3, target_regs, max_steps=50)
        
        if len(solutions) == 1 and solutions[0] == (r0_g, r1_g):
            # Found a high quality puzzle!
            disassembly = [disassemble_instruction(w, 8) for w in memory]
            
            item = {
                "id": item_id,
                "initial_memory": memory,
                "disassembly": disassembly,
                "initial_registers": {
                    "R2": r2,
                    "R3": r3
                },
                "target_registers": {
                    "R0": target_regs[0],
                    "R1": target_regs[1],
                    "R2": target_regs[2],
                    "R3": target_regs[3]
                },
                "max_steps": 50
            }
            
            gold = {
                "id": item_id,
                "answer": f"R0={r0_g},R1={r1_g}"
            }
            
            return item, gold

def main():
    parser = argparse.ArgumentParser(description="Mutative Assembly Inversion puzzle generator")
    parser.add_argument("--sample-count", type=int, default=30, help="Number of puzzles to generate")
    parser.add_argument("--seed", type=int, default=20260516, help="Random seed for reproducibility")
    parser.add_argument("--out-dir", type=str, default=".", help="Output directory path")
    args = parser.parse_args()
    
    # Initialize random number generator
    rng = random.Random(args.seed)
    
    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(os.path.join(args.out_dir, "solver_bundle"), exist_ok=True)
    
    items = []
    golds = []
    
    print(f"Generating {args.sample_count} puzzles with seed {args.seed}...")
    for i in range(args.sample_count):
        item_id = f"mai_{i}"
        item, gold = generate_valid_puzzle(rng, item_id)
        items.append(item)
        golds.append(gold)
        print(f"  Generated {item_id} successfully.")
        
    # Write solver bundle items
    items_path = os.path.join(args.out_dir, "solver_bundle", "items_private_sample.jsonl")
    with open(items_path, "w") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")
            
    # Write gold answers
    gold_path = os.path.join(args.out_dir, "gold_private_sample.jsonl")
    with open(gold_path, "w") as f:
        for gold in golds:
            f.write(json.dumps(gold) + "\n")
            
    print(f"Finished. Wrote {items_path} and {gold_path}.")

if __name__ == "__main__":
    main()
