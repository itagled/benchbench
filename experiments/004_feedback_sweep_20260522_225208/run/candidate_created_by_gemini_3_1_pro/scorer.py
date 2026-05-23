import argparse
import json
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gold', type=str, required=True)
    parser.add_argument('--predictions', type=str, required=True)
    parser.add_argument('--out', type=str, required=True)
    args = parser.parse_args()

    gold = {}
    with open(args.gold, "r") as f:
        for line in f:
            d = json.loads(line)
            gold[d["id"]] = d["answer"].strip().lower()

    preds = {}
    if os.path.exists(args.predictions):
        with open(args.predictions, "r") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    if "id" in d and "answer" in d:
                        preds[d["id"]] = str(d["answer"]).strip().lower()
                except Exception:
                    pass

    correct = 0
    total = len(gold)

    for item_id, g_ans in gold.items():
        if item_id in preds and preds[item_id] == g_ans:
            correct += 1

    score = {
        "correct": correct,
        "total": total,
        "accuracy": correct / total if total > 0 else 0.0
    }

    with open(args.out, "w") as f:
        json.dump(score, f, indent=2)

if __name__ == "__main__":
    main()
