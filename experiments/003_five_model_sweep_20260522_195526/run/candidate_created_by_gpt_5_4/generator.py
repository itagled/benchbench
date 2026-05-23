#!/usr/bin/env python3
import argparse
import hashlib
import json
import random
import shutil
from pathlib import Path


BENCHMARK_ID = "patchwork_ordinance_adjudication_v1"
SHARED_RULEBOOK = """# Patchwork Ordinance Adjudication (POA) v1

You are adjudicating one filing under a fictional municipal ordinance.

Each item contains:
- `charter.md`: the base ordinance.
- `amendments.md`: later amendments, clarifications, and exception rules.
- `case_file.json`: the filing to adjudicate.

Your task is to compute the final answer string in this exact format:

`verdict=<ALLOW|REVIEW|DENY>;lane=<GREEN|AMBER|RED>;fee=<integer>`

Interpretation rules:
1. Start from the base values in `charter.md`.
2. Apply later rules from `amendments.md` according to their stated priority.
3. If multiple rules could change the fee, apply them in this order:
   - replace fee if a replacement rule applies,
   - then add all additive adjustments that apply,
   - then apply the one capped waiver with the largest absolute reduction,
   - then floor the fee at 0.
4. `verdict` is determined from the final risk score:
   - score <= allow_max -> `ALLOW`
   - allow_max < score <= review_max -> `REVIEW`
   - score > review_max -> `DENY`
5. `lane` is determined from the final fee:
   - fee <= green_max -> `GREEN`
   - green_max < fee <= amber_max -> `AMBER`
   - fee > amber_max -> `RED`
6. Every condition in the documents is literal. There are no hidden norms.
7. When an amendment says it overrides an earlier rule, it wins for its scope only.
8. All category names, zones, and seals are case-sensitive exact strings.
"""


ZONES = ["North", "South", "East", "West"]
CATEGORIES = ["Transit", "Medical", "Research", "Agriculture", "Archives"]
TIERS = ["T1", "T2", "T3"]
SEALS = ["Aster", "Birch", "Cinder", "Dawn", "Ember"]
FLAGS = ["field", "dock", "vault", "relay"]


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def canonical_answer(verdict: str, lane: str, fee: int) -> str:
    return f"verdict={verdict};lane={lane};fee={fee}"


def choose_distinct(rng: random.Random, values, count: int):
    return rng.sample(list(values), count)


