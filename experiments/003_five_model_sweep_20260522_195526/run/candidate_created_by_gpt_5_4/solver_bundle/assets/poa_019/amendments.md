# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `South` and category is `Archives`, replace the entire risk score with `2`.
- If zone is `West` and category is `Research`, replace the running fee with `8`.
- If zone is `North` and `preclear = true`, replace the risk score with the smaller of its current value and `4`; then add fee `3`.

Additive rules:
- If seal is `Aster`, subtract fee `4` if flag `vault` is present.
- If zone is `East` and category is `Agriculture`, add fee `2`.
- If `quantity >= 5`, add risk `4`.

Waivers:
- If `quantity <= 7` and `escort = true`, subtract fee `1`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `4`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `32`, force the final risk score to be at least `8`.
