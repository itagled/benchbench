import os
import json
import random
import argparse
from typing import Dict, List, Tuple, Any, Optional

def parse_args():
    parser = argparse.ArgumentParser(description="Generate MFN-Cascade benchmark items.")
    parser.add_argument("--sample-count", type=int, default=30, help="Number of items to generate")
    parser.add_argument("--seed", type=int, default=20260516, help="Random seed for generation")
    parser.add_argument("--out-dir", type=str, default=".", help="Output directory")
    return parser.parse_args()

# Constants
NATIONS = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]

GOODS_HIERARCHY = {
    "Electronics": ["ConsumerElectronics", "IndustrialSemiconductors"],
    "Agriculture": ["GrainsAndCereals", "FreshProduce"],
    "Textiles": ["FinishedApparel", "RawFabrics"],
    "Machinery": ["HeavyEquipment", "PrecisionTools"],
    "Chemicals": ["OrganicSolvents", "SyntheticPolymers"]
}

ALL_GOODS = []
for parent, children in GOODS_HIERARCHY.items():
    ALL_GOODS.append(parent)
    ALL_GOODS.extend(children)

def get_parent(good: str) -> Optional[str]:
    for parent, children in GOODS_HIERARCHY.items():
        if good in children:
            return parent
    return None

class MFNClause:
    def __init__(self, importer: str, exporter: str, good: str, third_party: str,
                 rule_type: str, value: float, floor: float, article_num: int):
        self.importer = importer
        self.exporter = exporter
        self.good = good
        self.third_party = third_party  # "any" or a specific nation
        self.rule_type = rule_type      # "margin" (adds margin to target) or "multiplier" (multiplies target)
        self.value = value              # margin value (e.g. 0.5) or multiplier (e.g. 1.1)
        self.floor = floor              # floor rate (e.g. 1.0)
        self.article_num = article_num

    def to_text(self) -> str:
        party_str = f"any third nation" if self.third_party == "any" else f"Nation {self.third_party}"
        if self.rule_type == "margin":
            formula_str = f"to match that rate, plus a margin of {self.value:.1f}%" if self.value > 0 else f"to match that rate directly" if self.value == 0 else f"to match that rate minus a discount of {abs(self.value):.1f}%"
        else:
            formula_str = f"to match that rate multiplied by a factor of {self.value:.2f}"

        floor_str = f", subject to a minimum floor of {self.floor:.1f}%" if self.floor > 0 else ""
        return f"Article {self.article_num} (MFN): If Nation {self.importer} grants a tariff rate on {self.good} imported from {party_str} that is lower than the tariff rate applied on imports from Nation {self.exporter}, then the tariff rate applied on imports from Nation {self.exporter} for {self.good} shall be reduced {formula_str}{floor_str}."

class Treaty:
    def __init__(self, nation_a: str, nation_b: str, base_tariffs: Dict[Tuple[str, str, str], float], mfn_clauses: List[MFNClause]):
        self.nation_a = nation_a
        self.nation_b = nation_b
        self.base_tariffs = base_tariffs # Key: (importer, exporter, good) -> float
        self.mfn_clauses = mfn_clauses

    def to_text(self) -> str:
        lines = []
        lines.append(f"==============================================================")
        lines.append(f"BILATERAL TRADE AND TARIFF AGREEMENT BETWEEN {self.nation_a.upper()} AND {self.nation_b.upper()}")
        lines.append(f"==============================================================")
        lines.append(f"Signed: 2020-01-01 | Effective: 2020-03-01")
        lines.append("")
        lines.append("PREAMBLE:")
        lines.append(f"The Sovereign Governments of Nation {self.nation_a} and Nation {self.nation_b}, seeking to maximize trade efficiency and maintain fair competitive grounds, hereby agree to the following tariff schedules and trade rules.")
        lines.append("")
        lines.append("SECTION 1: BASE TARIFF RATES")

        article_counter = 1
        for (imp, exp, gd), rate in sorted(self.base_tariffs.items()):
            lines.append(f"Article {article_counter}: Nation {imp} shall apply a base tariff rate of {rate:.1f}% on the import of {gd} from Nation {exp}.")
            article_counter += 1

        lines.append("")
        lines.append("SECTION 2: MOST FAVORED NATION CLAUSES")
        for mfn in self.mfn_clauses:
            mfn.article_num = article_counter
            lines.append(mfn.to_text())
            article_counter += 1

        lines.append("")
        lines.append("--------------------------------------------------------------")
        return "\n".join(lines)

