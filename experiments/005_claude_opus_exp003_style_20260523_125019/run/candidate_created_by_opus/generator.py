#!/usr/bin/env python
"""Generator for String Rewriting Distance benchmark.

Each item:
- alphabet: subset of {A,B,C,D}
- initial: starting string
- target: target string
- rules: list of (pattern, replacement) where pattern has length 2 and
  replacement has length 1 or 2

Operation: a rule (p, r) applied at position i to string s replaces s[i:i+2]
with r, producing s[:i] + r + s[i+2:]. At each step exactly one rule
application is performed (any matching position, any rule).

Answer: minimum number of rule applications to transform initial -> target,
under the explicit cap that intermediate strings never exceed
MAX_INTERMEDIATE_LEN = 12 characters. If unreachable within the search
horizon (MAX_STEPS = 25, max explored states 300000), the answer is -1
(this case is filtered out at generation time so production items always
have a finite reachable distance).
"""
import argparse
import json
import os
import random
from collections import deque

ALPHABET = ["A", "B", "C", "D"]
MAX_INTERMEDIATE_LEN = 12
MAX_STEPS = 25
MAX_STATES = 300000


def apply_rules(s, rules):
    """Yield all (new_string, rule_idx, position) reachable in one step."""
    out = []
    for ri, (pat, rep) in enumerate(rules):
        i = 0
        while True:
            j = s.find(pat, i)
            if j < 0:
                break
            new_s = s[:j] + rep + s[j + 2:]
            if len(new_s) <= MAX_INTERMEDIATE_LEN:
                out.append((new_s, ri, j))
            i = j + 1
    return out


def bfs_distance(initial, target, rules):
    """Minimum number of rule applications from initial to target.

    Returns:
      integer >= 0 if reachable within MAX_STEPS and MAX_STATES,
      -1 if proven unreachable (frontier exhausted),
      None if the search budget was exceeded (ambiguous).
    """
    if initial == target:
        return 0
    visited = {initial}
    frontier = [initial]
    for step in range(1, MAX_STEPS + 1):
        new_frontier = []
        for s in frontier:
            for new_s, _, _ in apply_rules(s, rules):
                if new_s == target:
                    return step
                if new_s not in visited:
                    visited.add(new_s)
                    new_frontier.append(new_s)
        if len(visited) > MAX_STATES:
            return None
        if not new_frontier:
            return -1
        frontier = new_frontier
    # Exhausted MAX_STEPS without reaching target
    return None


def random_string(rng, length, alphabet):
    return "".join(rng.choice(alphabet) for _ in range(length))


def gen_rule(rng, alphabet):
    pat = random_string(rng, 2, alphabet)
    # replacement length 1 (50%) or 2 (50%)
    rlen = rng.choice([1, 1, 2])
    rep = random_string(rng, rlen, alphabet)
    return [pat, rep]


def gen_item(rng):
    alphabet = ALPHABET[:]
    n_rules = rng.choice([4, 5, 5, 6])
    rules = []
    seen_pats = set()
    while len(rules) < n_rules:
        r = gen_rule(rng, alphabet)
        if r[0] in seen_pats:
            continue
        if r[0] == r[1]:  # identity-like rule, skip
            continue
        seen_pats.add(r[0])
        rules.append(r)
    init_len = rng.randint(5, 7)
    initial = random_string(rng, init_len, alphabet)
    tgt_len = rng.randint(2, 4)
    target = random_string(rng, tgt_len, alphabet)
    return initial, target, rules


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sample-count", type=int, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--out-dir", default=".")
    args = p.parse_args()

    rng = random.Random(args.seed)
    items = []
    attempts = 0
    max_attempts = 50000
    while len(items) < args.sample_count and attempts < max_attempts:
        attempts += 1
        initial, target, rules = gen_item(rng)
        d = bfs_distance(initial, target, rules)
        if d is None:
            continue
        # Filter for interesting difficulty: reachable in [3, 14] steps
        if d == -1:
            continue
        if d < 3 or d > 14:
            continue
        item_id = f"srd_{len(items):03d}"
        items.append({
            "id": item_id,
            "initial": initial,
            "target": target,
            "rules": rules,
            "answer": d,
        })

    if len(items) < args.sample_count:
        raise SystemExit(f"Only generated {len(items)} / {args.sample_count}")

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(out_dir, "solver_bundle"), exist_ok=True)

    gold_path = os.path.join(out_dir, "gold_private_sample.jsonl")
    public_path = os.path.join(out_dir, "solver_bundle", "items_private_sample.jsonl")

    with open(gold_path, "w") as fg, open(public_path, "w") as fp:
        for it in items:
            fg.write(json.dumps({"id": it["id"], "answer": it["answer"]}) + "\n")
            public = {
                "id": it["id"],
                "initial": it["initial"],
                "target": it["target"],
                "rules": it["rules"],
            }
            fp.write(json.dumps(public) + "\n")

    print(f"Wrote {len(items)} items to {gold_path} and {public_path}")
    dist = {}
    for it in items:
        dist[it["answer"]] = dist.get(it["answer"], 0) + 1
    print(f"Answer distribution: {sorted(dist.items())}")


if __name__ == "__main__":
    main()
