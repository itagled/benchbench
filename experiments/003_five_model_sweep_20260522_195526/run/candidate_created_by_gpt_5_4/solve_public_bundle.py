#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


def parse_case(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_charter(text: str):
    data = {}
    data["allow_max"] = int(re.search(r"ALLOW.*<= (\d+)", text).group(1))
    data["review_max"] = int(re.search(r"REVIEW.*<= (\d+) and greater", text).group(1))
    data["green_max"] = int(re.search(r"GREEN.*<= (\d+)", text).group(1))
    data["amber_max"] = int(re.search(r"AMBER.*<= (\d+) and greater", text).group(1))
    data["fee_base"] = int(re.search(r"start with (\d+)", text).group(1))
    data["quantity_multiplier"] = int(re.search(r"quantity \* (\d+)", text).group(1))
    data["zones"] = {name: int(value) for name, value in re.findall(r"zone `([^`]+)`: (\d+)", text)}
    data["tiers"] = {name: int(value) for name, value in re.findall(r"tier `(T\d)`: (\d+)", text)}
    data["categories"] = {name: int(value) for name, value in re.findall(r"category `([^`]+)`: (\d+)", text)}
    flags = re.findall(r"add risk `(\d+)` if flag `([^`]+)` is present", text)
    data["flags"] = {flag: int(value) for value, flag in flags}
    data["mismatch_penalty"] = int(re.search(r"declared_units != quantity`, add risk `(\d+)`", text).group(1))
    data["stale_cutoff"] = int(re.search(r"record_age >= (\d+)`, add risk", text).group(1))
    data["stale_penalty"] = int(re.search(r"record_age >= \d+`, add risk `(\d+)`", text).group(1))
    data["weekend_penalty"] = int(re.search(r"weekend = true`, add fee `(\d+)`", text).group(1))
    return data


def parse_amendments(text: str):
    lines = text.splitlines()
    out = {}
    out["risk_replace_pair"] = re.search(r"zone is `([^`]+)` and category is `([^`]+)`, replace the entire risk score with `(\d+)`", text).groups()
    out["fee_replace_pair"] = re.search(r"zone is `([^`]+)` and category is `([^`]+)`, replace the running fee with `(\d+)`", text).groups()
    out["preclear_replace"] = re.search(r"zone is `([^`]+)` and `preclear = true`, replace the risk score with the smaller of its current value and `(\d+)`; then add fee `(\d+)`", text).groups()
    seal_match = re.search(r"If seal is `([^`]+)`, subtract fee `(\d+)` if flag `([^`]+)` is (absent|present)", text)
    out["seal_rule"] = seal_match.groups()
    out["zone_category_fee_add"] = re.search(r"zone is `([^`]+)` and category is `([^`]+)`, add fee `(\d+)`", text).groups()
    out["quantity_risk_add"] = re.search(r"quantity >= (\d+)`, add risk `(\d+)`", text).groups()
    out["escort_waiver"] = re.search(r"quantity <= (\d+)` and `escort = true`, subtract fee `(\d+)`", text).groups()
    out["mismatch_waiver"] = re.search(r"declared_units != quantity` and `preclear = true`, subtract fee `(\d+)`", text).group(1)
    out["manual_review"] = re.search(r"at least `(\d+)`, force the final risk score to be at least `(\d+)`", text).groups()
    return out


def solve_one(bundle_root: Path, row):
    charter = parse_charter((bundle_root / row["charter"]).read_text(encoding="utf-8"))
    amendments = parse_amendments((bundle_root / row["amendments"]).read_text(encoding="utf-8"))
    case = parse_case(bundle_root / row["case_file"])

    risk = charter["zones"][case["zone"]] + charter["tiers"][case["tier"]] + charter["categories"][case["category"]]
    fee = charter["fee_base"] + case["quantity"] * charter["quantity_multiplier"]
    risk += sum(charter["flags"][flag] for flag in case["flags"])
    if case["declared_units"] != case["quantity"]:
        risk += charter["mismatch_penalty"]
    if case["record_age"] >= charter["stale_cutoff"]:
        risk += charter["stale_penalty"]
    if case["weekend"]:
        fee += charter["weekend_penalty"]

    rz, rc, rv = amendments["risk_replace_pair"]
    if case["zone"] == rz and case["category"] == rc:
        risk = int(rv)

    fz, fc, fv = amendments["fee_replace_pair"]
    if case["zone"] == fz and case["category"] == fc:
        fee = int(fv)

    pz, prisk, pfee = amendments["preclear_replace"]
    if case["zone"] == pz and case["preclear"]:
        risk = min(risk, int(prisk))
        fee += int(pfee)

    seal, discount, guard_flag, mode = amendments["seal_rule"]
    if case["seal"] == seal:
        if (mode == "absent" and guard_flag not in case["flags"]) or (mode == "present" and guard_flag in case["flags"]):
            fee -= int(discount)

    az, ac, av = amendments["zone_category_fee_add"]
    if case["zone"] == az and case["category"] == ac:
        fee += int(av)

    qcut, qadd = amendments["quantity_risk_add"]
    if case["quantity"] >= int(qcut):
        risk += int(qadd)

    waiver_values = []
    ecut, eval_ = amendments["escort_waiver"]
    if case["quantity"] <= int(ecut) and case["escort"]:
        waiver_values.append(int(eval_))
    if case["declared_units"] != case["quantity"] and case["preclear"]:
        waiver_values.append(int(amendments["mismatch_waiver"]))
    if waiver_values:
        fee -= max(waiver_values)

    band, floor_review = amendments["manual_review"]
    if case["manual_note"] and fee >= int(band):
        risk = max(risk, int(floor_review))

    fee = max(fee, 0)
    if risk <= charter["allow_max"]:
        verdict = "ALLOW"
    elif risk <= charter["review_max"]:
        verdict = "REVIEW"
    else:
        verdict = "DENY"

    if fee <= charter["green_max"]:
        lane = "GREEN"
    elif fee <= charter["amber_max"]:
        lane = "AMBER"
    else:
        lane = "RED"
    return f"verdict={verdict};lane={lane};fee={fee}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    bundle_root = args.items.parent
    rows = [json.loads(line) for line in args.items.read_text(encoding="utf-8").splitlines() if line.strip()]
    with args.out.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps({"id": row["id"], "answer": solve_one(bundle_root, row)}, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
