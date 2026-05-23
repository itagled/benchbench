import os
import json
import random
import argparse

def get_next(face, r, c, d):
    if d == 0: # Up
        if r > 0: return face, r-1, c, d
        if face == 'B': return 'A', 2, c, 0
        if face == 'A': return 'F', 2, c, 0
        if face == 'E': return 'B', 2, c, 0
        if face == 'C': return 'A', c, 0, 1
        if face == 'D': return 'A', 2-c, 2, 3
        if face == 'F': return 'E', 2, c, 0
    elif d == 1: # Right
        if c < 2: return face, r, c+1, d
        if face == 'B': return 'D', r, 0, 1
        if face == 'A': return 'D', 0, 2-r, 2
        if face == 'E': return 'D', 2, r, 0
        if face == 'C': return 'B', r, 0, 1
        if face == 'D': return 'F', 2-r, 2, 3
        if face == 'F': return 'D', 2-r, 2, 3
    elif d == 2: # Down
        if r < 2: return face, r+1, c, d
        if face == 'B': return 'E', 0, c, 2
        if face == 'A': return 'B', 0, c, 2
        if face == 'E': return 'F', 0, c, 2
        if face == 'C': return 'E', 2-c, 0, 1
        if face == 'D': return 'E', c, 2, 3
        if face == 'F': return 'A', 0, c, 2
    elif d == 3: # Left
        if c > 0: return face, r, c-1, d
        if face == 'B': return 'C', r, 2, 3
        if face == 'A': return 'C', 0, r, 2
        if face == 'E': return 'C', 2, 2-r, 0
        if face == 'C': return 'F', 2-r, 0, 1
        if face == 'D': return 'B', r, 2, 3
        if face == 'F': return 'C', 2-r, 0, 1
    raise ValueError("Invalid state")

def generate_item(item_id):
    tokens = []
    while len(tokens) < 54:
        tok = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        if tok not in tokens:
            tokens.append(tok)
    
    grid = {}
    idx = 0
    for f in ['A', 'B', 'C', 'D', 'E', 'F']:
        grid[f] = []
        for r in range(3):
            row = []
            for c in range(3):
                row.append(tokens[idx])
                idx += 1
            grid[f].append(row)
            
    start_face = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
    start_r = random.randint(0, 2)
    start_c = random.randint(0, 2)
    start_d = random.randint(0, 3)
    
    face, r, c, d = start_face, start_r, start_c, start_d
    
    dir_names = {0: 'Up', 1: 'Right', 2: 'Down', 3: 'Left'}
    initial_state = f"Start at Face {start_face}, row {start_r}, col {start_c}, facing {dir_names[start_d]}"
    
    while True:
        commands = []
        visited_tokens = []
        temp_face, temp_r, temp_c, temp_d = face, r, c, d
        
        for _ in range(40):
            action = random.choices(['M', 'L', 'R'], weights=[0.5, 0.25, 0.25])[0]
            commands.append(action)
            if action == 'M':
                temp_face, temp_r, temp_c, temp_d = get_next(temp_face, temp_r, temp_c, temp_d)
                visited_tokens.append(grid[temp_face][temp_r][temp_c])
            elif action == 'L':
                temp_d = (temp_d - 1) % 4
            elif action == 'R':
                temp_d = (temp_d + 1) % 4
                
        if len(visited_tokens) >= 4:
            break

    ans = "-".join(visited_tokens[-4:])
    
    solver_item = {
        "id": item_id,
        "grid": grid,
        "initial_state": initial_state,
        "commands": commands
    }
    
    return solver_item, ans

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-count", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out-dir", type=str, default=".")
    args = parser.parse_args()
    
    random.seed(args.seed)
    
    solver_dir = os.path.join(args.out_dir, "solver_bundle")
    os.makedirs(solver_dir, exist_ok=True)
    
    items_path = os.path.join(solver_dir, "items_private_sample.jsonl")
    gold_path = os.path.join(args.out_dir, "gold_private_sample.jsonl")
    
    with open(items_path, 'w') as f_items, open(gold_path, 'w') as f_gold:
        for i in range(args.sample_count):
            item_id = f"item_{i:03d}"
            item, ans = generate_item(item_id)
            f_items.write(json.dumps(item) + "\n")
            f_gold.write(json.dumps({"id": item_id, "answer": ans}) + "\n")

if __name__ == "__main__":
    main()
