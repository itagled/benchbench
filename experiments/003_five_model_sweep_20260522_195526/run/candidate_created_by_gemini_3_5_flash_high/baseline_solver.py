#!/usr/bin/env python3
import json
import sys

def main():
    items_path = "solver_bundle/items_private_sample.jsonl"
    pred_path = "predictions_baseline.jsonl"
    
    try:
        with open(items_path, "r") as f_in, open(pred_path, "w") as f_out:
            for line in f_in:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                item_id = item["id"]
                
                # Weak baseline: always guess R0=0, R1=0
                pred = {
                    "id": item_id,
                    "answer": "R0=0,R1=0"
                }
                f_out.write(json.dumps(pred) + "\n")
        print(f"Wrote baseline predictions to {pred_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
