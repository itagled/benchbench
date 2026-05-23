# Patchwork Ordinance Adjudication (POA) v1

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
