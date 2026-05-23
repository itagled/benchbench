# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `East` and category is `Archives`, replace the entire risk score with `2`.
- If zone is `West` and category is `Transit`, replace the running fee with `14`.
- If zone is `North` and `preclear = true`, replace the risk score with the smaller of its current value and `2`; then add fee `1`.

Additive rules:
- If seal is `Birch`, subtract fee `6` if flag `relay` is present.
- If zone is `South` and category is `Research`, add fee `5`.
- If `quantity >= 3`, add risk `3`.

Waivers:
- If `quantity <= 5` and `escort = true`, subtract fee `4`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `2`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `26`, force the final risk score to be at least `7`.
