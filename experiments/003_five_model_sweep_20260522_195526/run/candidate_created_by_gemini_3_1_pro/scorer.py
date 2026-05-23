import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", required=True)
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    with open(args.gold) as f:
        golds = {json.loads(line)["id"]: json.loads(line)["answer"] for line in f}
        
    with open(args.predictions) as f:
        preds = {json.loads(line)["id"]: json.loads(line)["answer"] for line in f}
        
    correct = 0
    total = len(golds)
    
    for k, v in golds.items():
        if k in preds and preds[k].strip().upper() == v.strip().upper():
            correct += 1
            
    result = {
        "accuracy": correct / total if total > 0 else 0,
        "correct": correct,
        "total": total
    }
    
    with open(args.out, 'w') as f:
        json.dump(result, f, indent=2)
        
    print(f"Score: {correct}/{total}")

if __name__ == "__main__":
    main()
