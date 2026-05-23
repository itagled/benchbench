# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `West` and category is `Medical`, replace the entire risk score with `3`.
- If zone is `East` and category is `Research`, replace the running fee with `9`.
- If zone is `North` and `preclear = true`, replace the risk score with the smaller of its current value and `3`; then add fee `1`.

Additive rules:
- If seal is `Cinder`, subtract fee `4` if flag `field` is absent.
- If zone is `South` and category is `Archives`, add fee `1`.
- If `quantity >= 8`, add risk `3`.

Waivers:
- If `quantity <= 9` and `escort = true`, subtract fee `1`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `2`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `23`, force the final risk score to be at least `7`.
