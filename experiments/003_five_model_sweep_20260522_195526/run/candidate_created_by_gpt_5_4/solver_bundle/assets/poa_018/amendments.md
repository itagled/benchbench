# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `East` and category is `Archives`, replace the entire risk score with `3`.
- If zone is `South` and category is `Agriculture`, replace the running fee with `7`.
- If zone is `West` and `preclear = true`, replace the risk score with the smaller of its current value and `2`; then add fee `1`.

Additive rules:
- If seal is `Cinder`, subtract fee `6` if flag `relay` is absent.
- If zone is `North` and category is `Research`, add fee `1`.
- If `quantity >= 6`, add risk `2`.

Waivers:
- If `quantity <= 8` and `escort = true`, subtract fee `1`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `3`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `22`, force the final risk score to be at least `5`.
