import os
import json
import argparse
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Verify integrity of MFN-Cascade benchmark files.")
    parser.add_argument("--items", type=str, required=True, help="Path to items JSONL file")
    parser.add_argument("--gold", type=str, required=True, help="Path to gold JSONL file")
    return parser.parse_args()

def main():
    args = parse_args()

    # 1. Check if files exist
    if not os.path.exists(args.items):
        print(f"Error: Items file not found at {args.items}")
        sys.exit(1)

    if not os.path.exists(args.gold):
        print(f"Error: Gold file not found at {args.gold}")
        sys.exit(1)

    # 2. Read and parse items
    items = []
    with open(args.items, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                items.append((line_num, data))
            except Exception as e:
                print(f"Error: Failed to parse JSON on line {line_num} of items file: {e}")
                sys.exit(1)

    # 3. Read and parse gold
    gold = {}
    with open(args.gold, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if "id" not in data or "answer" not in data:
                    print(f"Error: Gold line {line_num} does not contain required keys 'id' and 'answer'")
                    sys.exit(1)
                gold[data["id"]] = data
            except Exception as e:
                print(f"Error: Failed to parse JSON on line {line_num} of gold file: {e}")
                sys.exit(1)

    # 4. Verify count
    if len(items) != 30:
        print(f"Error: Expected exactly 30 items, found {len(items)}")
        sys.exit(1)

    if len(gold) != 30:
        print(f"Error: Expected exactly 30 gold answers, found {len(gold)}")
        sys.exit(1)

    # 5. Verify integrity and mapping
    for line_num, item in items:
        if "id" not in item or "prompt" not in item:
            print(f"Error: Item on line {line_num} is missing 'id' or 'prompt'")
            sys.exit(1)

        item_id = item["id"]
        if item_id not in gold:
            print(f"Error: Item {item_id} has no matching gold answer")
            sys.exit(1)

        # Ensure answer is not leaked in the item prompt
        prompt = item["prompt"]
        gold_ans = gold[item_id]["answer"]
        if gold_ans in prompt:
            print(f"Error: Potential leak! Gold answer '{gold_ans}' found in prompt of item {item_id}")
            sys.exit(1)

    # 6. Verify SOLVER_MANIFEST.json
    bundle_dir = os.path.dirname(os.path.abspath(args.items))
    manifest_path = os.path.join(bundle_dir, "SOLVER_MANIFEST.json")
    if not os.path.exists(manifest_path):
        print(f"Error: SOLVER_MANIFEST.json not found in solver bundle")
        sys.exit(1)

    try:
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"Error: Failed to parse SOLVER_MANIFEST.json: {e}")
        sys.exit(1)

    if "files" not in manifest or not isinstance(manifest["files"], list):
        print("Error: SOLVER_MANIFEST.json does not contain list of 'files'")
        sys.exit(1)

    for file_rel in manifest["files"]:
        full_path = os.path.join(bundle_dir, file_rel)
        if not os.path.exists(full_path):
            print(f"Error: Manifest file '{file_rel}' does not exist at {full_path}")
            sys.exit(1)

    print("Verification passed successfully! All contracts, mappings, schemas, and counts are valid.")
    sys.exit(0)

if __name__ == "__main__":
    main()
