# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `South` and category is `Transit`, replace the entire risk score with `1`.
- If zone is `North` and category is `Agriculture`, replace the running fee with `14`.
- If zone is `West` and `preclear = true`, replace the risk score with the smaller of its current value and `3`; then add fee `2`.

Additive rules:
- If seal is `Cinder`, subtract fee `3` if flag `vault` is present.
- If zone is `East` and category is `Research`, add fee `3`.
- If `quantity >= 7`, add risk `4`.

Waivers:
- If `quantity <= 9` and `escort = true`, subtract fee `3`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `2`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `27`, force the final risk score to be at least `8`.
