#!/usr/bin/env python3
"""Generate private-sample items for Amendment Ledger Reconciliation (ALR)."""

from __future__ import annotations

import argparse
import json
import os
import random
from dataclasses import dataclass, field
from pathlib import Path


KINDS = ["standard", "expedited", "restoration", "archive"]
REGIONS = ["north", "south", "east", "west"]
CHANNELS = ["portal", "paper", "phone"]
FLAGS = ["safety", "heritage", "night", "bulk"]


@dataclass
class Rule:
    name: str
    priority: int
    condition: dict
    rate: int
    deadline: int
    notice: bool
    status: str = "active"
    note: str = ""


@dataclass
class State:
    definitions: dict[str, set[str]]
    rules: dict[str, Rule]
    caps: dict[str, int]
    waivers: dict[str, set[str]] = field(default_factory=dict)


def condition_text(cond: dict) -> str:
    parts = []
    if "kind" in cond:
        parts.append(f"the request class is {cond['kind']}")
    if "region" in cond:
        parts.append(f"the region is {cond['region']}")
    if "channel" in cond:
        parts.append(f"the filing channel is {cond['channel']}")
    if "flag" in cond:
        parts.append(f"the file carries the {cond['flag']} marker")
    if "tag" in cond:
        parts.append(f"the request class belongs to the defined group {cond['tag']}")
    return " and ".join(parts) if parts else "every case"


def rule_text(rule: Rule) -> str:
    status = "suspended" if rule.status != "active" else "active"
    notice = "written notice is required" if rule.notice else "written notice is not required"
    note = f" {rule.note}" if rule.note else ""
    return (
        f"{rule.name} ({status}, priority {rule.priority}): If {condition_text(rule.condition)}, "
        f"set fee_units={rule.rate}, deadline_days={rule.deadline}, and {notice}.{note}"
    )


def matches_condition(cond: dict, case: dict, definitions: dict[str, set[str]]) -> bool:
    for key, value in cond.items():
        if key == "tag":
            if case["kind"] not in definitions[value]:
                return False
        elif case.get(key) != value:
            return False
    return True


def resolve_answer(state: State, case: dict) -> str:
    candidates = [
        r
        for r in state.rules.values()
        if r.status == "active" and matches_condition(r.condition, case, state.definitions)
    ]
    if not candidates:
        raise RuntimeError("generated unsolvable item with no active matching rule")
    winner = sorted(candidates, key=lambda r: (-r.priority, r.name))[0]
    cap_key = f"{case['region']}:{case['kind']}"
    fee = min(winner.rate, state.caps.get(cap_key, 999))
    waiver_reasons = sorted(
        name
        for name, flagged in state.waivers.items()
        if case["flag"] in flagged or case["channel"] in flagged or case["kind"] in flagged
    )
    notice = winner.notice and not waiver_reasons
    waiver = "none" if not waiver_reasons else "+".join(waiver_reasons)
    return (
        f"rule={winner.name}|fee_units={fee}|deadline_days={winner.deadline}|"
        f"notice={'yes' if notice else 'no'}|waiver={waiver}"
    )


def base_state(rng: random.Random) -> State:
    definitions = {
        "fast_track": {"expedited", "restoration"},
        "ordinary": {"standard", "archive"},
    }
    rules: dict[str, Rule] = {}
    rules["R0"] = Rule("R0", 0, {}, 35, 45, True, note="This fallback applies only if no higher-priority active rule matches.")
    for idx, kind in enumerate(KINDS):
        rules[f"R{idx+1}"] = Rule(
            name=f"R{idx+1}",
            priority=10 + idx,
            condition={"kind": kind},
            rate=rng.randint(24, 58),
            deadline=rng.randint(18, 55),
            notice=bool(idx % 2),
        )
    rules["R5"] = Rule("R5", 15, {"tag": "fast_track", "channel": "portal"}, rng.randint(20, 50), rng.randint(8, 24), False)
    caps = {f"{region}:{kind}": rng.randint(28, 62) for region in REGIONS for kind in KINDS}
    return State(definitions=definitions, rules=rules, caps=caps)


def random_condition(rng: random.Random) -> dict:
    cond: dict[str, str] = {}
    choice = rng.choice(["kind", "kind_region", "tag_channel", "flag_region", "channel"])
    if choice in {"kind", "kind_region"}:
        cond["kind"] = rng.choice(KINDS)
    if choice == "kind_region":
        cond["region"] = rng.choice(REGIONS)
    if choice == "tag_channel":
        cond["tag"] = rng.choice(["fast_track", "ordinary"])
        cond["channel"] = rng.choice(CHANNELS)
    if choice == "flag_region":
        cond["flag"] = rng.choice(FLAGS)
        cond["region"] = rng.choice(REGIONS)
    if choice == "channel":
        cond["channel"] = rng.choice(CHANNELS)
    return cond


