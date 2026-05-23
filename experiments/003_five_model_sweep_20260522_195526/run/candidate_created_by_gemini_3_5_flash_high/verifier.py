#!/usr/bin/env python3
import os
import sys
import json
import argparse
import re

# Import or define the SMRM execution engine here
def parse_instruction(w):
    op = (w >> 12) & 0xF
    a = (w >> 8) & 0xF
    b = (w >> 4) & 0xF
    c = w & 0xF
    return op, a, b, c

def run_smrm(memory_init, registers_init, max_steps=50):
    memory = list(memory_init)
    registers = list(registers_init)
    pc = 0
    steps = 0
    n = len(memory)
    
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
            memory[target] = (memory[target] ^ mutation) & 0xFFFF
        elif op == 0xB: # HALT
            break
        else: # NOP
            pass
            
    return registers, memory, steps

def main():
    parser = argparse.ArgumentParser(description="Mutative Assembly Inversion verifier")
    parser.add_argument("--items", type=str, required=True, help="Path to items JSONL file")
    parser.add_argument("--gold", type=str, required=True, help="Path to gold JSONL file")
    args = parser.parse_args()
    
    if not os.path.exists(args.items):
        print(f"Error: Items file not found at {args.items}", file=sys.stderr)
        sys.exit(1)
        
    if not os.path.exists(args.gold):
        print(f"Error: Gold file not found at {args.gold}", file=sys.stderr)
        sys.exit(1)
        
    # Load items
    items = {}
    with open(args.items, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                item_id = item.get("id")
                if not item_id:
                    print(f"Error: Item missing 'id' on line {line_num} in {args.items}", file=sys.stderr)
                    sys.exit(1)
                items[item_id] = item
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line {line_num} in {args.items}: {e}", file=sys.stderr)
                sys.exit(1)
                
    # Load golds
    golds = {}
    with open(args.gold, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                gold = json.loads(line)
                gold_id = gold.get("id")
                if not gold_id:
                    print(f"Error: Gold missing 'id' on line {line_num} in {args.gold}", file=sys.stderr)
                    sys.exit(1)
                golds[gold_id] = gold
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line {line_num} in {args.gold}: {e}", file=sys.stderr)
                sys.exit(1)
                
    # Match items and golds
    item_ids = set(items.keys())
    gold_ids = set(golds.keys())
    
    if item_ids != gold_ids:
        print(f"Error: Mismatched IDs between items and golds.", file=sys.stderr)
        print(f"Items only: {item_ids - gold_ids}", file=sys.stderr)
        print(f"Golds only: {gold_ids - item_ids}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Verifying {len(items)} items...")
    
    # Format pattern for answer
    ans_pattern = re.compile(r"^R0=(\d+),R1=(\d+)$")
    
    for item_id, item in items.items():
        gold = golds[item_id]
        ans_str = gold.get("answer", "")
        
        match = ans_pattern.match(ans_str)
        if not match:
            print(f"Error for item {item_id}: Answer '{ans_str}' does not match expected format 'R0=X,R1=Y'", file=sys.stderr)
            sys.exit(1)
            
        r0_val = int(match.group(1))
        r1_val = int(match.group(2))
        
        if not (0 <= r0_val <= 255) or not (0 <= r1_val <= 255):
            print(f"Error for item {item_id}: Secret values must be in [0, 255], got R0={r0_val}, R1={r1_val}", file=sys.stderr)
            sys.exit(1)
            
        # Run simulation with these gold inputs
        memory_init = item["initial_memory"]
        r2 = item["initial_registers"]["R2"]
        r3 = item["initial_registers"]["R3"]
        max_steps = item.get("max_steps", 50)
        
        expected_regs = [
            item["target_registers"]["R0"],
            item["target_registers"]["R1"],
            item["target_registers"]["R2"],
            item["target_registers"]["R3"]
        ]
        
        actual_regs, _, steps = run_smrm(memory_init, [r0_val, r1_val, r2, r3], max_steps)
        
        if actual_regs != expected_regs:
            print(f"Error for item {item_id}: Emulation on gold answer produced {actual_regs}, but expected target is {expected_regs}", file=sys.stderr)
            sys.exit(1)
            
        # Optional: verify uniqueness to be absolutely certain
        # We perform a small check of other solutions
        solutions = []
        for test_r0 in range(256):
            for test_r1 in range(256):
                test_regs, _, _ = run_smrm(memory_init, [test_r0, test_r1, r2, r3], max_steps)
                if test_regs == expected_regs:
                    solutions.append((test_r0, test_r1))
                    if len(solutions) > 1:
                        break
            if len(solutions) > 1:
                break
                
        if len(solutions) != 1 or solutions[0] != (r0_val, r1_val):
            print(f"Error for item {item_id}: Uniqueness check failed! Found multiple solutions or no solution. Solutions: {solutions}", file=sys.stderr)
            sys.exit(1)
            
        print(f"  Item {item_id} verified successfully (unique solution R0={r0_val}, R1={r1_val}; steps={steps}).")
        
    print("Verification completed successfully. All items are valid and correct.")
    sys.exit(0)

if __name__ == "__main__":
    main()
