import os
import json
import argparse
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Score MFN-Cascade benchmark predictions.")
    parser.add_argument("--gold", type=str, required=True, help="Path to gold JSONL file")
    parser.add_argument("--predictions", type=str, required=True, help="Path to predictions JSONL file")
    parser.add_argument("--out", type=str, required=True, help="Path to write score report JSON")
    return parser.parse_args()

def main():
    args = parse_args()

    # 1. Load gold answers
    if not os.path.exists(args.gold):
        print(f"Error: Gold file not found at {args.gold}")
        sys.exit(1)

    gold = {}
    with open(args.gold, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                gold[data["id"]] = data["answer"]
            except Exception as e:
                print(f"Error: Failed to parse gold line {line_num}: {e}")
                sys.exit(1)

    # 2. Load predictions
    if not os.path.exists(args.predictions):
        print(f"Error: Predictions file not found at {args.predictions}")
        sys.exit(1)

    predictions = {}
    with open(args.predictions, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if "id" not in data or "answer" not in data:
                    print(f"Warning: Predictions line {line_num} missing required 'id' or 'answer' keys. Skipping.")
                    continue
                predictions[data["id"]] = data["answer"]
            except Exception as e:
                print(f"Error: Failed to parse predictions line {line_num}: {e}")
                sys.exit(1)

    # 3. Compute score
    correct_count = 0
    total_count = len(gold)

    detailed_results = []

    for item_id, gold_ans in gold.items():
        pred_ans = predictions.get(item_id)

        is_correct = False
        if pred_ans is not None:
            # Normalizing answer formats: strip whitespace, convert to lowercase
            norm_gold = str(gold_ans).strip().lower()
            norm_pred = str(pred_ans).strip().lower()
            if norm_gold == norm_pred:
                is_correct = True

        if is_correct:
            correct_count += 1

        detailed_results.append({
            "id": item_id,
            "gold": gold_ans,
            "prediction": pred_ans,
            "correct": is_correct
        })

    accuracy = correct_count / total_count if total_count > 0 else 0.0

    report = {
        "benchmark": "mfn_cascade",
        "total_items": total_count,
        "correct_predictions": correct_count,
        "accuracy": accuracy,
        "results": detailed_results
    }

    # 4. Write report
    try:
        with open(args.out, "w") as f:
            json.dump(report, f, indent=4)
        print(f"Score report saved to {args.out}")
    except Exception as e:
        print(f"Error: Failed to write score report to {args.out}: {e}")
        sys.exit(1)

    print(f"Overall Accuracy: {accuracy * 100:.1f}% ({correct_count}/{total_count})")

if __name__ == "__main__":
    main()