def generate_item(seed: int, index: int) -> tuple[dict, dict, dict]:
    rng = random.Random(seed * 1009 + index * 9176)
    state = base_state(rng)
    initial_state = State(
        definitions={k: set(v) for k, v in state.definitions.items()},
        rules={name: Rule(**rule.__dict__) for name, rule in state.rules.items()},
        caps=dict(state.caps),
    )
    audit = []
    amendments = []

    for step in range(1, rng.randint(8, 12)):
        op = rng.choice(["replace_rule", "add_rule", "suspend_rule", "cap", "definition", "waiver"])
        if op == "replace_rule":
            target = rng.choice(list(state.rules))
            old = state.rules[target]
            old.status = "active"
            old.rate += rng.choice([-9, -6, 5, 8, 11])
            old.deadline = max(5, old.deadline + rng.choice([-12, -7, 6, 10]))
            old.notice = rng.choice([old.notice, not old.notice])
            old.priority += rng.choice([0, 1, 3, 5])
            text = f"A{step}: Replace {target} in full with: {rule_text(old)}"
        elif op == "add_rule":
            name = f"R{max(int(r[1:]) for r in state.rules) + 1}"
            rule = Rule(
                name=name,
                priority=rng.randint(9, 24),
                condition=random_condition(rng),
                rate=rng.randint(18, 72),
                deadline=rng.randint(5, 60),
                notice=rng.choice([True, False]),
            )
            state.rules[name] = rule
            text = f"A{step}: Add rule {name}: {rule_text(rule)}"
        elif op == "suspend_rule":
            suspendable = [name for name in state.rules if name != "R0"]
            target = rng.choice(suspendable)
            state.rules[target].status = "suspended"
            text = f"A{step}: Suspend {target}. A suspended rule is ignored unless a later amendment replaces it in full."
        elif op == "cap":
            region = rng.choice(REGIONS)
            kind = rng.choice(KINDS)
            cap = rng.randint(18, 55)
            state.caps[f"{region}:{kind}"] = cap
            text = f"A{step}: For region={region} and request_class={kind}, set the fee cap to {cap} fee_units."
        elif op == "definition":
            tag = rng.choice(["fast_track", "ordinary"])
            kind = rng.choice(KINDS)
            action = rng.choice(["include", "exclude"])
            if action == "include":
                state.definitions[tag].add(kind)
                text = f"A{step}: Definition update: include {kind} in {tag}."
            else:
                state.definitions[tag].discard(kind)
                text = f"A{step}: Definition update: exclude {kind} from {tag}."
        else:
            name = f"W{len(state.waivers)+1}"
            tokens = set(rng.sample(FLAGS + CHANNELS + KINDS, k=2))
            state.waivers[name] = tokens
            text = f"A{step}: Add notice waiver {name}: notice is waived when any one of these tokens is present in the case file: {', '.join(sorted(tokens))}."
        amendments.append(text)
        audit.append({"step": step, "operation": op, "text": text})

    case = {
        "kind": rng.choice(KINDS),
        "region": rng.choice(REGIONS),
        "channel": rng.choice(CHANNELS),
        "flag": rng.choice(FLAGS),
    }
    answer = resolve_answer(state, case)
    item_id = f"alr_{seed}_{index:03d}"
    base_rules = [rule_text(initial_state.rules[name]) for name in sorted(initial_state.rules, key=lambda r: int(r[1:]))]
    base_caps = [
        f"Initial cap: region={region}, request_class={kind}, fee_cap={initial_state.caps[f'{region}:{kind}']}."
        for region in REGIONS
        for kind in KINDS
    ]
    item = {
        "id": item_id,
        "answer_format": "rule=<RULE>|fee_units=<INT>|deadline_days=<INT>|notice=<yes/no>|waiver=<none or + joined waiver ids>",
        "task": "Apply the base code and amendments in chronological order, then answer the case file exactly.",
        "decision_rules": [
            "Only active rules can win.",
            "A later replacement of a suspended rule makes the replacement active.",
            "Among matching active rules, choose the highest priority; break ties by lexicographically smaller rule id.",
            "A tag condition matches the request class if the final definition of that tag contains the request class.",
            "The final fee is the winning rule fee capped by the final region/request_class cap.",
            "Notice is no only if the winning rule says notice is not required, or if at least one final waiver matches a case token.",
        ],
        "base_code": {
            "definitions": [
                "fast_track initially contains expedited and restoration.",
                "ordinary initially contains standard and archive.",
            ],
            "rules": base_rules,
            "caps": base_caps,
        },
        "amendments": amendments,
        "case_file": case,
    }
    gold = {"id": item_id, "answer": answer}
    private_audit = {"id": item_id, "final_state": state_to_json(state), "audit": audit, "answer": answer}
    return item, gold, private_audit


def state_to_json(state: State) -> dict:
    return {
        "definitions": {k: sorted(v) for k, v in state.definitions.items()},
        "rules": {name: rule.__dict__ for name, rule in state.rules.items()},
        "caps": dict(sorted(state.caps.items())),
        "waivers": {k: sorted(v) for k, v in state.waivers.items()},
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-count", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    solver_dir = out_dir / "solver_bundle"
    solver_dir.mkdir(parents=True, exist_ok=True)

    items, gold, audits = [], [], []
    for index in range(1, args.sample_count + 1):
        item, answer, audit = generate_item(args.seed, index)
        items.append(item)
        gold.append(answer)
        audits.append(audit)

    write_jsonl(solver_dir / "items_private_sample.jsonl", items)
    write_jsonl(out_dir / "gold_private_sample.jsonl", gold)
    write_jsonl(out_dir / "private_audit_traces.jsonl", audits)

    manifest = {
        "benchmark": "Amendment Ledger Reconciliation",
        "version": "1.0",
        "item_file": "items_private_sample.jsonl",
        "sample_count": args.sample_count,
        "solver_visible_files": ["items_private_sample.jsonl", "solver_packet.md", "SOLVER_MANIFEST.json"],
        "prediction_schema": {"id": "string", "answer": "string"},
    }
    (solver_dir / "SOLVER_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