class Amendment:
    def __init__(self, amend_id: int, date: str, description: str,
                 modifications: List[Dict[str, Any]]):
        self.amend_id = amend_id
        self.date = date
        self.description = description
        self.modifications = modifications # List of changes: e.g. base tariff updates or MFN modifications

    def to_text(self) -> str:
        lines = []
        lines.append(f"==============================================================")
        lines.append(f"MULTILATERAL TARIFF AMENDMENT AND OVERRIDE ACT (ACT-{self.date.replace('-', '')})")
        lines.append(f"==============================================================")
        lines.append(f"Ratification Date: {self.date} | Effective Date: {self.date}")
        lines.append("")
        lines.append("Be it resolved by the signatory nations that the following modifications and overrides to existing bilateral agreements are officially codified and active as of the effective date.")
        lines.append("")
        for idx, mod in enumerate(self.modifications, 1):
            if mod["type"] == "base_tariff":
                lines.append(f"Amendment Clause {idx}: The base tariff rate applied by Nation {mod['importer']} on {mod['good']} from Nation {mod['exporter']} is hereby modified to {mod['rate']:.1f}%, overriding all previous article clauses.")
            elif mod["type"] == "mfn_modify":
                lines.append(f"Amendment Clause {idx}: Article {mod['article_num']} of the Treaty between Nation {mod['nation_a']} and Nation {mod['nation_b']} is modified. The MFN floor is adjusted to {mod['new_floor']:.1f}% and the margin is set to {mod['new_value']:.1f}%.")
        lines.append("")
        lines.append("--------------------------------------------------------------")
        return "\n".join(lines)

# Core Simulator
class TariffSimulator:
    def __init__(self, base_tariffs: Dict[Tuple[str, str, str], float], mfn_clauses: List[MFNClause], amendments: List[Amendment]):
        self.initial_base_tariffs = base_tariffs.copy()
        self.mfn_clauses = mfn_clauses
        self.amendments = amendments

    def get_tariffs_at_date(self, query_date: str) -> Dict[Tuple[str, str, str], float]:
        # Start with base tariffs
        tariffs = self.initial_base_tariffs.copy()

        # Sort amendments by date
        sorted_amends = sorted(self.amendments, key=lambda x: x.date)

        # Apply amendments that are effective on or before the query_date
        active_mfn_modifications = {} # (importer, exporter, good, article_num) -> (new_floor, new_value)

        for amend in sorted_amends:
            if amend.date <= query_date:
                for mod in amend.modifications:
                    if mod["type"] == "base_tariff":
                        tariffs[(mod["importer"], mod["exporter"], mod["good"])] = mod["rate"]
                    elif mod["type"] == "mfn_modify":
                        key = (mod["nation_a"], mod["nation_b"], mod["good"], mod["article_num"])
                        active_mfn_modifications[key] = (mod["new_floor"], mod["new_value"])

        # Also prepare the MFN clauses with active modifications applied
        current_mfn_clauses = []
        for mfn in self.mfn_clauses:
            # Check if this clause was modified
            # Find the treaty parties
            nat_a, nat_b = mfn.importer, mfn.exporter
            mod_key = (nat_a, nat_b, mfn.good, mfn.article_num)
            if mod_key in active_mfn_modifications:
                new_floor, new_value = active_mfn_modifications[mod_key]
                # Create a modified clone
                cloned_mfn = MFNClause(mfn.importer, mfn.exporter, mfn.good, mfn.third_party,
                                       mfn.rule_type, new_value, new_floor, mfn.article_num)
                current_mfn_clauses.append(cloned_mfn)
            else:
                current_mfn_clauses.append(mfn)

        return tariffs, current_mfn_clauses

    def simulate(self, query_date: str, event: Dict[str, Any]) -> Dict[Tuple[str, str, str], float]:
        # Get active tariffs and MFNs
        tariffs, mfns = self.get_tariffs_at_date(query_date)

        # Apply the initial event modification
        tariffs[(event["importer"], event["exporter"], event["good"])] = event["rate"]

        # Run rounds of propagation
        # We run up to 20 rounds. If not converged, lock values.
        converged = False
        prev_tariffs = tariffs.copy()

        for r in range(1, 21):
            new_tariffs = prev_tariffs.copy()

            # Step A: Apply MFN updates
            for mfn in mfns:
                imp = mfn.importer
                exp = mfn.exporter
                good = mfn.good

                # Check third-party rates
                third_parties = [n for n in NATIONS if n != imp and n != exp]
                if mfn.third_party != "any":
                    third_parties = [mfn.third_party]

                for tp in third_parties:
                    tp_rate = prev_tariffs.get((imp, tp, good))
                    if tp_rate is not None:
                        current_rate = prev_tariffs.get((imp, exp, good), 100.0)

                        # Trigger condition
                        if tp_rate < current_rate:
                            # Apply formula
                            if mfn.rule_type == "margin":
                                calculated = tp_rate + mfn.value
                            elif mfn.rule_type == "multiplier":
                                calculated = tp_rate * mfn.value
                            else:
                                calculated = tp_rate

                            calculated = max(mfn.floor, calculated)
                            if calculated < current_rate:
                                # We only reduce tariffs
                                new_tariffs[(imp, exp, good)] = calculated

            # Step B: Apply hierarchical propagation
            # Parent -> Child propagation
            for parent, children in GOODS_HIERARCHY.items():
                for imp in NATIONS:
                    for exp in NATIONS:
                        if imp == exp:
                            continue
                        p_rate = new_tariffs.get((imp, exp, parent))
                        if p_rate is not None:
                            for child in children:
                                c_rate = new_tariffs.get((imp, exp, child))
                                if c_rate is not None and p_rate < c_rate:
                                    new_tariffs[(imp, exp, child)] = p_rate

            # Check convergence (max change < 0.01%)
            max_diff = 0.0
            for key in new_tariffs:
                old_val = prev_tariffs.get(key, 0.0)
                new_val = new_tariffs[key]
                diff = abs(old_val - new_val)
                if diff > max_diff:
                    max_diff = diff

            if max_diff < 0.01:
                converged = True
                prev_tariffs = new_tariffs
                break

            prev_tariffs = new_tariffs

        # Stalemate Locking Rule if not converged by round 20
        # Round rates to 1 decimal place
        final_tariffs = {}
        for key, val in prev_tariffs.items():
            final_tariffs[key] = round(val, 1)

        return final_tariffs, converged

