# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `East` and category is `Archives`, replace the entire risk score with `0`.
- If zone is `West` and category is `Medical`, replace the running fee with `9`.
- If zone is `South` and `preclear = true`, replace the risk score with the smaller of its current value and `1`; then add fee `1`.

Additive rules:
- If seal is `Birch`, subtract fee `4` if flag `field` is present.
- If zone is `North` and category is `Agriculture`, add fee `4`.
- If `quantity >= 8`, add risk `3`.

Waivers:
- If `quantity <= 9` and `escort = true`, subtract fee `4`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `3`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `30`, force the final risk score to be at least `8`.
