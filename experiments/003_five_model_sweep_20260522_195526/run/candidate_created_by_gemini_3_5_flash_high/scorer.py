#!/usr/bin/env python3
import os
import sys
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="Mutative Assembly Inversion scorer")
    parser.add_argument("--gold", type=str, required=True, help="Path to gold JSONL file")
    parser.add_argument("--predictions", type=str, required=True, help="Path to predictions JSONL file")
    parser.add_argument("--out", type=str, required=True, help="Path to write the output score report JSON")
    args = parser.parse_args()
    
    if not os.path.exists(args.gold):
        print(f"Error: Gold file not found at {args.gold}", file=sys.stderr)
        sys.exit(1)
        
    if not os.path.exists(args.predictions):
        print(f"Error: Predictions file not found at {args.predictions}", file=sys.stderr)
        sys.exit(1)
        
    # Load gold answers
    golds = {}
    with open(args.gold, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                item_id = data.get("id")
                ans = data.get("answer")
                if not item_id or ans is None:
                    print(f"Error: Gold missing 'id' or 'answer' on line {line_num} in {args.gold}", file=sys.stderr)
                    sys.exit(1)
                golds[item_id] = str(ans).strip()
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line {line_num} in {args.gold}: {e}", file=sys.stderr)
                sys.exit(1)
                
    # Load predictions
    predictions = {}
    with open(args.predictions, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                item_id = data.get("id")
                ans = data.get("answer")
                if not item_id or ans is None:
                    print(f"Error: Prediction missing 'id' or 'answer' on line {line_num} in {args.predictions}", file=sys.stderr)
                    sys.exit(1)
                predictions[item_id] = str(ans).strip()
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line {line_num} in {args.predictions}: {e}", file=sys.stderr)
                sys.exit(1)
                
    # Grade predictions
    correct_count = 0
    total_count = len(golds)
    details = {}
    
    for item_id, gold_ans in golds.items():
        pred_ans = predictions.get(item_id, None)
        
        is_correct = False
        if pred_ans is not None:
            # Check exact match
            if pred_ans.replace(" ", "") == gold_ans.replace(" ", ""):
                is_correct = True
                
        if is_correct:
            correct_count += 1
            status = "correct"
        else:
            status = "incorrect"
            
        details[item_id] = {
            "status": status,
            "gold": gold_ans,
            "prediction": pred_ans
        }
        
    accuracy = correct_count / total_count if total_count > 0 else 0.0
    
    report = {
        "accuracy": accuracy,
        "correct": correct_count,
        "total": total_count,
        "details": details
    }
    
    # Write report
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"Scoring complete. Accuracy: {accuracy:.4f} ({correct_count}/{total_count}). Wrote report to {args.out}.")
    sys.exit(0)

if __name__ == "__main__":
    main()
