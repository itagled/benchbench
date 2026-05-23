#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


def extract_thresholds(text: str):
    allow_max = int(re.search(r"ALLOW.*<= (\d+)", text).group(1))
    review_max = int(re.search(r"REVIEW.*<= (\d+) and greater", text).group(1))
    green_max = int(re.search(r"GREEN.*<= (\d+)", text).group(1))
    amber_max = int(re.search(r"AMBER.*<= (\d+) and greater", text).group(1))
    return allow_max, review_max, green_max, amber_max


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    bundle_root = args.items.parent
    rows = [json.loads(line) for line in args.items.read_text(encoding="utf-8").splitlines() if line.strip()]

    with args.out.open("w", encoding="utf-8") as handle:
        for row in rows:
            charter = (bundle_root / row["charter"]).read_text(encoding="utf-8")
            case = json.loads((bundle_root / row["case_file"]).read_text(encoding="utf-8"))
            allow_max, review_max, green_max, amber_max = extract_thresholds(charter)
            risk = len(case["flags"]) + case["quantity"]
            fee = case["quantity"] + case["declared_units"]
            if risk <= allow_max:
                verdict = "ALLOW"
            elif risk <= review_max:
                verdict = "REVIEW"
            else:
                verdict = "DENY"
            if fee <= green_max:
                lane = "GREEN"
            elif fee <= amber_max:
                lane = "AMBER"
            else:
                lane = "RED"
            answer = f"verdict={verdict};lane={lane};fee={fee}"
            handle.write(json.dumps({"id": row["id"], "answer": answer}, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