def build_item(index: int, seed: int):
    rng = random.Random(seed + index * 7919)
    zone_order = choose_distinct(rng, ZONES, 4)
    category_order = choose_distinct(rng, CATEGORIES, 5)
    seal_order = choose_distinct(rng, SEALS, 5)
    flag_order = choose_distinct(rng, FLAGS, 4)

    allow_max = rng.randint(3, 5)
    review_max = allow_max + rng.randint(2, 4)
    green_max = rng.randint(10, 17)
    amber_max = green_max + rng.randint(8, 14)

    zone_base = {zone: rng.randint(3, 9) for zone in zone_order}
    tier_add = {"T1": rng.randint(0, 2), "T2": rng.randint(2, 4), "T3": rng.randint(4, 6)}
    category_add = {cat: rng.randint(0, 3) for cat in category_order}
    flag_penalty = {flag: rng.randint(1, 4) for flag in flag_order}

    target_zone = rng.choice(zone_order)
    target_category = rng.choice(category_order)
    target_tier = rng.choice(TIERS)
    target_seal = rng.choice(seal_order)
    flag_count = rng.randint(1, 3)
    target_flags = sorted(choose_distinct(rng, flag_order, flag_count))
    quantity = rng.randint(1, 9)
    declared_units = rng.randint(1, 9)
    while declared_units == quantity:
        declared_units = rng.randint(1, 9)
    record_age = rng.randint(1, 9)
    weekend = rng.choice([True, False])
    escort = rng.choice([True, False])
    preclear = rng.choice([True, False])
    manual_note = rng.choice([True, False])

    fee_base = rng.randint(8, 18)
    quantity_multiplier = rng.randint(2, 5)
    mismatch_penalty = rng.randint(2, 7)
    stale_cutoff = rng.randint(5, 7)
    stale_penalty = rng.randint(2, 5)
    weekend_penalty = rng.randint(1, 4)

    pair_override_score = rng.randint(0, 3)
    pair_override_fee_replace = rng.randint(5, 14)
    seal_discount = rng.randint(2, 6)
    seal_guard_flag = rng.choice([f for f in flag_order if f not in target_flags] + target_flags)
    seal_guard_requires_absent = seal_guard_flag in target_flags
    category_zone_add = rng.randint(1, 5)
    high_quantity_cutoff = max(quantity - 1, 1)
    high_quantity_add = rng.randint(2, 6)
    low_quantity_cutoff = min(quantity + 1, 9)
    low_quantity_discount = rng.randint(1, 4)
    mismatch_waiver = rng.randint(2, 5)
    preclear_replace_score = rng.randint(1, 4)
    preclear_fee_add = rng.randint(1, 3)
    manual_review_band = rng.randint(amber_max + 1, amber_max + 7)

    risk_score = zone_base[target_zone] + tier_add[target_tier] + category_add[target_category]
    fee = fee_base + quantity * quantity_multiplier

    risk_score += sum(flag_penalty[f] for f in target_flags)
    if declared_units != quantity:
        risk_score += mismatch_penalty
    if record_age >= stale_cutoff:
        risk_score += stale_penalty
    if weekend:
        fee += weekend_penalty

    if target_zone == zone_order[0] and target_category == category_order[0]:
        risk_score = pair_override_score
    if target_zone == zone_order[1] and target_category == category_order[2]:
        fee = pair_override_fee_replace
    if target_zone == zone_order[3] and preclear:
        risk_score = min(risk_score, preclear_replace_score)
        fee += preclear_fee_add
    if target_seal == seal_order[0]:
        if seal_guard_requires_absent:
            if seal_guard_flag not in target_flags:
                fee -= seal_discount
        else:
            if seal_guard_flag in target_flags:
                fee -= seal_discount
    if target_zone == zone_order[2] and target_category == category_order[1]:
        fee += category_zone_add
    if quantity >= high_quantity_cutoff:
        risk_score += high_quantity_add
    waiver_candidates = []
    if quantity <= low_quantity_cutoff and escort:
        waiver_candidates.append(low_quantity_discount)
    if declared_units != quantity and preclear:
        waiver_candidates.append(mismatch_waiver)
    if waiver_candidates:
        fee -= max(waiver_candidates)
    if manual_note and fee >= manual_review_band:
        risk_score = max(risk_score, review_max)

    fee = max(fee, 0)
    if risk_score <= allow_max:
        verdict = "ALLOW"
    elif risk_score <= review_max:
        verdict = "REVIEW"
    else:
        verdict = "DENY"

    if fee <= green_max:
        lane = "GREEN"
    elif fee <= amber_max:
        lane = "AMBER"
    else:
        lane = "RED"

    item_id = f"poa_{index:03d}"
    answer = canonical_answer(verdict, lane, fee)

    charter = f"""# Charter

Decision thresholds:
- `ALLOW` if final risk score <= {allow_max}
- `REVIEW` if final risk score <= {review_max} and greater than {allow_max}
- `DENY` if final risk score > {review_max}

Lane thresholds:
- `GREEN` if final fee <= {green_max}
- `AMBER` if final fee <= {amber_max} and greater than {green_max}
- `RED` if final fee > {amber_max}

Base risk score components:
- zone `{zone_order[0]}`: {zone_base[zone_order[0]]}
- zone `{zone_order[1]}`: {zone_base[zone_order[1]]}
- zone `{zone_order[2]}`: {zone_base[zone_order[2]]}
- zone `{zone_order[3]}`: {zone_base[zone_order[3]]}
- tier `T1`: {tier_add['T1']}
- tier `T2`: {tier_add['T2']}
- tier `T3`: {tier_add['T3']}
- category `{category_order[0]}`: {category_add[category_order[0]]}
- category `{category_order[1]}`: {category_add[category_order[1]]}
- category `{category_order[2]}`: {category_add[category_order[2]]}
- category `{category_order[3]}`: {category_add[category_order[3]]}
- category `{category_order[4]}`: {category_add[category_order[4]]}

Base fee:
- start with {fee_base}
- add `quantity * {quantity_multiplier}`

Standing operational penalties:
- add risk `{flag_penalty[flag_order[0]]}` if flag `{flag_order[0]}` is present
- add risk `{flag_penalty[flag_order[1]]}` if flag `{flag_order[1]}` is present
- add risk `{flag_penalty[flag_order[2]]}` if flag `{flag_order[2]}` is present
- add risk `{flag_penalty[flag_order[3]]}` if flag `{flag_order[3]}` is present
- if `declared_units != quantity`, add risk `{mismatch_penalty}`
- if `record_age >= {stale_cutoff}`, add risk `{stale_penalty}`
- if `weekend = true`, add fee `{weekend_penalty}`
"""

    guard_text = (
        f"if flag `{seal_guard_flag}` is absent"
        if seal_guard_requires_absent
        else f"if flag `{seal_guard_flag}` is present"
    )
    amendments = f"""# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `{zone_order[0]}` and category is `{category_order[0]}`, replace the entire risk score with `{pair_override_score}`.
- If zone is `{zone_order[1]}` and category is `{category_order[2]}`, replace the running fee with `{pair_override_fee_replace}`.
- If zone is `{zone_order[3]}` and `preclear = true`, replace the risk score with the smaller of its current value and `{preclear_replace_score}`; then add fee `{preclear_fee_add}`.

Additive rules:
- If seal is `{seal_order[0]}`, subtract fee `{seal_discount}` {guard_text}.
- If zone is `{zone_order[2]}` and category is `{category_order[1]}`, add fee `{category_zone_add}`.
- If `quantity >= {high_quantity_cutoff}`, add risk `{high_quantity_add}`.

Waivers:
- If `quantity <= {low_quantity_cutoff}` and `escort = true`, subtract fee `{low_quantity_discount}`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `{mismatch_waiver}`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `{manual_review_band}`, force the final risk score to be at least `{review_max}`.
"""

    case = {
        "id": item_id,
        "zone": target_zone,
        "category": target_category,
        "tier": target_tier,
        "seal": target_seal,
        "quantity": quantity,
        "declared_units": declared_units,
        "record_age": record_age,
        "weekend": weekend,
        "escort": escort,
        "preclear": preclear,
        "manual_note": manual_note,
        "flags": target_flags,
    }
    return {
        "id": item_id,
        "answer": answer,
        "charter": charter,
        "amendments": amendments,
        "case": case,
    }