def generate_benchmark_data(seed: int, sample_count: int) -> Tuple[List[Treaty], List[Amendment], List[Dict[str, Any]]]:
    random.seed(seed)

    # 1. Generate base tariffs for all bilateral pairs
    # Keep it simple: 5 treaties representing the circle (Alpha-Beta, Beta-Gamma, Gamma-Delta, Delta-Epsilon, Epsilon-Alpha)
    pairs = [
        ("Alpha", "Beta"),
        ("Beta", "Gamma"),
        ("Gamma", "Delta"),
        ("Delta", "Epsilon"),
        ("Epsilon", "Alpha")
    ]

    base_tariffs = {}
    mfn_clauses = []
    treaties = []

    # For each pair, create a bilateral treaty
    for p_idx, (nat_a, nat_b) in enumerate(pairs):
        p_base_tariffs = {}
        p_mfn_clauses = []

        # Base tariffs for all goods categories
        for good in ALL_GOODS:
            # Tariff from A to B and B to A
            # Base rates range from 4.0% to 12.0%
            p_base_tariffs[(nat_a, nat_b, good)] = round(random.uniform(5.0, 10.0), 1)
            p_base_tariffs[(nat_b, nat_a, good)] = round(random.uniform(5.0, 10.0), 1)

        # Add 2 MFN clauses per treaty
        # MFN clause 1: Nation A's imports from B
        # Choose a random good
        good_mfn1 = random.choice(ALL_GOODS)
        # Type of rule: margin or multiplier
        rule_type = random.choice(["margin", "multiplier"])
        if rule_type == "margin":
            val = round(random.choice([0.0, 0.2, 0.5, 0.8]), 1)
        else:
            val = round(random.choice([1.0, 1.05, 1.1]), 2)
        floor = round(random.uniform(1.0, 3.0), 1)

        # MFN importer: nat_a, exporter: nat_b
        mfn1 = MFNClause(importer=nat_a, exporter=nat_b, good=good_mfn1, third_party="any",
                          rule_type=rule_type, value=val, floor=floor, article_num=0)
        p_mfn_clauses.append(mfn1)
        mfn_clauses.append(mfn1)

        # MFN clause 2: Nation B's imports from A
        good_mfn2 = random.choice(ALL_GOODS)
        rule_type2 = random.choice(["margin", "multiplier"])
        if rule_type2 == "margin":
            val2 = round(random.choice([0.0, 0.2, 0.5, 0.8]), 1)
        else:
            val2 = round(random.choice([1.0, 1.05, 1.1]), 2)
        floor2 = round(random.uniform(1.0, 3.0), 1)

        mfn2 = MFNClause(importer=nat_b, exporter=nat_a, good=good_mfn2, third_party="any",
                          rule_type=rule_type2, value=val2, floor=floor2, article_num=0)
        p_mfn_clauses.append(mfn2)
        mfn_clauses.append(mfn2)

        # Build the base tariff dictionary
        bt_dict = {}
        for (imp, exp, gd) in p_base_tariffs:
            bt_dict[(imp, exp, gd)] = p_base_tariffs[(imp, exp, gd)]
            base_tariffs[(imp, exp, gd)] = p_base_tariffs[(imp, exp, gd)]

        treaty = Treaty(nat_a, nat_b, bt_dict, p_mfn_clauses)
        treaties.append(treaty)

    # Populate actual article numbers for MFN clauses now that we have base tariff counts
    for t in treaties:
        base_count = len(t.base_tariffs)
        for idx, mfn in enumerate(t.mfn_clauses, 1):
            mfn.article_num = base_count + idx

    # 2. Generate Amendments
    # We will generate 3 amendments at different historical dates
    amendments = []
    amend_dates = ["2022-04-15", "2024-09-01", "2025-06-20"]
    for i, date in enumerate(amend_dates, 1):
        modifications = []
        # Each amendment modifies 2 base tariffs and 1 MFN clause
        for _ in range(2):
            imp = random.choice(NATIONS)
            exp = random.choice([n for n in NATIONS if n != imp])
            good = random.choice(ALL_GOODS)
            rate = round(random.uniform(3.0, 6.0), 1)
            modifications.append({
                "type": "base_tariff",
                "importer": imp,
                "exporter": exp,
                "good": good,
                "rate": rate
            })

        # Modify a random MFN clause
        chosen_mfn = random.choice(mfn_clauses)
        new_floor = round(random.uniform(0.5, 2.0), 1)
        new_val = round(random.choice([0.0, 0.1, 0.3]), 1) if chosen_mfn.rule_type == "margin" else round(random.choice([1.0, 1.02]), 2)

        # Find which treaty this MFN belongs to
        treaty_found = None
        for t in treaties:
            if chosen_mfn in t.mfn_clauses:
                treaty_found = t
                break

        if treaty_found:
            modifications.append({
                "type": "mfn_modify",
                "nation_a": treaty_found.nation_a,
                "nation_b": treaty_found.nation_b,
                "good": chosen_mfn.good,
                "article_num": chosen_mfn.article_num,
                "new_floor": new_floor,
                "new_value": new_val
            })

        amend = Amendment(amend_id=i, date=date, description=f"Amendment Act {i}", modifications=modifications)
        amendments.append(amend)

    # 3. Create simulator
    simulator = TariffSimulator(base_tariffs, mfn_clauses, amendments)

    # 4. Generate Queries
    queries = []
    # To make queries challenging and unique, let's create a pool of query parameters
    query_id = 1
    attempts = 0

    while len(queries) < sample_count and attempts < 1000:
        attempts += 1
        # Random date
        year = random.choice([2021, 2023, 2026])
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        date_str = f"{year}:{month:02d}:{day:02d}".replace(":", "-")

        # Unilateral concession event
        event_imp = random.choice(NATIONS)
        event_exp = random.choice([n for n in NATIONS if n != event_imp])
        event_good = random.choice(ALL_GOODS)
        # A low rate (e.g. 1.0% to 3.0%)
        event_rate = round(random.uniform(1.0, 3.0), 1)

        event = {
            "importer": event_imp,
            "exporter": event_exp,
            "good": event_good,
            "rate": event_rate
        }

        # Output query target
        target_imp = random.choice(NATIONS)
        target_exp = random.choice([n for n in NATIONS if n != target_imp])
        target_good = random.choice(ALL_GOODS)

        # Make sure target is not the same as the event
        if target_imp == event_imp and target_exp == event_exp and target_good == event_good:
            continue

        # Run simulation to check if the cascade actually reaches the target rate (i.e. has high reasoning depth)
        # Compute baseline initial tariff at that date
        tariffs_init, _ = simulator.get_tariffs_at_date(date_str)
        init_val = tariffs_init.get((target_imp, target_exp, target_good))

        if init_val is None:
            # No base tariff exists for this pair/good directly, which means they use fallback or default (we skip this for simplicity)
            continue

        final_tariffs, converged = simulator.simulate(date_str, event)
        final_val = final_tariffs.get((target_imp, target_exp, target_good))

        if final_val is None:
            continue

        # We prefer items where the tariff actually *changed* or where the cascade is complex (converged or stalemate)
        # This filters out trivial items
        if final_val == init_val and random.random() > 0.15:
            # Allow some non-changing queries as negative controls, but keep most changing
            continue

        # Formulate description
        query_desc = (
            f"On {date_str}, Nation {event_imp} unilaterally reduces its tariff rate on imports of "
            f"{event_good} from Nation {event_exp} to {event_rate:.1f}% as a special trade concession.\n"
            f"Assuming all other tariff rates start at their active base levels for {date_str} as codified in the "
            f"Trade Agreements, and applying all active MFN clauses, hierarchical category propagation rules, "
            f"amendments, and stalemate locking protocols:\n"
            f"Calculate the final stable tariff rate applied by Nation {target_imp} on imports of "
            f"{target_good} from Nation {target_exp}."
        )

        # Storing query data
        queries.append({
            "id": f"mfn_cascade_{query_id:03d}",
            "date": date_str,
            "event": event,
            "target": {
                "importer": target_imp,
                "exporter": target_exp,
                "good": target_good
            },
            "prompt": query_desc,
            "answer": f"{final_val:.1f}%" if converged else f"STALEMATE_{final_val:.1f}%"
        })
        query_id += 1

    return treaties, amendments, queries

