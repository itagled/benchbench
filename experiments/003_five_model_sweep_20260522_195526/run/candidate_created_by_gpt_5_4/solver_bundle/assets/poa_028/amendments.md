# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `South` and category is `Archives`, replace the entire risk score with `2`.
- If zone is `West` and category is `Transit`, replace the running fee with `13`.
- If zone is `North` and `preclear = true`, replace the risk score with the smaller of its current value and `1`; then add fee `1`.

Additive rules:
- If seal is `Ember`, subtract fee `3` if flag `relay` is present.
- If zone is `East` and category is `Research`, add fee `1`.
- If `quantity >= 4`, add risk `2`.

Waivers:
- If `quantity <= 6` and `escort = true`, subtract fee `1`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `3`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `25`, force the final risk score to be at least `9`.
