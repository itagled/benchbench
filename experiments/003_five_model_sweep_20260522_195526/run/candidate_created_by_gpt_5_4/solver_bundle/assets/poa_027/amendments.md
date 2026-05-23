# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `East` and category is `Agriculture`, replace the entire risk score with `3`.
- If zone is `South` and category is `Medical`, replace the running fee with `13`.
- If zone is `West` and `preclear = true`, replace the risk score with the smaller of its current value and `4`; then add fee `3`.

Additive rules:
- If seal is `Ember`, subtract fee `4` if flag `relay` is absent.
- If zone is `North` and category is `Research`, add fee `1`.
- If `quantity >= 1`, add risk `3`.

Waivers:
- If `quantity <= 3` and `escort = true`, subtract fee `2`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `2`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `24`, force the final risk score to be at least `8`.
