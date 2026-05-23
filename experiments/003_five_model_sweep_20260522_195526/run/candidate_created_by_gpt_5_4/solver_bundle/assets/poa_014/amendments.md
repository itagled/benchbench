# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `West` and category is `Transit`, replace the entire risk score with `2`.
- If zone is `North` and category is `Archives`, replace the running fee with `8`.
- If zone is `East` and `preclear = true`, replace the risk score with the smaller of its current value and `3`; then add fee `2`.

Additive rules:
- If seal is `Aster`, subtract fee `5` if flag `relay` is present.
- If zone is `South` and category is `Medical`, add fee `5`.
- If `quantity >= 5`, add risk `3`.

Waivers:
- If `quantity <= 7` and `escort = true`, subtract fee `4`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `5`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `28`, force the final risk score to be at least `5`.
