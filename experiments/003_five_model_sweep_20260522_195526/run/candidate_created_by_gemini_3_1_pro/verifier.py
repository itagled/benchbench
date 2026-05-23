import argparse
import json
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", required=True)
    parser.add_argument("--gold", required=True)
    args = parser.parse_args()
    
    assert os.path.exists(args.items), f"Items file missing: {args.items}"
    assert os.path.exists(args.gold), f"Gold file missing: {args.gold}"
    
    with open(args.items) as f:
        items = [json.loads(line) for line in f]
    with open(args.gold) as f:
        golds = [json.loads(line) for line in f]
        
    assert len(items) == len(golds), "Count mismatch"
    for item, gold in zip(items, golds):
        assert item["id"] == gold["id"]
        assert "grid" in item
        assert "initial_state" in item
        assert "commands" in item
        assert "answer" in gold
        assert len(gold["answer"].split("-")) == 4
        
    print("Verification passed.")

if __name__ == "__main__":
    main()