def write_common_framework(out_path: str):
    framework = """==============================================================
COMMON MULTI-LATERAL TARIFF AND TRADE SETTLEMENT FRAMEWORK
==============================================================
Active: 2020-01-01 | Re-codified: 2025-01-01

This document outlines the standard operational framework governing all bilateral and multilateral tariff schedules, MFN updates, category hierarchies, and operational protocols. All signatory nations must adhere strictly to these execution steps.

SECTION 1: GOODS CATEGORIES AND HIERARCHY
The system utilizes a 2-tier hierarchical goods classification. Tariff adjustments applied to parent categories automatically propagate downwards to sub-categories if the parent rate becomes lower than the sub-category rate.

Hierarchy Definition:
- Electronics (Parent)
  ├─ ConsumerElectronics (Child)
  └─ IndustrialSemiconductors (Child)
- Agriculture (Parent)
  ├─ GrainsAndCereals (Child)
  └─ FreshProduce (Child)
- Textiles (Parent)
  ├─ FinishedApparel (Child)
  └─ RawFabrics (Child)
- Machinery (Parent)
  ├─ HeavyEquipment (Child)
  └─ PrecisionTools (Child)
- Chemicals (Parent)
  ├─ OrganicSolvents (Child)
  └─ SyntheticPolymers (Child)

Rule (Parent-Child Propagation):
For any bilateral pair (Importer, Exporter), if the tariff rate on a parent category is lower than the tariff rate on a sub-category, the sub-category tariff rate is instantly reduced to match the parent category rate:
Tariff(Child) = min(Tariff(Child), Tariff(Parent))

SECTION 2: MOST FAVORED NATION (MFN) CLAUSE EXECUTION
1. An MFN clause triggers whenever the Importer applies a tariff rate to imports from a third-party nation that is strictly lower than the tariff rate currently applied to the Exporter for the same category.
2. When triggered, the tariff applied to the Exporter is reduced according to the specific formula stated in the bilateral treaty:
   - "match that rate, plus a margin of M%": New Tariff = min(Current, max(Floor, Third-Party Rate + M%))
   - "match that rate, multiplied by a factor of C": New Tariff = min(Current, max(Floor, Third-Party Rate * C))
3. Tariff rates can never be increased via MFN clauses. They are strictly downward-reducing.

SECTION 3: DISCRETE ROUND SIMULATION AND STALEMATE PROTOCOLS
To determine the final, stable tariff rates following a trade adjustment:
1. Initialize all tariff rates to their active base levels on the query date (after applying all active historical amendments).
2. Apply the initiating unilateral trade event to the tariff schedule.
3. Perform discrete rounds of updates. In each round:
   - Step A: Evaluate and apply all MFN clauses based on the tariff rates from the PREVIOUS round.
   - Step B: Apply hierarchical parent-to-child propagation to the updated rates.
4. Convergence: If, after any round, the maximum change across all tariff rates in the system is less than 0.01%, the system is declared STABLE.
5. Stalemate Lock: If the system does not reach stability after exactly 20 rounds of updates, the system is declared to be in a circular stalemate. All rates are locked to their values at the end of round 20, rounded to the nearest 0.1%.
   - In this case, the final answer must be formatted as: STALEMATE_X.Y% (where X.Y is the locked rate).
   - If the system did reach stability, the answer must be formatted as: X.Y%
"""
    with open(out_path, "w") as f:
        f.write(framework)

