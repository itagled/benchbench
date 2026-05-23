import json
import hashlib
from solver_bundle.compressor import decompress, DecompressionError

def main():
    items = []
    with open("solver_bundle/items_private_sample.jsonl", "r") as f:
        for line in f:
            items.append(json.loads(line))

    predictions = []
    for item in items:
        try:
            with open(f"solver_bundle/{item['filename']}", "rb") as f:
                comp = f.read()
            uncomp = decompress(comp, item["uncompressed_size"])
            ans = hashlib.sha256(uncomp).hexdigest()
        except DecompressionError:
            ans = "error"

        predictions.append({
            "id": item["id"],
            "answer": ans
        })

    with open("predictions_baseline.jsonl", "w") as f:
        for p in predictions:
            f.write(json.dumps(p) + "\n")

if __name__ == "__main__":
    main()
