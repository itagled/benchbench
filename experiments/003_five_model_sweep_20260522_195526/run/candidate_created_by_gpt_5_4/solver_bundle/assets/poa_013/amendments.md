# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `West` and category is `Medical`, replace the entire risk score with `3`.
- If zone is `North` and category is `Transit`, replace the running fee with `12`.
- If zone is `South` and `preclear = true`, replace the risk score with the smaller of its current value and `1`; then add fee `2`.

Additive rules:
- If seal is `Aster`, subtract fee `2` if flag `relay` is present.
- If zone is `East` and category is `Agriculture`, add fee `5`.
- If `quantity >= 7`, add risk `4`.

Waivers:
- If `quantity <= 9` and `escort = true`, subtract fee `2`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `4`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `31`, force the final risk score to be at least `7`.
