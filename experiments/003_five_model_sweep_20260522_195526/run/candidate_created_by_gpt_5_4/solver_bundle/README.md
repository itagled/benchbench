# Solver Bundle for Patchwork Ordinance Adjudication (POA) v1

Each item is a fictional compliance packet. The answer for every item must be a single string:

`verdict=<ALLOW|REVIEW|DENY>;lane=<GREEN|AMBER|RED>;fee=<integer>`

Use:
- `shared_rules.md` for global interpretation rules,
- the per-item `charter.md`,
- the per-item `amendments.md`,
- and the per-item `case_file.json`.

The authoritative item index is `items_private_sample.jsonl`. All asset paths inside it are relative to this solver bundle.

Nothing outside this directory is needed to solve the benchmark in principle.