def generate_dataset(sample_count: int, seed: int, out_dir: Path) -> None:
    solver_bundle = out_dir / "solver_bundle"
    if solver_bundle.exists():
        shutil.rmtree(solver_bundle)
    solver_bundle.mkdir(parents=True, exist_ok=True)
    assets_dir = solver_bundle / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    write_text(solver_bundle / "README.md", SOLVER_README)
    write_text(solver_bundle / "shared_rules.md", SHARED_RULEBOOK)

    gold_rows = []
    item_rows = []
    manifest_items = []

    for index in range(sample_count):
        item = build_item(index, seed)
        item_asset_dir = assets_dir / item["id"]
        item_asset_dir.mkdir(parents=True, exist_ok=True)
        charter_rel = f"assets/{item['id']}/charter.md"
        amendments_rel = f"assets/{item['id']}/amendments.md"
        case_rel = f"assets/{item['id']}/case_file.json"
        write_text(solver_bundle / charter_rel, item["charter"])
        write_text(solver_bundle / amendments_rel, item["amendments"])
        write_json(solver_bundle / case_rel, item["case"])

        item_row = {
            "id": item["id"],
            "shared_rules": "shared_rules.md",
            "charter": charter_rel,
            "amendments": amendments_rel,
            "case_file": case_rel,
        }
        item_rows.append(item_row)
        gold_rows.append({"id": item["id"], "answer": item["answer"]})
        manifest_items.append(
            {
                "id": item["id"],
                "files": {
                    "charter": {"path": charter_rel, "sha256": stable_hash(item["charter"])},
                    "amendments": {"path": amendments_rel, "sha256": stable_hash(item["amendments"])},
                    "case_file": {
                        "path": case_rel,
                        "sha256": stable_hash(json.dumps(item["case"], sort_keys=True)),
                    },
                },
            }
        )

    with (out_dir / "gold_private_sample.jsonl").open("w", encoding="utf-8") as handle:
        for row in gold_rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    with (solver_bundle / "items_private_sample.jsonl").open("w", encoding="utf-8") as handle:
        for row in item_rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    write_json(
        solver_bundle / "SOLVER_MANIFEST.json",
        {
            "benchmark_id": BENCHMARK_ID,
            "item_count": sample_count,
            "answer_format": "verdict=<ALLOW|REVIEW|DENY>;lane=<GREEN|AMBER|RED>;fee=<integer>",
            "public_files": ["shared_rules.md", "items_private_sample.jsonl", "README.md"],
            "items": manifest_items,
        },
    )


SOLVER_README = """# Solver Bundle for Patchwork Ordinance Adjudication (POA) v1

Each item is a fictional compliance packet. The answer for every item must be a single string:

`verdict=<ALLOW|REVIEW|DENY>;lane=<GREEN|AMBER|RED>;fee=<integer>`

Use:
- `shared_rules.md` for global interpretation rules,
- the per-item `charter.md`,
- the per-item `amendments.md`,
- and the per-item `case_file.json`.

The authoritative item index is `items_private_sample.jsonl`. All asset paths inside it are relative to this solver bundle.

Nothing outside this directory is needed to solve the benchmark in principle.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-count", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    generate_dataset(args.sample_count, args.seed, args.out_dir.resolve())


if __name__ == "__main__":
    main()
