import argparse
import json
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--items', type=str, required=True)
    parser.add_argument('--gold', type=str, required=True)
    args = parser.parse_args()

    items = {}
    with open(args.items, "r") as f:
        for line in f:
            d = json.loads(line)
            items[d["id"]] = d

    gold = {}
    with open(args.gold, "r") as f:
        for line in f:
            d = json.loads(line)
            gold[d["id"]] = d

    assert len(items) > 0, "No items found"
    assert len(items) == len(gold), "Mismatched items and gold lengths"

    for item_id, item in items.items():
        assert item_id in gold, f"Missing gold for {item_id}"

        bundle_dir = os.path.dirname(args.items)
        filepath = os.path.join(bundle_dir, item["filename"])
        assert os.path.exists(filepath), f"File missing: {filepath}"

        # Check that it's a binary file with reasonable size
        sz = os.path.getsize(filepath)
        assert 100 < sz < 1000, f"Unexpected file size for {filepath}: {sz}"

    print(f"Verified {len(items)} items successfully.")

if __name__ == "__main__":
    main()