def main():
    args = parse_args()

    # Create directories
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    solver_bundle_dir = os.path.join(out_dir, "solver_bundle")
    treaties_dir = os.path.join(solver_bundle_dir, "treaties")
    os.makedirs(treaties_dir, exist_ok=True)

    # Generate data
    treaties, amendments, queries = generate_benchmark_data(args.seed, args.sample_count)

    # Write treaties
    write_common_framework(os.path.join(treaties_dir, "common_framework.txt"))
    for idx, t in enumerate(treaties, 1):
        filename = f"treaty_{t.nation_a.lower()}_{t.nation_b.lower()}.txt"
        with open(os.path.join(treaties_dir, filename), "w") as f:
            f.write(t.to_text())

    # Write amendments as standalone files
    for a in amendments:
        filename = f"amendment_{a.date.replace('-', '_')}.txt"
        with open(os.path.join(treaties_dir, filename), "w") as f:
            f.write(a.to_text())

    # Write solver_bundle/items_private_sample.jsonl (No answers!)
    items_path = os.path.join(solver_bundle_dir, "items_private_sample.jsonl")
    with open(items_path, "w") as f:
        for q in queries:
            item = {
                "id": q["id"],
                "date": q["date"],
                "prompt": q["prompt"]
            }
            f.write(json.dumps(item) + "\n")

    # Write gold_private_sample.jsonl
    gold_path = os.path.join(out_dir, "gold_private_sample.jsonl")
    with open(gold_path, "w") as f:
        for q in queries:
            gold_row = {
                "id": q["id"],
                "answer": q["answer"]
            }
            f.write(json.dumps(gold_row) + "\n")

    # Write solver_bundle/README.md
    readme_solver = """# MFN-Cascade Benchmark Solver Packet

Welcome to the **MFN-Cascade** (Recursive Treaty Tariff Adjudication) solver bundle.

In this challenge, you are asked to resolve the final stable tariff rates under recursive multi-lateral trade agreements following a unilateral tariff adjustment.

## Rules & Framework

1. The general rules for MFN clauses, category hierarchies, and stalemate locking are defined in:
   `treaties/common_framework.txt`

2. The specific bilateral agreements are located in:
   `treaties/treaty_[nation1]_[nation2].txt`

3. Overriding multilateral amendments are located in:
   `treaties/amendment_[date].txt`

4. For each item in `items_private_sample.jsonl`, you are given:
   - `id`: Unique identifier
   - `date`: The historical date of the query
   - `prompt`: The specific query describing the starting event and the target rate to calculate.

## Format of the Output

You must output a predictions JSONL file named `predictions.jsonl` where each line contains exactly:
`{"id": "...", "answer": "..."}`

The `answer` field must be:
- The exact stable rate formatted as a percentage with one decimal place (e.g. `5.2%`), OR
- If the system did not converge after 20 rounds of updates, prefix it with `STALEMATE_` and format the locked rate at round 20 rounded to 1 decimal place (e.g. `STALEMATE_3.5%`).

Always read the treaties, common framework, and active amendments up to the query date very carefully.
"""
    with open(os.path.join(solver_bundle_dir, "README.md"), "w") as f:
        f.write(readme_solver)

    # Write SOLVER_MANIFEST.json
    manifest = {
        "benchmark_name": "MFN-Cascade",
        "files": [
            "README.md",
            "items_private_sample.jsonl",
            "treaties/common_framework.txt"
        ]
    }
    for t in treaties:
        manifest["files"].append(f"treaties/treaty_{t.nation_a.lower()}_{t.nation_b.lower()}.txt")
    for a in amendments:
        manifest["files"].append(f"treaties/amendment_{a.date.replace('-', '_')}.txt")

    with open(os.path.join(solver_bundle_dir, "SOLVER_MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"Generated {len(queries)} items successfully.")

if __name__ == "__main__":
    main()
